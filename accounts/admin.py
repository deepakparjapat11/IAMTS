from django.contrib import admin
from .models import User, Company, Department, Designation, FuelType, Holiday, Manufacturer
from django.contrib.auth.models import Group
from .forms import UserModelForm

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    form = UserModelForm
    list_display = ['name', 'email', 'company', 'department', 'designation']
    list_filter = ['company', 'department', 'designation']

    def get_form(self, request, obj=None, **kwargs):
        exclude_data = ['is_superuser', 'groups', 'user_permissions', 'password', 'last_login', 'is_staff', 'contact'
                        , 'profile_picture', 'joining_date', 'driving_licence', 'id_proof', 'is_active', 'date_joined',
                        'all_buses', 'total_wo', 'bus_analytics', 'bus_calendar', 'dark_mode']
        self.exclude = exclude_data
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)
        for field in form.base_fields:
            if form.base_fields.get(field).required:
                form.base_fields.get(field).label_suffix = " *:"
        form.request = request
        return form

    def get_queryset(self, request):
        queryset = super(UserAdmin, self).get_queryset(request)
        return queryset.exclude(is_superuser=True)

    def name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)


class DesignationAdmin(admin.ModelAdmin):
    list_display = ['designation_name', 'main_dashboard', 'bus_management', 'man_management', 'work_management',
                    'repair_request', 'bus_edit', 'service_request', 'work_show', 'user_admin_management']
    list_filter = ['department']


class DepartmentAdmin(admin.ModelAdmin):
    list_filter = ['company']
    list_display = ['department_name', 'company']


class HolidayAdmin(admin.ModelAdmin):
    list_filter = ['is_public_holiday']
    list_display = ['name', 'holiday_date', 'is_public_holiday', 'description']


admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Department, DepartmentAdmin)
# admin.site.register(Roster)
admin.site.register(Designation, DesignationAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(Manufacturer)
admin.site.register(FuelType)
# admin.site.unregister(BusManagement)
# admin.site.unregister(RepairRequest)
admin.site.unregister(Group)
