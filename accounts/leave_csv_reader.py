import codecs
import csv
import datetime
import logging
from .models import LeaveManagement, User
import  re
log = logging.getLogger(__name__)


class CSVImporter:
    """Core upsert functionality for CSV import, for re-use by `import_csv` management command, web UI and tests.
    Supplies a detailed log of what was and was not imported at the end. See README for usage notes.
    """
    def __init__(self):
        self.errors = []
        self.upserts = []
        self.summaries = []
        self.line_count = 0
        self.upsert_count = 0

    def upsert(self, fileobj, request, as_string_obj=False):
        """Expects a file *object*, not a file path. This is important because this has to work for both
        the management command and the web uploader; the web uploader will pass in in-memory file
        with no path!
        Header row is:
        Title, Group, Task List, Created Date, Due Date, Completed, Created By, Assigned To, Note, Priority
        """
        if as_string_obj:
            # fileobj comes from mgmt command
            csv_reader = csv.DictReader(fileobj)
        else:
            # fileobj comes from browser upload (in-memory)
            csv_reader = csv.DictReader(codecs.iterdecode(fileobj, "utf-8"))
        # DI check: Do we have expected header row?
        header = csv_reader.fieldnames
        expected = [
            "EmployeeId",
            "From",
            "To",
            "LeaveType",
            "Description",
            "Status"
        ]
        if header != expected:
            self.errors.append("Inbound data does not have expected columns.\nShould be: %s"% expected)
            return self.errors
        for row in csv_reader:
            self.line_count += 1
            newrow = self.validate_row(row)
            if newrow:
                # newrow at this point is fully validated, and all FK relations exist,
                # e.g. `newrow.get("Assigned To")`, is a Django User instance.
                employee = User.objects.filter(employee_id=row.get("EmployeeId"), company=request.user.company).first()
                obj, created = LeaveManagement.objects.get_or_create(
                    employee=employee,
                    from_date=newrow.get("From"),
                    to_date=newrow.get("To"),
                    company=request.user.company,
                    defaults={
                        "leave_type": newrow.get("LeaveType"),
                        "description":newrow.get("Description"),
                        "status": newrow.get("Status") if newrow.get("Status") else 'pending',
                    },
                )
                if obj:
                    obj.leave_type = newrow.get("LeaveType")
                    obj.description = newrow.get("Description")
                    if newrow.get("Status"):
                        obj.status = newrow.get("Status")
                    obj.save()
                self.upsert_count += 1
                msg = (
                    'Upserted leave of employee: %s'% (obj.employee.employee_id +' '+ obj.employee.first_name)
                )
                self.upserts.append(msg)
        self.summaries.append("Processed %s CSV rows"% self.line_count)
        self.summaries.append("Upserted %s rows"% self.upsert_count)
        self.summaries.append("Skipped %s rows"% (self.line_count - self.upsert_count))
        return {"summaries": self.summaries, "upserts": self.upserts, "errors": self.errors}

    def validate_row(self, row):
        """Perform data integrity checks and set default values. Returns a valid object for insertion, or False.
        Errors are stored for later display. Intentionally not broken up into separate validator functions because
        there are interdpendencies, such as checking for existing `creator` in one place and then using
        that creator for group membership check in others."""
        row_errors = []
        # #######################
        # Task creator must exist
        if not row.get("EmployeeId"):
            msg = "Employee Id is missing."
            row_errors.append(msg)

        employee = User.objects.filter(employee_id=row.get("EmployeeId")).first()
        if row.get('EmployeeId'):
            if not employee:
                msg = "Invalid Employee Id %s"% row.get('EmployeeId')
                row_errors.append(msg)

        if not row.get("Status"):
            status = ['pending', 'approved', 'rejected', '']
            if not row.get("Status") in status:
                msg = "Invalid status entry %s" % row.get('Status')
                row_errors.append(msg)

        # #######################
        # Validate Dates
        datefields = ["From", "To"]
        to_date = row.get(datefields[1])
        from_date = row.get(datefields[0])
        if to_date and from_date:
            to_date = self.validate_date(to_date)
            from_date = self.validate_date(from_date)
            if to_date and from_date:
                if not(to_date >= from_date):
                    msg = "To date is less the from date."
                    row_errors.append(msg)

            else:
                msg = "Enter a valid date format."
                row_errors.append(msg)
        else:
            msg = "Date is missing."
            row_errors.append(msg)
        for datefield in datefields:
            datestring = row.get(datefield)
            if datestring:
                valid_date = self.validate_date(datestring)
                if valid_date:
                    row[datefield] = valid_date
                else:
                    msg = "Enter a valid date format."
                    row_errors.append(msg)
            else:
                msg = "Date is missing."
                row_errors.append(msg)


        # #######################
        # Group membership checks have passed
        if row_errors:
            self.errors.append({self.line_count: row_errors})
            return False

        return row

    def validate_date(self, datestring):
        """Inbound date string from CSV translates to a valid python date."""
        mat = re.match('(\d{2})[/](\d{2})[/](\d{4})$', datestring)
        date_strf = "%d-%m-%Y"
        if mat is not None:
            date_strf = "%d/%m/%Y"
        elif re.match('(\d{2})[-](\d{2})[-](\d{4})$', datestring) is not None:
            date_strf = "%d-%m-%Y"
        try:
            date_obj = datetime.datetime.strptime(datestring, date_strf)
            return date_obj
        except ValueError:
            return False


