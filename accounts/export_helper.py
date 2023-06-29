import csv
import tempfile
from datetime import datetime

from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import get_template
from IAMTS import settings
# from utils import render_to_pdf
from xhtml2pdf import pisa
import xlsxwriter

try:
    import cStringIO as StringIO
except ImportError:
    from io import BytesIO, StringIO


def get_file(data, action, file_type='pdf', request=None):
    if file_type == 'pdf':
        template = get_template('export/%s.html' % action)
        print(request)
        html = template.render({'data': data, 'today': datetime.now().strftime("%d/%m/%Y %H:%M:%S").split(" ")[0],
                                'domain': request.META['HTTP_HOST'],
                                'protocol': 'https' if request.is_secure() else 'http'
                                })
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
        if not pdf.err:
            return result.getvalue()
        return None
    elif file_type == 'csv':
        output = StringIO()
        if len(data) > 0:
            writer = csv.DictWriter(output,fieldnames=data[0].keys())
            writer.writeheader()
            for element in data:
                writer.writerow(element)
        else:
            output.write("No data found")
        output.seek(0)
        response = output
        return response
    elif file_type == 'xls':
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet(action)
        bold_highlight_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'font_size': 12, 'border': 1})
        data_format = workbook.add_format({'border': 1,'align': 'center'})
        data_format.set_text_wrap()
        row = 0
        worksheet.write_row(row,0,data[0].keys(),bold_highlight_format)
        row += 1
        if len(data)>0:
            for element in data:
                worksheet.write_row(row,0,element.values(), data_format)
                row += 1
        else:
            worksheet.merge_range(row,0,row,len(data[0].keys())-1,"No data found")
        workbook.close()
        output.seek(0)
        return output
    else:
        raise Exception("Unable to export data in %s format. Available Formats are: pdf, csv and xls." % file_type)


def export_as_email(action, request, subject, export_file, file_type):

        try:
            email_from = "<%s>" % settings.EMAIL_FROM
            msg = EmailMultiAlternatives(subject, '', email_from, [request.user.email])
            context = {
                'domain': request.META['HTTP_HOST'],

                'protocol': 'https' if request.is_secure() else 'http',
            }
            html_content = get_template('export/export_email.html',).render(context
                )
            msg.attach_alternative(html_content, 'text/html')
            filename = "%s-%s_" % (action, datetime.today().date())
            msg.attach('Report%s.pdf' % filename, export_file, 'application/%s' %file_type)

            # attachment = tempfile.NamedTemporaryFile(
            #     'w+b', delete=True, dir='temp/attachments', suffix='.'+file_type, prefix=filename)
            # if file_type == 'pdf':
            #     attachment.write(export_file.content)
            # if file_type == 'xls':
            #     attachment.write(export_file.read())
            # if file_type == 'csv':
            #     attachment.write(export_file.content)
            # attachment.flush()
        # msg.attach_file(attachment.name)

            msg.send()
        except Exception as e:
            print(e)
        #attachment.close()
