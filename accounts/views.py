from .forms import LoginForm, PasswordRestForm
from django.contrib import messages
from django.contrib.auth import login, authenticate

from .models import (User, Department, Designation, BusManagement, RepairRequest, Roster, LeaveManagement, Department,
                     WorkOrderManagement, ServiceRequest, FuelType)


from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
import datetime
from constants import ROSTER_CATEGORY_OPTION, ROSTER_STATUS_OPTION, BUS_STATUS_OPTION
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from helper_functions import (check_not_admin, check_dashboard, check_bus_management, check_repair_request, check_service_request,
                              check_man_management, check_work_management, check_user_admin_management)
from django.db.models import Max

# Create your views here.

def get_query_params(query_string):
    query_params = {}
    if len(query_string)>0:
        for query_param in query_string.split("&"):
            if "=" in query_param:
                query_params[query_param.split("=")[0]] = query_param.split("=")[1]
            else:
                query_params[query_param.split("=")[0]] = 1
    return query_params


def register(request):
    department = Department.objects.filter(company=request.user.company)
    designation = Designation.objects.filter(company=request.user.company)
    return render(request, 'registration/register_user.html', {'department': department, 'designation': designation})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_repair_request, login_url="admin:index")
def repair(request):
    buses = BusManagement.objects.filter(company=request.user.company)
    department = Department.objects.filter(company=request.user.company)
    query_params = get_query_params(request.environ['QUERY_STRING'])
    # if department:
    #     user = User.objects.filter(
    #         department=Department.objects.filter(department_name="technican", company=request.user.company).first())

    context = {'buses': buses, 'department': department,
               'req_by': request.user.first_name + " " + request.user.last_name}
    if "bus" in query_params:
        context['bus'] = int(query_params['bus'])
    return render(request, 'repair/add_repair_request.html', context)


def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        else:
            if request.user.designation.main_dashboard:
                return redirect('dashboard')
            elif request.user.designation.bus_management:
                return redirect('bus_dashboard')
            elif request.user.designation.repair_request:
                return redirect('repair_listing')
            elif request.user.designation.man_management:
                return redirect('manpower_dashboard')
            elif request.user.designation.work_management:
                return redirect('Work_order')
            elif request.user.designation.service_request:
                return redirect('list_service')
            elif request.user.designation.user_admin_management:
                return redirect('roles')
            else:
                return redirect('my_accounts')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                if request.POST.get('remember_me', None) and request.user.id:
                    request.session.set_expiry(86400)
                if user.is_superuser:
                    return redirect('admin:index')
                else:
                    if request.user.designation.main_dashboard:
                        return redirect('dashboard')
                    elif request.user.designation.bus_management:
                        return redirect('bus_dashboard')
                    elif request.user.designation.repair_request:
                        return redirect('repair_listing')
                    elif request.user.designation.man_management:
                        return redirect('manpower_dashboard')
                    elif request.user.designation.work_management:
                        return redirect('Work_order')
                    elif request.user.designation.service_request:
                        return redirect('list_service')
                    elif request.user.designation.user_admin_management:
                        return redirect('roles')
                    else:
                        return redirect('my_accounts')

            else:
                messages.error(request, 'Email or Password field are incorrect.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def reset_password(request):
    """
    reset user password
    :param request:
    :return:
    """
    page_title = 'Reset Password'
    host = 'https' if request.is_secure() else 'http'
    if request.method == 'POST':
        form = PasswordRestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.get('email')
            user = User.objects.filter(email=data).first()
            if user:
                if user.is_active:
                    data = {
                        'email': user.email,
                        'domain': request.META['HTTP_HOST'],
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email_from = settings.EMAIL_FROM
                    # subject_template_name = 'registration/password_reset_subject.txt'
                    # subject = loader.render_to_string(subject_template_name, data)
                    subject = "Password Reset IAMTS Account"
                    html_content = loader.get_template('registration/password_reset_email.html').render(data)
                    msg = EmailMultiAlternatives(subject, '', email_from, [user.email])
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send()
                    messages.success(request, _('Password reset link has been sent successfully.'))
                    return redirect(_('forgot'))
                else:
                    messages.error(request, _('Please verify your email address.'))
                    return redirect('forgot')
            else:
                messages.error(request, _('Please enter valid email address.'))
                return redirect('forgot')
        else:
            return HttpResponse(_('Invalid  form request found.'))
    else:
        form = PasswordRestForm()
        return render(request, 'registration/password_reset_form.html', {'form': form, 'page_title': page_title,
                                                                         'host': host})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_dashboard, login_url="/popup" )
def dashboard(request):
    return render(request, 'dashboard.html', data(request))


def logout_user(request):
    logout(request)
    return redirect("login")


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_bus_management, login_url="/popup" )
def bus_listing(request):
    buses = BusManagement.objects.filter(company=request.user.company)
    in_service = buses.filter(status=1).count()
    out_service = buses.filter(status=2).count()
    schedule_service = buses.filter(status=3).count()
    awaiting_parts = buses.filter(status=4).count()
    return render(request, 'bus_management/bus_listing.html',
                  {'buses': buses, 'in_service': in_service, 'out_service': out_service,
                   'schedule_service': schedule_service, 'awaiting_parts': awaiting_parts})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_bus_management, login_url="/popup")
