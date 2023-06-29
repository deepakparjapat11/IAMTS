from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from constants import BUS_MANUFACTUER_OPTION, BUS_STATUS_OPTION, BUS_CATEGORY_OPTION, BUS_FUEL_OPTION, LEAVE_TYPE,\
    REPAIR_STATUS_OPTION, ROSTER_CATEGORY_OPTION, ROSTER_STATUS_OPTION, LEAVE_STATUS, ORDER_STATUS
import datetime

# Create your models here.


def increment_repair_number():
    '''Set a serial number for repair request created'''
    last_repair = RepairRequest.objects.all().order_by('id').last()
    if not last_repair:
        return 'RR-001'
    new_organisation_no = 'RR-{}'.format(str(int(last_repair.id) + 1).zfill(3))
    return new_organisation_no


def increment_order_number():
    '''Set a serial number for work order created'''
    last_repair = WorkOrderManagement.objects.all().order_by('id').last()
    if not last_repair:
        return 'WO-001'
    new_organisation_no = 'WO-{}'.format(str(int(last_repair.id) + 1).zfill(3))
    return new_organisation_no


def increment_service_number():
    '''Set a serial number for service request created'''
    last_repair = ServiceRequest.objects.all().order_by('id').last()
    if not last_repair:
        return 'SR-001'
    new_organisation_no = 'SR-{}'.format(str(int(last_repair.id) + 1).zfill(3))
    return new_organisation_no


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class Company(models.Model):
    '''Company model'''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    industry = models.CharField(max_length=100)

    def __str__(self):
        return self.industry

    class Meta:
        verbose_name_plural = "companies"


class Department(models.Model):
    '''Department for particular company'''
    company = models.ForeignKey(Company, related_name='department_company', on_delete=models.CASCADE)
    department_name = models.CharField('Department name', max_length=100)

    def __str__(self):
        return self.department_name


class Designation(models.Model):
    '''Designation model'''
    company = models.ForeignKey(Company, related_name='designation_company', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name='designation_department', on_delete=models.CASCADE)
    designation_name = models.CharField('Designation name', max_length=100)
    user_admin_management = models.BooleanField('User Administration', default=False)
    main_dashboard = models.BooleanField('Main Dashboard', default=False)
    bus_management = models.BooleanField('Bus Mgt.', default=False)
    man_management = models.BooleanField('Manpower Mgt.', default=False)
    work_management = models.BooleanField('WO Mgt.', default=False)
    work_show = models.BooleanField('WO Show Privileges', default=False)
    repair_request = models.BooleanField('RR', default=False)
    bus_edit = models.BooleanField('Bus Edit Privileges', default=False)
    service_request = models.BooleanField('SR', default=False)
    email_rr = models.BooleanField('RR Email Privileges', default=False)
    reponsibilty = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.designation_name


