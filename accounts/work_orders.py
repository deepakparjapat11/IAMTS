import csv
import codecs
from accounts.models import WorkOrderItems
import pandas
import xlsxwriter


class add_work_order_items:
    """
    A class to save items for a WorkOrderManagement 

    ...

    Attributes
    ----------
        errors: bool
            True if there was some problem with the contents of the file and if True, no item will be saved.
        no_of_items: int
            Number of items saved for current WorkOrderManagement object 
        error_list: list
            A list of all the errors with the file object containing details of items
        items: list
            A list of valid items cached to be saved which may not be saved if self.errors is found to be True
        counter: int
            Total number of rows found for item data in the file.

    Methods
    -------
        validate_item
    """
    @property
    def errors(self):
        if len(self.error_list)>0:
            return True
        return False

    def __init__(self, file_obj, order):
        """ 
        Constructs all the necessary attributes for the add_work_order_items object.

        Parameters
        ----------
            file_obj : file object
                File object containing details of items
            order : WorkOrderManagement
                Work order for which the items are to be saved
        """
        fieldnames = ["description", "quantity", "unit_price"]
        self.no_of_items = 0
        self.error_list = []
        self.items = []
        self.counter = 0
        order.items.all().delete()
        order.tax = 0
        order.other = 0
        order.save()
        
        if file_obj.name.lower().endswith('.csv'):
            dict_reader = csv.DictReader(codecs.iterdecode(file_obj, "utf-8"))
            if dict_reader.fieldnames != fieldnames:
                self.error_list.append(
                    "Inbound data does not have expected columns.\nShould be: %s" % fieldnames)
            if not self.errors:
                for row in dict_reader:
                    if row['description'].lower().strip() == "tax":
                        try:
                            order.tax = float(row['quantity'])
                        except:
                            self.error_list.append("Invalid tax amount.")
                        continue                
                    if row['description'].lower().strip() == "other":
                        try:
                            order.other = float(row['quantity'])
                        except:
                            self.error_list.append("Invalid tax amount.")
                        continue
                    self.counter += 1 
                    if self.validate_item(row):
                        item = WorkOrderItems(
                            description=row['description'], quantity=row['quantity'], unit_price=row['unit_price'], work_order=order)
                        self.items.append(item)
        if file_obj.name.lower().endswith('.xls'):
            reader = pandas.read_excel(file_obj.read())
            if [key for key in reader.keys()] != fieldnames:
                self.error_list.append(
                    "Inbound data does not have expected columns.\nShould be: %s" % fieldnames)
            if not self.errors:
                for row in reader.itertuples():
                    if row['description'].lower().strip() == "tax":
                        try:
                            order.tax = float(row['quantity'])
                        except:
                            self.error_list.append("Invalid tax amount.")
                        continue                
                    if row['description'].lower().strip() == "other":
                        try:
                            order.other = float(row['quantity'])
                        except:
                            self.error_list.append("Invalid tax amount.")
                        continue
                    item = {
                        'description': row.description,
                        'quantity': row.quantity,
                        'unit_price': row.unit_price
                    }
                    self.counter += 1 
                    if self.validate_item(item):
                        item = WorkOrderItems(
                            description=item['description'], quantity=item['quantity'], unit_price=item['unit_price'], work_order=order)
                        self.items.append(item)

        if not self.errors:
            for item in self.items:
                item.save()
                self.no_of_items = self.no_of_items + 1
            order.save()

    def validate_item(self, item):
        """ 
        Checks if an item can be saved as WorkOrderItems.

        Parameters
        ----------
        item : dict
            A dict containing "description", "quantity", "unit_price" keys

        Returns
        -------
        bool
        """
        valid = True
        if len(item['description'].strip()) == 0:
            valid = False
            self.error_list.append("Item %d: Description can not be blank."%self.counter)
        try:
            int(item['quantity'])
        except:
            valid = False
            self.error_list.append("Item %d: Invalid quantity."%self.counter)
        try:
            float(item['unit_price'])
        except:
            valid = False
            self.error_list.append("Item %d: Invalid unit_price."%self.counter)
        return valid