def bus_dashboard(request):
    return render(request, 'bus_management/dashboard.html', data(request))


def data(request):
    start_date = datetime.datetime.now()
    end_date = start_date - datetime.timedelta(days=30)
    lt_date = start_date + relativedelta(months=-1, day=1)
    back_month = datetime.datetime(lt_date.year, (lt_date + relativedelta(months=1)).month,
                                   1) - datetime.timedelta(days=1)

    total_buses = BusManagement.objects.filter(company=request.user.company).count()
    bus_data = BusManagement.objects.filter(company=request.user.company)
    thirty_days = bus_data.filter(created_at__range=[end_date, start_date])
    last_sixty_days = BusManagement.objects.filter(created_at__date__range=[lt_date.date(), back_month.date()], company=request.user.company)
    this_month_data = bus_data.filter(created_at__date__range=[(start_date + relativedelta(day=1)).date(), start_date.date()]).count()
    thirty_days_percent = 0
    if total_buses and thirty_days:
        thirty_days_percent = (thirty_days.count() / total_buses) * 100
    this_month_percent = 0
    if total_buses and this_month_data:
        this_month_percent = (this_month_data / total_buses) * 100
    sixty_days_percent = 0
    if total_buses and last_sixty_days:
        sixty_days_percent = (last_sixty_days.count() / total_buses) * 100

    thirty_days_buses = 0
    if total_buses and thirty_days:
        thirty_days_buses = (thirty_days.count() / total_buses) * 100

    in_service = BusManagement.objects.filter(status=1, company=request.user.company)
    total_in_service = BusManagement.objects.filter(Q(Q(status=1) | Q(status=3)), company=request.user.company)
    buses_in_service = total_in_service.filter(updated_at__range=[end_date, start_date]).count()
    in_service_percent = 0

    if buses_in_service and total_in_service:
        in_service_percent = (buses_in_service / total_in_service.count()) * 100

    tot_repair_service = BusManagement.objects.filter(company=request.user.company, status__in=[2, 4])
    buses_repair_service = tot_repair_service.filter(updated_at__range=[end_date, start_date]).count()
    percent_repair_service = 0
    if tot_repair_service and buses_repair_service:
        percent_repair_service = (buses_repair_service / tot_repair_service.count()) * 100

    tot_out_service = BusManagement.objects.filter(company=request.user.company, status=2)
    active_percent = 0
    if in_service and total_buses:
        active_percent = (in_service.count() / total_buses) * 100

    out_percent = 0
    if tot_out_service and total_buses:
        out_percent = (tot_out_service.count() / total_buses) * 100

    repair_percent = 0
    if tot_repair_service and total_buses:
        repair_percent = (tot_repair_service.count() / total_buses) * 100

    tot_repair_reuest = RepairRequest.objects.filter(Q(Q(request_status=1) | Q(request_status=2)), company=request.user.company).count()
    tot_schedule_service = BusManagement.objects.filter(company=request.user.company, status=3).count()
    tot_awaiting_parts = BusManagement.objects.filter(company=request.user.company, status=4).count()
    short_service_percent = 0
    if tot_schedule_service and total_buses:
        short_service_percent = (tot_schedule_service / total_buses) * 100
    total_user = User.objects.filter(company=request.user.company)
    thirty_days_user = total_user.filter(created_at__range=[end_date, start_date]).count()
    thirty_user_per = 0
    if total_user and thirty_days_user:
        thirty_user_per = round((thirty_days_user / total_user.count()) * 100, 2)

    total_ord = WorkOrderManagement.objects.filter(company=request.user.company)
    thirty_days_ord = total_ord.filter(created_at__range=[end_date, start_date]).count()
    ord_percent = 0
    if total_ord and thirty_days_ord:
        ord_percent = round((thirty_days_ord / total_ord.count()) * 100, 2)
    total_rr = RepairRequest.objects.filter(company=request.user.company).count()
    open_service = RepairRequest.objects.filter(request_status=1, company=request.user.company).count()
    progress_service = RepairRequest.objects.filter(request_status=2, company=request.user.company).count()
    resolved_service = RepairRequest.objects.filter(request_status=3, company=request.user.company).count()
    # thirty_days_service = open_service.filter(created_at__range=[end_date, start_date]).count()
    # percent_service = 0

    # if open_service and thirty_days_service:
    #     percent_service = round((thirty_days_service / open_service.count()) * 100, 2)
    '''Queries for Service data for due soon'''
    future_date = start_date + datetime.timedelta(days=7)
    due_soon = BusManagement.objects.filter(schedule_service__range=[start_date.date(), future_date.date()], company=request.user.company)
    service_due = due_soon.count()
    for bus in due_soon:
        service_due = service_due - ServiceRequest.objects.filter(request_status=3, schedule_date=bus.schedule_service, bus=bus.id).count()

    '''Queries for Service data for Overdue'''
    bus_due = BusManagement.objects.filter(schedule_service__lt=start_date.date(), company=request.user.company)
    service_overdue = bus_due.count()
    for bus in bus_due:
        service_overdue = service_overdue - ServiceRequest.objects.filter(request_status=3, schedule_date=bus.schedule_service,
                                                                  bus=bus.id).count()
    '''Queries for licensing data for Due Soon'''
    licence_date = start_date + datetime.timedelta(days=30)
    licence_due = BusManagement.objects.filter(vehicle_licensing__range=[start_date.date(), licence_date.date()], company=request.user.company)
    count_licence_due = licence_due.count()
    '''Queries for licensing data for overdue Soon'''
    licence_overdue = BusManagement.objects.filter(vehicle_licensing__lt=start_date.date(), company=request.user.company)

    return {'total_buses': total_buses, 'thirty_days_buses': round(thirty_days_buses, 2),
            'buses_in_service': total_in_service.count(),
            'in_service_percent': round(in_service_percent, 2),
            'percent_repair_service': round(percent_repair_service, 2),
            'tot_repair_service': tot_repair_service.count(),
            'thirty_days': thirty_days.count(), 'last_sixty_days': last_sixty_days.count(),
            'thirty_days_percent': round(thirty_days_percent, 2),
            'sixty_days_percent': round(sixty_days_percent, 2), 'tot_out_service': tot_out_service.count(),
            'active_percent': round(active_percent, 2),
            'out_percent': round(out_percent, 2), 'repair_percent': round(repair_percent, 2),
            'tot_repair_reuest': tot_repair_reuest, 'tot_schedule_service': tot_schedule_service,
            'tot_awaiting_parts': tot_awaiting_parts, 'thirty_user_per': thirty_user_per,
            'total_user': total_user.count(), 'short_service_percent': round(short_service_percent, 2),
            'this_month_percent': round(this_month_percent, 2), 'this_month_data': this_month_data,
            'ord_percent': round(ord_percent, 2), 'total_ord':total_ord.count(), 'open_service': open_service,
            'service_due': service_due, 'service_overdue': service_overdue, 'progress_service': progress_service,
            'count_licence_due': count_licence_due, 'licence_overdue':licence_overdue.count(), 'total_rr': total_rr,
            'resolved_service': resolved_service, 'in_service': in_service.count()}


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_repair_request, login_url="/popup" )
def edit_repair(request, pk):
    buses = BusManagement.objects.filter(company=request.user.company)
    department = Department.objects.filter(company=request.user.company)

    return render(request, 'repair/edit_repair_request.html', {'buses': buses, 'department': department})