class User(AbstractUser):
    """User model."""
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True, null=True)
    last_name = models.CharField('last name', max_length=30, blank=True, null=True)
    company = models.ForeignKey(Company, related_name='user_company', null=True, on_delete=models.CASCADE)
    contact = models.CharField('contact', max_length=30, null=True, blank=True)
    department = models.ForeignKey(Department, related_name='user_department', null=True, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, related_name='user_designation', null=True, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='user/profile_images', blank=True, null=True, max_length=500)
    joining_date = models.DateField(null=True, blank=True)
    driving_licence = models.FileField(upload_to='user/driving_licence', blank=True, null=True, max_length=500)
    id_proof = models.FileField(upload_to='user/ID_proof', blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    employee_id = models.CharField('Employee Id', max_length=30, unique=True)
    all_buses = models.BooleanField(default=True)
    total_wo = models.BooleanField(default=True)
    bus_analytics = models.BooleanField(default=True)
    bus_calendar = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class Manufacturer(models.Model):
    '''Manufacturer model'''
    name = models.CharField(max_length=100)
    enable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FuelType(models.Model):
    fuel_type = models.CharField('Fuel Type', max_length=100, unique=True)

    def __str__(self):
        return self.fuel_type


class BusManagement(models.Model):
    '''Bus Management Model'''
    company = models.ForeignKey(Company, related_name='bus_management_company', null=True, on_delete=models.CASCADE)
    bus_id = models.CharField('bus id', max_length=100, unique=True)
    manufacturer = models.ForeignKey(Manufacturer, related_name='bus_manufacturer', on_delete=models.CASCADE)
    make_year = models.CharField('make year', max_length=20, blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    chassis_number = models.CharField('chassis number', max_length=100)
    body_construction = models.CharField('body construction', max_length=100, blank=True, null=True)
    status = models.CharField('status', choices=BUS_STATUS_OPTION, max_length=100)
    schedule_service = models.DateField('Schedule Service', blank=True, null=True)
    schedule_repair = models.DateField('Schedule Repair', blank=True, null=True)
    vehicle_licensing = models.DateField('Vehicle Licensing', blank=True, null=True)
    bus_category = models.CharField('Bus Category', choices=BUS_CATEGORY_OPTION, max_length=30, blank=True, null=True)
    odo_reading = models.FloatField(default=0, blank=True, null=True)
    fuel_input = models.CharField('Fuel Input', max_length=100, null=True, choices=BUS_FUEL_OPTION)
    fuel_type = models.ForeignKey(FuelType, related_name='bus_management_fuel_type', null=True, on_delete=models.CASCADE)
    bus_price = models.CharField('Bus Price', max_length=100, blank=True, null=True)
    average_fuel_cost = models.FloatField('Avg. Monthly fuel', default=0, blank=True, null=True)
    labor_cost = models.FloatField('Labor Cost', default=0, blank=True, null=True)
    average_cost = models.FloatField('Average Cost', default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    out_of_service = models.DateTimeField(null=True, blank=True)
    back_in_service = models.DateTimeField(null=True, blank=True)

    @classmethod
    def from_db(cls, db, field_names, values):
        new = super(BusManagement, cls).from_db(db, field_names, values)
        # cache value went from the base
        new._check = values[field_names.index('status')]
        return new

    def save(self, *args, **kwargs):
        if not self._state.adding:
            if int(self.status) == 2 and int(self._check) != int(self.status):
                self.out_of_service = datetime.datetime.now()
            elif int(self.status) == 1 and int(self._check) != int(self.status):
                self.back_in_service = datetime.datetime.now()
        super(BusManagement, self).save(*args, **kwargs)


class BusPhotos(models.Model):
    '''Bus photos model save multiple images of particular bus'''
    bus_photos = models.FileField(upload_to='bus/images/', null=True, blank=True)
    bus_id = models.ForeignKey(BusManagement, related_name='bus_photos_management', null=True, on_delete=models.CASCADE)


class RepairRequest(models.Model):
    '''Repair Request model'''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    raise_date = models.DateField()
    repair_no = models.CharField(max_length=15, default=increment_repair_number)
    resolution_date = models.DateField()
    bus = models.ForeignKey(BusManagement, related_name='bus_repair_request', null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='company_repair_request', null=True, on_delete=models.CASCADE)
    description = models.TextField('Description', blank=True, null=True)
    request_status = models.CharField(max_length=100, default="1", choices=REPAIR_STATUS_OPTION)
    bus_system = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, related_name='repair_user', null=True, on_delete=models.CASCADE)
    # department = models.ForeignKey(Department, related_name='repair_department', null=True, on_delete=models.CASCADE)


class Roster(models.Model):
    '''Roster model'''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=30, )
    from_time = models.TimeField()
    to_time = models.TimeField()
    status = models.CharField(max_length=15, choices=ROSTER_STATUS_OPTION, blank=True, null=True)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    terms_and_conditions = models.FileField(
        upload_to='Roster/terms_and_conditions', blank=True, null=True)
    department = models.ForeignKey(Department, related_name='roster_department', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, blank=True)
    company = models.ForeignKey(Company, null=True, on_delete=models.CASCADE)
    roster_no = models.IntegerField(default=1)
    from_date = models.DateField()
    to_date = models.DateField()

    def __str__(self):
        return self.name


class LeaveManagement(models.Model):
    '''Leave Management model'''
    employee = models.ForeignKey(User, related_name='leave_employee', null=True, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    leave_type = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, default='pending', choices=LEAVE_STATUS)
    description = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, related_name='company_leaves', null=True, on_delete=models.CASCADE)


class BusLog(models.Model):
    '''Buslogs model'''
    bus = models.ForeignKey(BusManagement, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    log = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Holiday(models.Model):
    '''Holidays model'''
    holiday_date = models.DateField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)
    is_public_holiday = models.BooleanField(default=True)
    holiday_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    '''service request model'''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    service_no = models.CharField(max_length=15, default=increment_service_number)
    resolution_date = models.DateField()
    bus = models.ForeignKey(BusManagement, related_name='bus_service_request', null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='company_service_request', null=True, on_delete=models.CASCADE)
    description = models.TextField('Description', blank=True, null=True)
    request_status = models.CharField(max_length=100, default="1", choices=REPAIR_STATUS_OPTION)
    user = models.ForeignKey(User, related_name='service_user', null=True, on_delete=models.CASCADE)
    schedule_date = models.DateField(blank=True, null=True)
    bus_system = models.CharField(max_length=100, null=True, blank=True)


class WorkOrderManagement(models.Model):
    '''Work Order Management model'''
    work_order_no = models.CharField(max_length=15, default=increment_order_number)
    req_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_order_req_by')
    assigned_date = models.DateField(null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supervisor_description = models.TextField(blank=True, null=True)
    mechanics_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    req_type = models.CharField(max_length=10, null=True)
    procedure = models.CharField(max_length=30, null=True)
    repair_req = models.ForeignKey(RepairRequest, related_name='order_repair', null=True, blank=True, on_delete=models.CASCADE)
    service_req = models.ForeignKey(ServiceRequest, related_name='order_service', null=True, blank=True, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=100, default="2", choices=ORDER_STATUS)
    progress_at = models.DateTimeField(blank=True, null=True)
    close_at = models.DateTimeField(blank=True, null=True)
    hourly_rate = models.FloatField(default=0)
    employee_assigned = models.ForeignKey(User, related_name='order_user', null=True, on_delete=models.CASCADE)
    labor_hours = models.FloatField(default=0)
    completion_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.work_order_no


class OrderItems(models.Model):
    '''Work order items will store here'''
    description = models.CharField(max_length=30)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    tax = models.FloatField()
    other = models.FloatField()
    order = models.ForeignKey(WorkOrderManagement, on_delete=models.CASCADE, related_name="order_items")


class WorkOrderLog(models.Model):
    '''work order logs will store here'''
    order = models.ForeignKey(WorkOrderManagement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    log = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)