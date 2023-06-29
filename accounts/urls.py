from accounts import views as account_views
from accounts import api as account_api
from django.urls import path, include, re_path
from rest_framework import routers
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

router = routers.DefaultRouter()
router.register(r'registration', account_api.RegistrationApi, basename='register')
router.register(r'password', account_api.PasswordView, basename='password')
router.register(r'bus', account_api.BusManagementApi, basename='bus')
router.register(r'list/bus', account_api.BusListingApi, basename='bus_list')
router.register(r'list/user', account_api.UserListingDashboardApi, basename='user_list')
router.register(r'repair/request', account_api.RepairRequestApi, basename='repair')
router.register(r'service/request', account_api.ServiceRequestApi, basename='service')
router.register(r'dashboard', account_api.MainDashboardBusData, basename='dashboard')
router.register(r'roster', account_api.RosterApi, basename='roster')
router.register(r'roaster/list', account_api.RosterDashboardApi, basename='roster_dashboard')
router.register(r'user', account_api.UserListingApi, basename='user')
router.register(r'leaves/uploadcsv',account_api.UploadCsvLeavesApi, 'upload_leaves')
router.register(r'list/leaves',account_api.LeaveListingApi, 'list_leaves')
router.register(r'export',account_api.ExportApi, basename='export')
router.register(r'data/leave',account_api.LeaveDataWithRangeApi, basename='leave_data')
router.register(r'holiday', account_api.HolidayView, basename='holiday')
router.register(r'bus/photo', account_api.BusPhotosApi, basename='photos')
router.register(r'work_order', account_api.WorkOrderManagementAPI, basename='work_order')
router.register(r'manufacturer', account_api.ManufacturerApi, basename='manufacturer')
router.register(r'pending/repair', account_api.PendingRepairRequestApi, basename='pending')
router.register(r'pending/service', account_api.PendingServiceRequestApi, basename='pending_service')
router.register(r'list/order', account_api.WorkOrderListAPI, basename='list_order')
router.register(r'graph/order', account_api.GraphOrderApi, basename='graph')
router.register(r'graph/service', account_api.GraphServiceApi, basename='graph')
router.register(r'dashboard/order', account_api.MainDashboardorderApi, basename='dashboard_order')
router.register(r'roles/permission', account_api.RolesAndPermissionApi, basename='roles_permission')
router.register(r'upload/image', account_api.UserEditApi, basename='upload_image')
router.register(r'bus/log', account_api.BusLogsApi, basename='bus_log')


urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('register/', account_views.register, name='register'),
    path('repair/', account_views.repair, name='repair'),
    path('', account_views.user_login, name='login'),
    path('forgot/', account_views.reset_password, name='forgot'),

    path('add/bus/', account_views.add_bus_view,
         name='add_bus'),
    path('bus/dashboard', account_views.bus_dashboard, name='bus_dashboard'),
    re_path(r'bus/(?P<pk>\d+)/$', account_views.edit_bus_view,
            name='edit_bus'),
    re_path('list/bus/$', account_views.bus_listing, name='view_buses'),
    re_path(r'bus/(?P<pk>\d+)/detail/$', account_views.bus_details_view, name='bus_details'),
    path('main/dashboard', account_views.dashboard, name='dashboard'),
    path('logout/', account_views.logout_user, name='logout'),
    path('list/repair', account_views.repair_listing_view,
         name='repair_listing'),
    re_path('repair/(?P<pk>\d+)', account_views.edit_repair, name='repair_edit'),
    re_path('detail/(?P<pk>\d+)/repair', account_views.detail_repair_view, name='detail_repair'),
    path('change_password/<slug:uidb64>/<slug:token>', account_views.change_password, name="change_password"),
    path('password/success/', TemplateView.as_view(template_name='email/password_success.html'),
         name='password_success'),
    path('add/employee', account_views.add_employee, name='add_employee'),
    re_path(r'employee/(?P<pk>\d+)/$', account_views.update_employee, name='edit_employee'),
    path('list/employee', account_views.list_employee_view,name='list_employee'),
    re_path('detail/(?P<pk>\d+)/employee', account_views.detail_employee_view, name='detail_employee'),
    re_path('detail/(?P<pk>\d+)/leave',  account_views.leave_detail_view,name='leave_detail'),
    path('leave/listing', account_views.leave_listing_view,name='leave_listing'),
    path('manpower/management', account_views.manpower_dashboard, name='manpower_dashboard'),
    path('list/roster', account_views.roster_listing, name='list_roster'),
    path('add/roster', account_views.add_roster, name='add_roster'),
    re_path(r'roster/(?P<pk>\d+)/$', account_views.edit_roster, name='edit_roster'),
    re_path(r'roster/(?P<pk>\d+)/detail/$', account_views.roster_details, name='roster_details'),
    path('add/order', account_views.add_work_order ,name='add_order'),
    re_path(r'order/(?P<pk>\d+)/$', account_views.edit_work_order ,name='edit_order'),
    re_path(r'order/(?P<pk>\d+)/detail/$', account_views.work_order_details ,name='detail_order'),
    path('list/order', account_views.order_list_view, name='list_order'),
    path('work/order', account_views.order_dashboard,name='Work_order'),
    path('service/', account_views.add_service, name='add_service'),
    path('list/service', account_views.service_list_view, name='list_service'),
    re_path(r'service/(?P<pk>\d+)',
            account_views.edit_service, name='service_edit'),
    re_path(r'detail/(?P<pk>\d+)/service', login_required(TemplateView.as_view(
        template_name='service_request/request_detail.html')), name='detail_service'),
    path('work/report', TemplateView.as_view(template_name='service_request/reports.html'), name='reports'),
    path('user/settings', account_views.settings_page,name='settings'),
    path('user/roles', account_views.roles_page, name='roles'),
    path('upload/leave', account_views.upload_leave_view, name='upload_leave'),
    path('user/accounts', account_views.mysettings_page, name='my_accounts'),
    path('role/add', account_views.add_roles, name='add_role'),
    path('user/edit', TemplateView.as_view(template_name='roles/edit_user_permissions.html'),name='edit_user_permissions'),
    path('not/found', TemplateView.as_view(template_name='notFound.html'),name='notfound'),
    path('popup', TemplateView.as_view(template_name='popup.html'),name='popup'),
    re_path(r'getSubcategory/$', account_views.get_department),
    re_path(r'getDesignation/$', account_views.get_designation)
]