def change_password(request, uidb64, token):
    return render(request, 'email/change_password.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_man_management, login_url="/popup" )
def update_employee(request, pk=None):
    department = Department.objects.filter(company=request.user.company)
    designation = Designation.objects.filter(company=request.user.company)
    return render(request, 'manpower_management/edit_new_employee.html',
                  {'department': department, 'designation': designation})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_man_management, login_url="/popup" )
def add_employee(request, pk=None):
    department = Department.objects.filter(company=request.user.company)
    designation = Designation.objects.filter(company=request.user.company)
    return render(request, 'manpower_management/add_new_employee.html',
                  {'department': department, 'designation': designation})

@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_man_management, login_url="/popup" )
def manpower_dashboard(request):
    start_date = datetime.datetime.now()
    end_date = start_date - datetime.timedelta(days=30)
    lt_date = start_date + relativedelta(months=-1, day=1)
    back_month = datetime.datetime(lt_date.year, (lt_date + relativedelta(months=1)).month,
                                   1) - datetime.timedelta(days=1)
    '''user data'''
    total_user = User.objects.filter(company=request.user.company)
    thirty_days = total_user.filter(created_at__range=[end_date, start_date]).count()
    total_leaves = LeaveManagement.objects.filter(company=request.user.company, status='approved')
    this_month_leaves = total_leaves.filter((Q(from_date__lte=start_date) & Q(to_date__gte=start_date)) | (Q(to_date__gte=start_date) & Q(from_date__lte=start_date)) | (
                        Q(from_date__gte=start_date) & Q(to_date__lte=start_date))).count()
    current_day_leaves = total_leaves.filter((Q(from_date__lte=start_date) & Q(to_date__gte=start_date)) | (Q(to_date__gte=start_date) & Q(from_date__lte=start_date)) | (
                        Q(from_date__gte=start_date) & Q(to_date__lte=start_date))).count()
    present_user = total_user.count() - current_day_leaves
    user_thirty_days = 0
    if total_user and thirty_days:
        user_thirty_days = round((thirty_days / total_user.count()) * 100, 2)

    '''roster data'''

    total_roster = Roster.objects.filter(company=request.user.company)
    roster_thirty_days = total_roster.filter(created_at__range=[end_date, start_date], status=1)
    roster_this_month = total_roster.filter(created_at__date__range=[(start_date + relativedelta(day=1)).date(), start_date.date()])
    roster_last_month = total_roster.filter(created_at__date__range=[lt_date.date(), back_month.date()])

    active_roster = total_roster.filter(status=1).count()
    inactive_roster = total_roster.filter(status=2).count()

    roster_percent_days = 0
    if active_roster and roster_thirty_days:
        roster_percent_days = round((roster_thirty_days.count() / active_roster) * 100, 2)

    this_month_percent = 0
    if total_roster and roster_this_month:
        this_month_percent = round((roster_this_month.count() / total_roster.count()) * 100, 2)
    leave_percent = 0
    if total_leaves and this_month_leaves:
        leave_percent = round((this_month_leaves / total_leaves.count()) * 100, 2)
    last_month_percent = 0
    if total_roster and roster_last_month:
        last_month_percent = round((roster_last_month.count() / total_roster.count()) * 100, 2)

    act_rstr_per = 0
    if active_roster and total_roster:
        act_rstr_per = round((active_roster / total_roster.count()) * 100, 2)

    inact_rstr_per = 0
    if inactive_roster and total_roster:
        inact_rstr_per = round((inactive_roster / total_roster.count()) * 100, 2)
    return render(request, 'manpower_management/manpower_management.html',
                  {'user': total_user.count(), 'user_thirty_days': user_thirty_days,
                   'active_roster': active_roster, 'roster_percent_days': roster_percent_days,
                   'act_rstr_per': act_rstr_per, 'inact_rstr_per': inact_rstr_per,
                   'inactive_roster': inactive_roster, 'roster_this_month': roster_this_month.count(),
                   'this_month_percent': this_month_percent, 'roster_last_month': roster_last_month.count(),
                   'last_month_percent': last_month_percent, 'this_month_leaves': this_month_leaves,
                   'present_user': present_user, 'current_day_leaves': current_day_leaves,
                   'leave_percent': leave_percent})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_man_management, login_url="/popup" )