class OrderImporter:

    def __init__(self):
        self.errors = []
        self.upserts = []
        self.summaries = []
        self.items = []
        self.line_count = 0
        self.upsert_count = 0

    def upsert(self, fileobj, request, as_string_obj=False):
        if as_string_obj:
            # fileobj comes from mgmt command
            csv_reader = csv.DictReader(fileobj)
        else:
            # fileobj comes from browser upload (in-memory)
            csv_reader = csv.DictReader(codecs.iterdecode(fileobj, "utf-8"))
        # DI check: Do we have expected header row?
        header = csv_reader.fieldnames
        print(header)
        expected = [
            "Product Description",
            "Product Quantity",
            "Product Unit Price",
            "Product Tax(%)",
            "Other Charges",
        ]
        if header != expected:
            print(22222222222)
            self.errors.append("Inbound data does not have expected columns.\nShould be: %s" % expected)
            print(self.errors)
            return {"errors": self.errors}
        for row in csv_reader:
            self.line_count += 1
            newrow = self.validate_row(row)
            if newrow:
                print(88888888888)
                print(newrow)
                self.items.append(newrow)


        self.summaries.append("Processed %s CSV rows" % self.line_count)
        self.summaries.append("Upserted %s rows" % self.upsert_count)
        self.summaries.append("Skipped %s rows" % (self.line_count - self.upsert_count))
        return {"summaries": self.summaries, "upserts": self.upserts, "errors": self.errors, 'items': self.items}

    def validate_row(self, row):
        print(44444444444444)
        row_errors = []
        # #######################
        # Task creator must exist
        if not row.get("Product Description"):
            print(1111111111111)
            msg = "Product Description is missing."
            row_errors.append(msg)

        if not row.get("Product Quantity"):
            msg = "Product Quantity is missing."
            row_errors.append(msg)
        else:
            print(type(row.get("Product Quantity")))
            print(type(row.get("Product Quantity")) is not int)
            check = self.convertInt(row.get("Product Quantity"))
            print(check)
            if not check:
                msg = "Product Quantity is must be a number."
                row_errors.append(msg)

        if not row.get("Product Unit Price"):
            msg = "Product Unit Price is missing."
            row_errors.append(msg)
        else:
            check = self.convertInt(row.get("Product Unit Price"))
            print(check)
            if not check:
                msg = "Product Unit Price is must be a number."
                row_errors.append(msg)

        if not row.get("Product Tax(%)"):
            msg = "Product Tax(%) is missing."
            row_errors.append(msg)
        else:
            check = self.convertInt(row.get("Product Tax(%)"))
            print(check)
            if not check:
                msg = "Product Tax(%) is must be a number."
                row_errors.append(msg)
            else:
                if int(row.get("Product Tax(%)")) > 100:
                    msg = "Product Tax % is not more than 100."
                    row_errors.append(msg)

        if not row.get("Other Charges"):
            msg = "Other Charges is missing."
            row_errors.append(msg)
        else:
            check = self.convertInt(row.get("Other Charges"))
            print(check)
            if not check:
                msg = "Other Charges is must be a number."
                row_errors.append(msg)

        if row_errors:
            self.errors.append({self.line_count: row_errors})
            return False

        return row

    def convertInt(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False