from django.conf import settings
from django.core.mail import EmailMultiAlternatives
# get_template is what we need for loading up the template for parsing.
# from django.template.loader import get_template
# Templates in Django need a "Context" to parse with, so we'll borrow this.
# "Context"'s are really nothing more than a generic dict wrapped up in a
# neat little function call.
from django.template import loader
from django.core import mail
from django.contrib import admin


class Common():
    mail = mail

    def getDefaultSender(self):
        return "%s <%s>" % (admin.site.site_title, settings.EMAIL_FROM )

    def send_mass_mail(self, mail_list):
        msg_list = []
        for email in mail_list:
            email['mail_template_args']['STATIC_URL'] = settings.STATIC_URL
            mail_context = email['mail_template_args']
            try:
                template = loader.get_template('generic/' + email['mail_template'])
            except:

                template = loader.get_template(email['mail_template'])
            text_part = template.render(mail_context)
            html_part = template.render(mail_context)
            msg = EmailMultiAlternatives(
                email['mail_subject'],
                text_part,
                self.getDefaultSender(),
                email['mail_to'] if type(email['mail_to']) == list else [email['mail_to']],
            )
            msg.attach_alternative(html_part, "text/html")
            msg_list.append(msg)
        try:
            connection = mail.get_connection(
                host=settings.EMAIL_HOST,
                port=int(settings.EMAIL_PORT),
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS)
            connection.open()
            connection.send_messages(msg_list)
            connection.close()
        except Exception as e:
            print(e)
            print(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, )