def roster_listing(request):
    objects = Roster.objects.filter(company=request.user.company)
    department = Department.objects.filter(company=request.user.company)
    return render(request, 'manpower_management/roster_listing.html', {'rosters': objects, 'departments': department})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_man_management, login_url="/popup" )
def add_roster(request):
    member_choices = User.objects.filter(company=request.user.company)
    department = Department.objects.filter(company=request.user.company)
    return render(request, 'manpower_management/add_new_roster.html',
                  {'members_choices': member_choices, 'status_choices': ROSTER_STATUS_OPTION,
                   'category_choices': department})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index" )
@user_passes_test(check_man_management, login_url="/popup" )
def roster_details(request, pk=None):
    roster = Roster.objects.get(id=pk)
    members = roster.members.all()
    check = roster.monday == True and roster.wednesday == True and roster.thursday == True and roster.friday == True  \
            and roster.tuesday == True & roster.saturday == True and roster.sunday == True
    check1 = roster.monday == False and roster.wednesday == False and roster.thursday == False and roster.friday == False \
            and roster.tuesday == False & roster.saturday == False and roster.sunday == False

    return render(request, 'manpower_management/roster_details.html', {'roster': roster, 'members': members,
                                                                       'roster_category_option': ROSTER_CATEGORY_OPTION,
                                                                       'check': check, 'check1': check1})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_man_management, login_url="/popup" )
