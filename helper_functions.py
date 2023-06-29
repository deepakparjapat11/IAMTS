from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from threading import Thread
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from common.notification import Common
common = Common()


class AdminPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
            'current': self.page.number
        })


class DashboardPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
            'current': self.page.number
        })


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class EmailThread(Thread):
    """sending email when register using thread"""

    def __init__(self, mail_list):
        self.mail_list = mail_list

        Thread.__init__(self)

    def run(self):
        common.send_mass_mail(self.mail_list)


def send_register_mail(mail_list):
    """
    email function for register
    :param subject:
    :param html_content:
    :param recipient_list:
    :return:
    """
    EmailThread(mail_list).start()



def send_roster_mail(mail_list):
    """
    email function for register
    :param subject:
    :param html_content:
    :param recipient_list:
    :return:
    """

    EmailThread(mail_list).start()


def send_leave_mail(mail_list):
    """
    email function for register
    :param subject:
    :param html_content:
    :param recipient_list:
    :return:
    """

    EmailThread(mail_list).start()


def check_not_admin(user):
    return False if user.is_superuser else True


def check_dashboard(user):
    return user.designation.main_dashboard


def check_bus_management(user):
    return user.designation.bus_management


def check_repair_request(user):
    return user.designation.repair_request


def check_service_request(user):
    return user.designation.service_request


def check_man_management(user):
    return user.designation.man_management


def check_work_management(user):
    return user.designation.work_management


def check_user_admin_management(user):
    return user.designation.user_admin_management