def edit_roster(request, pk=None):
    member_choices = User.objects.filter(company=request.user.company)
    department = Department.objects.filter(company=request.user.company)
    return render(request, 'manpower_management/edit_roster.html',
                  {'members_choices': member_choices, 'status_choices': ROSTER_STATUS_OPTION,
                   'category_choices': department})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_work_management, login_url="/popup" )
def add_work_order(request):
    user = User.objects.filter(company=request.user.company)
    print(user)
    return render(request, 'work_order/add_work_order.html',
                  {'user': user})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_work_management, login_url="/popup" )
def edit_work_order(request, pk):
    if request.user.designation.work_management and not request.user.designation.work_show:
        if not WorkOrderManagement.objects.filter(id=pk).first().employee_assigned == request.user:
            return render(request, 'popup.html')
    user = User.objects.filter(company=request.user.company)
    return render(request, 'work_order/edit_work_order.html', {'user': user})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_work_management, login_url="/popup" )
def work_order_details(request, pk=None):
    if request.user.designation.work_management and not request.user.designation.work_show:
        if not WorkOrderManagement.objects.filter(id=pk).first().employee_assigned == request.user:
            return render(request, 'popup.html')
    work_order = WorkOrderManagement.objects.get(pk=pk)
    return render(request, 'work_order/detail_work_order.html',{'work_order': work_order})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_service_request, login_url="/popup" )
def add_service(request):
    buses = BusManagement.objects.filter(company=request.user.company)
    department = Department.objects.filter(department_name="technican", company=request.user.company).first()
    query_params = get_query_params(request.environ['QUERY_STRING'])
    if department:
        user = User.objects.filter(
            department=Department.objects.filter(department_name="technican", company=request.user.company).first())
    
    context = {'bus_status_options': BUS_STATUS_OPTION, 'bus_options': buses}
    if "bus" in query_params:
        context['bus'] = int(query_params['bus'])

    return render(request, 'service_request/add_request.html', context)


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_service_request, login_url="/popup" )
def edit_service(request, pk):
    buses = BusManagement.objects.filter(company=request.user.company)
    department = Department.objects.filter(department_name="technican", company=request.user.company).first()
    user = None
    if department:
        user = User.objects.filter(
            department=Department.objects.filter(department_name="technican", company=request.user.company).first())
    return render(request, 'service_request/edit_request.html', {'bus_status_options': BUS_STATUS_OPTION})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_bus_management, login_url="/popup" )
def add_bus_view(request):
    fuel_type = FuelType.objects.all()
    return render(request, 'bus_management/add_bus_management.html',{'fuel_type': fuel_type})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_bus_management, login_url="/popup" )
def edit_bus_view(request, pk=None):
    if request.user.designation.bus_edit:
        fuel_type = FuelType.objects.all()
        return render(request, 'bus_management/edit_bus.html', {'fuel_type': fuel_type})
    return render(request, 'popup.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_bus_management, login_url="/popup" )
def bus_details_view(request, pk=None):
    return render(request, 'bus_management/bus_details.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_repair_request, login_url="/popup" )
def repair_listing_view(request):
    return render(request, 'repair/repair_listing.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_repair_request, login_url="/popup" )
def detail_repair_view(request, pk=None):
    return render(request, 'repair/repair_detail.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_man_management, login_url="/popup" )
def list_employee_view(request):
    return render(request, 'manpower_management/list_employee.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_man_management, login_url="/popup" )
def detail_employee_view(request, pk=None):
    return render(request, 'manpower_management/employee_detail.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_man_management, login_url="/popup" )
def leave_detail_view(request, pk=None):
    return render(request, 'manpower_management/leave_detail.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_man_management, login_url="/popup" )
def leave_listing_view(request):
    return render(request, 'manpower_management/leave_listing.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_man_management, login_url="/popup" )
def upload_leave_view(request):
    return render(request, 'manpower_management/upload_leaves.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_work_management, login_url="/popup" )
def order_dashboard(request):
    start_date = datetime.datetime.now()
    end_date = start_date - datetime.timedelta(days=30)
    total_ord = WorkOrderManagement.objects.filter(company=request.user.company)
    total_ord_thirty = total_ord.filter(created_at__range=[end_date, start_date]).count()
    total_order_percent = 0
    if total_ord and total_ord_thirty:
        total_order_percent = round((total_ord_thirty / total_ord.count()) * 100, 2)

    active_ord = total_ord.filter(Q(Q(order_status=1) | Q(order_status=2) | Q(order_status=4)))
    thirty_days = active_ord.filter(created_at__range=[end_date, start_date]).count()
    ord_thirty_days = 0
    if active_ord and thirty_days:
        ord_thirty_days = round((thirty_days / active_ord.count()) * 100, 2)

    total_service = ServiceRequest.objects.filter(company=request.user.company)
    thirty_days_service = total_service.filter(created_at__range=[end_date, start_date]).count()
    percent_service = 0
    if total_service and thirty_days_service:
        percent_service = round((thirty_days_service / total_service.count()) * 100, 2)

    active_service = total_service.filter(Q(Q(request_status=1) | Q(request_status=2)))
    active_service_thirty = active_service.filter(created_at__range=[end_date, start_date]).count()
    active_service_percent = 0
    if active_service and active_service_thirty:
        active_service_percent = round((active_service_thirty / active_service.count()) * 100, 2)

    return render(request, 'work_order/Work_order.html', {'active_ord': active_ord.count(), 'user_thirty_days':ord_thirty_days,
                                                          'percent_service':percent_service, 'total_service':total_service.count(),
                                                          'total_ord':total_ord.count(), 'total_order_percent': total_order_percent,
                                                          'active_service': active_service.count(), 'active_service_percent':active_service_percent})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_service_request, login_url="/popup")
def service_list_view(request):
    return render(request, 'service_request/request_list.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_work_management, login_url="/popup")
def order_list_view(request):
    return render(request, 'work_order/list_work_order.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_user_admin_management, login_url="/popup" )
def add_roles(request):
    department = Department.objects.filter(company=request.user.company)
    return render(request, 'roles/add_user.html', {'department': department})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
@user_passes_test(check_user_admin_management, login_url="/popup" )
def roles_page(request):
    departments = Department.objects.filter(company=request.user.company)
    return render(request, 'roles/roles_permissions.html', {'departments':departments})


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
def settings_page(request):
    return render(request, 'settings/settings.html')


@login_required(login_url="/")
@user_passes_test(check_not_admin, login_url="admin:index")
def mysettings_page(request):
    return render(request, 'my_accounts/my_accounts.html')

import json
def get_department(request):
    id = request.GET.get('id','')
    result = list(Department.objects.filter(company_id=int(id)).values('id', 'department_name'))
    return HttpResponse(json.dumps(result), content_type="application/json")


def get_designation(request):
    id = request.GET.get('id','')
    result = list(Designation.objects.filter(department_id=int(id)).values('id', 'designation_name'))
    return HttpResponse(json.dumps(result), content_type="application/json")


def error_404_view(request, exception):
    data = {"name": "ThePythonDjango.com"}
    return render(request,'notFound.html', data)

