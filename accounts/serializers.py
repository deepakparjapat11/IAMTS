from rest_framework import serializers
from .models import (User, BusManagement, RepairRequest, BusPhotos, Company, Roster, BusLog, LeaveManagement, Holiday,
                     BusPhotos, WorkOrderManagement, Department, ServiceRequest, Manufacturer, OrderItems, WorkOrderLog,
                     Designation, FuelType)
import string
import random
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import make_password
import datetime
import pytz
from helper_functions import send_register_mail
from django.contrib import admin
from django.db.models import Q
from constants import *
from django.shortcuts import get_object_or_404


def get_random_string(length=8):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Registration Serializer
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'company', 'contact', 'department', 'designation',
                  'profile_picture', 'joining_date', 'driving_licence', 'employee_id']
        read_only_fields = ('joining_date',)

    def validate(self, attrs):
        image = attrs['driving_licence']
        profile_picture = attrs['profile_picture']
        if image:
            name = image.name.lower()
            if not (name.endswith('.png') or name.endswith('.jpg') or name.endswith('.jpeg')):
                raise serializers.ValidationError('Please select only .png, .jpg and .jpeg files.')

        if profile_picture:
            name = profile_picture.name.lower()
            if not (name.endswith('.png') or name.endswith('.jpg') or name.endswith('.jpeg')):
                raise serializers.ValidationError('Please select only .png, .jpg and .jpeg files.')
        if attrs["employee_id"]:
            if not User.objects.filter(employee_id=attrs["employee_id"]).count() < 1:
                raise serializers.ValidationError({'error': 'This Employee id is already exist.'})
        return attrs

    def create(self, *args, **kwargs):
        if User.objects.filter(email=self.validated_data['email']).count() < 1:
            password = get_random_string()
            user = User(
                email=self.validated_data['email'],
                first_name=self.validated_data.get('first_name'),
                last_name=self.validated_data.get('last_name'),
                company=self.context["request"].user.company,
                contact=self.validated_data.get('contact'),
                department=self.validated_data.get('department'),
                designation=self.validated_data.get('designation'),
                profile_picture=self.validated_data.get('profile_picture'),
                joining_date=datetime.datetime.strptime(self.context['request'].data['joining_date'], '%d/%m/%Y').strftime(
                '%Y-%m-%d'),
                driving_licence=self.validated_data.get('driving_licence'),
                employee_id=self.validated_data['employee_id']
            )
            user.set_password(password)
            user.save()
            mail_list = []
            try:
                subject = "Welcome to %s" % admin.site.site_title
                data = {
                    "mail_template_args": {
                        'email': user.email,
                        'domain': self.context["request"].META['HTTP_HOST'],
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if self.context["request"].is_secure() else 'http',

                    },
                    "mail_to": user.email,
                    "mail_template": "email/welcome_email.html",
                    "mail_subject": subject
                }
                mail_list.append(data)
                send_register_mail(mail_list)
            except Exception as e:
                print(e)
            return user
        raise serializers.ValidationError({'error': 'This email already exist.'})


class PasswordResetSerializer(serializers.ModelSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.CharField(
        max_length=100,
        style={'input_type': 'email', 'placeholder': ' email'}
    )

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if user is None:
            raise serializers.ValidationError({"error": "User does not exist."})
        elif not user.is_active:
            raise serializers.ValidationError({"error": "This account is not verified yet."
                                                        " Please verify your account first."})
        return data

    def send_email(self, by, request):
        user = User.objects.filter(email=by).first()
        if user:
            try:
                data = {
                    'email': user.email,
                    'domain': request.META['HTTP_HOST'],
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http',
                }
                email_from = "<%s>" % settings.EMAIL_FROM
                subject = "Password Reset Email"
                html_content = get_template('email/password_reset_email.html').render(data)
                msg = EmailMultiAlternatives(subject, '', email_from, [user.email])
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
            except Exception as e:
                print(e)
        return by

    class Meta:
        model = User
        fields = ('email',)


class NewPasswordSerializer(serializers.ModelSerializer):
    '''
    Set new password
    '''
    password = serializers.CharField(
        max_length=100,
        style={'input_type': 'password', 'placeholder': 'Password*'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={
            "blank": "Password cannot be empty.",
        },
    )

    class Meta:
        model = User
        fields = ('password', 'confirm_password')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'error': 'confirm password and password does not match.'})
        return data

    def change_password(self, by):
        user = User.objects.get(email=by.email)
        user.password = make_password(self.validated_data['password'])
        user.save()
        return user


class BusManagementSerializer(serializers.ModelSerializer):
    """create new bus serializer"""
    bus_photos = serializers.ImageField(required=False)
    manufacturer_name = serializers.SerializerMethodField()

    class Meta:
        model = BusManagement
        fields = ['id', 'company', 'bus_id', 'manufacturer', 'make_year', 'history', 'chassis_number','body_construction',
                  'status', 'schedule_service', 'schedule_repair', 'bus_category', 'odo_reading', 'fuel_input',
                  'bus_price', 'average_fuel_cost', 'labor_cost', 'average_cost', 'bus_photos', 'manufacturer_name',
                  'vehicle_licensing', 'fuel_type']
        read_only_fields = ('schedule_service', 'schedule_repair', 'vehicle_licensing')

    def get_manufacturer_name(self, obj):
        return obj.manufacturer.name

    def create(self, *args, **kwargs):
        bus = BusManagement(
            bus_id=self.validated_data['bus_id'],
            manufacturer=self.validated_data.get('manufacturer'),
            make_year=self.validated_data.get('make_year'),
            history=self.validated_data.get('history'),
            company=Company.objects.get(id=self.context['request'].user.company.id),
            chassis_number=self.validated_data.get('chassis_number'),
            body_construction=self.validated_data.get('body_construction'),
            status=self.validated_data.get('status'),
            bus_category=self.validated_data.get('bus_category'),
            odo_reading=self.validated_data.get('odo_reading'),
            fuel_type=get_object_or_404(FuelType, pk=self.validated_data.get('fuel_input')),
            bus_price=self.validated_data.get('bus_price'),
            average_fuel_cost=self.validated_data.get('average_fuel_cost'),
            labor_cost=self.validated_data.get('labor_cost'),
            average_cost=self.validated_data.get('average_cost'),
        )
        if self.context['schedule_service']:
            bus.schedule_service = datetime.datetime.strptime(self.context['schedule_service'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
        if self.context['schedule_repair']:
            bus.schedule_repair = datetime.datetime.strptime(self.context['schedule_repair'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
        if self.context['request'].data['vehicle_licensing']:
            bus.vehicle_licensing = datetime.datetime.strptime(self.context['request'].data['vehicle_licensing'],
                                                               '%d/%m/%Y').strftime('%Y-%m-%d')
        bus.save()
        if self.context['file']:
            for img in self.context['file']:
                bus_photos = BusPhotos.objects.create(
                    bus_photos=img,
                    bus_id=bus,
                )
                bus_photos.save()

        BusLog.objects.create(
            bus=bus,
            user=self.context['request'].user,
            log='bus Added',
            company=self.context['request'].user.company
        )
        return bus


class UpdateBusManagementSerializer(serializers.ModelSerializer):
    """Update bus serializer"""
    bus_photos = serializers.ImageField(required=False)
    bus_images = serializers.SerializerMethodField()
    manufacturer_name = serializers.SerializerMethodField()
    fuel_type = serializers.SerializerMethodField()
    fuel_type_id = serializers.SerializerMethodField()

    def get_manufacturer_name(self, obj):
        return obj.manufacturer.name

    class Meta:
        model = BusManagement
        fields = ['id', 'company', 'bus_id', 'manufacturer', 'make_year', 'history', 'chassis_number',
                  'body_construction', 'status', 'schedule_service', 'schedule_repair', 'bus_category', 'odo_reading',
                  'fuel_input', 'bus_price', 'average_fuel_cost', 'labor_cost', 'average_cost', 'bus_photos',
                  'bus_images', 'manufacturer_name', 'vehicle_licensing', 'bus_id', 'fuel_type', 'fuel_type_id']
        read_only_fields = ('schedule_service', 'schedule_repair', 'vehicle_licensing', 'fuel_type', 'fuel_type_id')

    def get_fuel_type_id(self, obj):
        return obj.fuel_type.id if obj.fuel_type else None

    def get_fuel_type(self, obj):
        return (obj.fuel_type.fuel_type).capitalize() if obj.fuel_type else None

    def get_bus_images(self, obj):
        imges = BusPhotos.objects.filter(bus_id=obj).all()
        photo = []
        if imges is not None:
            for img in imges:
                photo.append({'id':img.id, 'image':img.bus_photos.name})
        return photo

    def update(self, instance, validated_data):
        instance.bus_id = self.validated_data.get('bus_id')
        instance.manufacturer = self.validated_data.get('manufacturer')
        instance.make_year = self.validated_data.get('make_year')
        instance.history = self.validated_data.get('history')
        instance.chassis_number = self.validated_data.get('chassis_number')
        instance.body_construction = self.validated_data.get('body_construction')
        instance.status = self.validated_data.get('status')
        if self.context['schedule_service']:
            instance.schedule_service = datetime.datetime.strptime(self.context['schedule_service'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
        if self.context['schedule_repair']:
            instance.schedule_repair = datetime.datetime.strptime(self.context['schedule_repair'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
        if self.context['request'].data['vehicle_licensing']:
            instance.vehicle_licensing = datetime.datetime.strptime(self.context['request'].data['vehicle_licensing'],
                                                               '%d/%m/%Y').strftime('%Y-%m-%d')
        instance.bus_category = self.validated_data.get('bus_category')
        instance.odo_reading = self.validated_data.get('odo_reading')
        instance.fuel_type = get_object_or_404(FuelType, pk=self.validated_data.get('fuel_input'))
        instance.bus_price = self.validated_data.get('bus_price')
        instance.average_fuel_cost = self.validated_data.get('average_fuel_cost')
        instance.labor_cost = self.validated_data.get('labor_cost')
        instance.average_cost = self.validated_data.get('average_cost')

        instance.save()
        if self.context['file']:
            for img in self.context['file']:
                bus_photos = BusPhotos.objects.create(
                    bus_photos=img,
                    bus_id=instance,
                )
                bus_photos.save()
        BusLog.objects.create(
            bus=instance,
            user=self.context['request'].user,
            log='bus updated',
            company=self.context['request'].user.company
        )
        return instance


class LsitBusManagementSerializer(serializers.ModelSerializer):
    """Listing of buses serializer"""
    bus_photos = serializers.SerializerMethodField()
    schedule_service = serializers.SerializerMethodField()
    schedule_repair = serializers.SerializerMethodField()
    last_modified = serializers.SerializerMethodField()
    manufacturer_name = serializers.SerializerMethodField()

    def get_manufacturer_name(self, obj):
        return obj.manufacturer.name

    class Meta:
        model = BusManagement
        fields = ['id', 'company', 'bus_id', 'manufacturer', 'make_year', 'history', 'chassis_number',
                  'body_construction',
                  'status', 'schedule_service', 'schedule_repair', 'bus_category', 'odo_reading', 'fuel_input',
                  'bus_price', 'average_fuel_cost', 'labor_cost', 'bus_photos', 'average_cost', 'last_modified',
                  'manufacturer_name']

    def get_bus_photos(self, obj):
        imges = BusPhotos.objects.filter(bus_id=obj).all()
        photo = []
        if imges is not None:
            for img in imges:
                photo.append(img.bus_photos.name)
        return photo

    def get_schedule_service(self, obj):
        d = None
        if obj.schedule_service:
            date = str(obj.schedule_service)
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d

    def get_schedule_repair(self, obj):
        d = None
        if obj.schedule_repair:
            date = str(obj.schedule_repair)
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d

    def get_last_modified(self, obj):
        last_modified = {}
        if obj:
            if not last_modified:
                buses = BusLog.objects.filter(company=obj.company).order_by('-created_at').first()
                if buses:
                    client_timezone = pytz.timezone('Atlantic/Bermuda')
                    lt_date = buses.created_at.astimezone(client_timezone)
                    last_modified = {'user': '%s %s' % (buses.user.first_name, buses.user.last_name),
                                     'date': lt_date.strftime('%d-%b-%y'),
                                     'time': lt_date.strftime('%l:%M%p')}
        return last_modified


class BusLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_user(self, obj):
        return '%s %s' % (obj.user.first_name, obj.user.last_name)


    def get_created_at(self, obj):
        data_time = {}
        client_timezone = pytz.timezone('Atlantic/Bermuda')
        lt_date = obj.created_at.astimezone(client_timezone)
        data_time = {'date': lt_date.strftime('%d-%b-%y'), 'time': lt_date.strftime('%l:%M%p')}
        return data_time

    class Meta:
        model = BusLog
        fields = '__all__'


class RepairRequestSerializer(serializers.ModelSerializer):
    """Create new Repair request serializer"""
    bus_status = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = RepairRequest
        fields = ['id', 'resolution_date', 'bus', 'description', 'request_status', 'created_at', 'bus_status',
                  'repair_no', 'bus_system']
        read_only_fields = ('resolution_date',)

    def get_bus_status(self, obj):
        return obj.bus.status

    def get_created_at(self, obj):
        return obj.created_at.date()

    def create(self, *args, **kwargs):
        repair = RepairRequest(
            bus=self.validated_data['bus'],
            description=self.validated_data['description'],
            bus_system=self.validated_data['bus_system'],
            company=self.context['request'].user.company,
            user=self.context['request'].user,
            raise_date=datetime.datetime.today().date(),
        )
        if self.context['resolution_date']:
            repair.resolution_date = datetime.datetime.strptime(self.context['resolution_date'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
        repair.save()
        bus = BusManagement.objects.filter(id=self.validated_data['bus'].id).first()
        bus.status = 2
        if 'bus_status' in self.context['request'].data:
            bus.status = self.context['request'].data['bus_status']
        bus.save()
        BusLog.objects.create(bus=bus, user=self.context['request'].user,
                              log='repair request raised', company=self.context['request'].user.company)
        designation = Designation.objects.filter(email_rr=True).first()
        users = None
        if designation:
            users = User.objects.filter(designation=designation, company=self.context['request'].user.company)
        if users:
            mail_list = []
            for user in users:
                try:
                    subject = "A new Repair Request is created"
                    data = {
                        "mail_template_args": {
                            'domain': self.context["request"].META['HTTP_HOST'],
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'user': user,
                            'repair': repair,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'https' if self.context["request"].is_secure() else 'http',
                        },
                        "mail_to": user.email,
                        "mail_template": "email/repair_request.html",
                        "mail_subject": subject
                    }
                    mail_list.append(data)
                except Exception as e:
                    print(e)
            send_register_mail(mail_list)
        return repair


class UpdateRepairRequestSerializer(serializers.ModelSerializer):
    """Update Repair Request Serializer"""
    bus_id = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = RepairRequest
        fields = ['id', 'resolution_date', 'user_name', 'user', 'bus', 'description', 'created_at', 'bus_status',
                  'request_status', 'bus_id', 'repair_no', 'bus_system']
        read_only_fields = ('resolution_date',)

    def get_bus_id(self, obj):
        return obj.bus.bus_id

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.first_name + ' ' + obj.user.last_name
        return None

    def get_bus_status(self, obj):
        return obj.bus.status

    def get_created_at(self, obj):
        return obj.created_at.date()

    def update(self, instance):
        obj = RepairRequest.objects.filter(id=instance).first()
        if obj:
            obj.description = self.validated_data.get('description')
            obj.bus_system = self.validated_data.get('bus_system')

        if self.context['resolution_date']:
            obj.resolution_date = datetime.datetime.strptime(self.context['resolution_date'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
        obj.save()
        bus_status = BusManagement.objects.filter(id=obj.bus.id).first()
        bus_status.status = self.context['request'].data['bus_status']
        bus_status.save()
        BusLog.objects.create(bus=bus_status, user=self.context['request'].user, log='repair request updated',
                              company=self.context['request'].user.company)
        return obj


class ListRepairSerializer(serializers.ModelSerializer):
    """Listing serilzer of repair request"""
    bus_id = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    resolution_date = serializers.SerializerMethodField()

    class Meta:
        model = RepairRequest
        fields = ['id', 'resolution_date', 'user_name', 'user', 'bus', 'description', 'created_at', 'bus_status',
                  'request_status', 'bus_id', 'raise_date', 'repair_no']

    def get_bus_id(self, obj):
        return obj.bus.bus_id

    def get_bus_status(self, obj):
        return obj.bus.status

    def get_created_at(self, obj):
        date = str(obj.created_at.date())
        d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.first_name + ' ' + obj.user.last_name
        return None

    def get_resolution_date(self, obj):
        date = str(obj.resolution_date)
        d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d


class UpdateEmployeeSerializer(serializers.ModelSerializer):
    """Update user serializer"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'contact', 'department', 'designation', 'profile_picture',
                  'joining_date', 'driving_licence', 'employee_id']
        read_only_fields = ('email', 'employee_id', 'joining_date')

    def validate(self, attrs):
        image = attrs['driving_licence']
        if image:
            name = image.name.lower()
            if not (name.endswith('.png') or name.endswith('.jpg') or name.endswith('.jpeg')):
                raise serializers.ValidationError('Please select only .png, .jpg and .jpeg files.')
        profile_picture = attrs['profile_picture']
        if profile_picture:
            name = profile_picture.name.lower()
            if not (name.endswith('.png') or name.endswith('.jpg') or name.endswith('.jpeg')):
                raise serializers.ValidationError('Please select only .png, .jpg and .jpeg files.')
        return attrs

    def update(self, pk):
        user = User.objects.filter(id=pk).first()
        if user:
            user.first_name = self.validated_data['first_name']
            user.last_name = self.validated_data['last_name']
            user.contact = self.validated_data.get('contact')
            user.department = self.validated_data['department']
            user.designation = self.validated_data['designation']
            user.joining_date = datetime.datetime.strptime(self.context['request'].data['joining_date'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
            user.save()
        if self.validated_data.get('profile_picture'):
            user.profile_picture = self.validated_data.get('profile_picture')
        if self.validated_data.get('driving_licence'):
            user.driving_licence = self.validated_data.get('driving_licence')
        user.save()
        return user


class RepairRequestExportSerializer(serializers.ModelSerializer):
    """Export functionality for repair request"""
    bus_id = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    resolution_date = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()

    class Meta:
        model = RepairRequest
        fields = ['repair_no', 'created_at', 'resolution_date', 'bus_id', 'description', 'request_status', 'bus_status']

    def get_bus_id(self, obj):
        return obj.bus.bus_id
    
    def get_bus_status(self, obj):
        if obj.bus.status == BUS_STATUS_OPTION[0][0]:
            return 'In Service'
        if obj.bus.status == BUS_STATUS_OPTION[1][0]:
            return 'Out Of Service'
        if obj.bus.status == BUS_STATUS_OPTION[2][0]:
            return 'Scheduled Service'
        if obj.bus.status == BUS_STATUS_OPTION[3][0]:
            return 'Awaiting for parts'

    def get_created_at(self, obj):
        d = None
        if obj.created_at:
            date = str(obj.created_at).split(" ")[0]
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d
    
    def get_request_status(self, obj):
        if obj.request_status == REPAIR_STATUS_OPTION[0][0]:
            return 'Pending'
        if obj.request_status == REPAIR_STATUS_OPTION[1][0]:
            return 'In progress'
        if obj.request_status == REPAIR_STATUS_OPTION[2][0]:
            return 'Resolved'

    def get_resolution_date(self, obj):
        d = None
        if obj.resolution_date:
            date = str(obj.resolution_date).split(" ")[0]
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d


class RosterSerializer(serializers.ModelSerializer):
    """Create serializer for roster"""
    doc_name = serializers.SerializerMethodField()
    members_detail = serializers.SerializerMethodField()

    def get_members_detail(self, obj):
        a = []
        for emp in obj.members.all():
            d = dict(id="", name="", picture="")
            d['id'] = emp.id
            d['name'] = emp.first_name+' '+emp.last_name
            if emp.profile_picture:
                d['picture'] = emp.profile_picture.url
            a.append(d)
        return a

    def get_doc_name(self, obj):
        file_name = None
        if obj.terms_and_conditions:
            file_name = obj.terms_and_conditions.name.split('/')[2]
        return file_name

    class Meta:
        model = Roster
        fields = ["id", "name", "company", "from_time", "to_time", "status", "monday", "tuesday", "wednesday",
                  "thursday", "friday", "saturday", "sunday", "terms_and_conditions", "department", "members",
                  "roster_no", "from_date", "to_date", 'doc_name', 'members_detail']
        read_only_fields = ('from_date', 'to_date')


class UpdateRosterSerializer(serializers.ModelSerializer):
    """Update Roster serializer"""
    class Meta:
        model = Roster
        fields = ["id", "name", "company", "from_time", "to_time", "status", "monday", "tuesday", "wednesday",
                  "thursday", "friday", "saturday", "sunday", "terms_and_conditions", "department", "members",
                  "roster_no", "from_date", "to_date"]
        read_only_fields = ('name', 'from_date', 'to_date')

    def update(self, pk):
        roster = Roster.objects.filter(id=pk).first()
        if (self.validated_data['roster_no'] != roster.roster_no):
            check = Roster.objects.filter(roster_no=self.validated_data['roster_no'], department=self.validated_data['department'])
            if check:
                raise serializers.ValidationError('Roster already exists with this Roster number.')

        users = []
        if roster:
            roster.from_time = self.validated_data['from_time']
            roster.to_time = self.validated_data['to_time']
            roster.roster_no = self.validated_data['roster_no']
            from_date = datetime.datetime.strptime(self.context['request'].data['from_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            to_date = datetime.datetime.strptime(self.context['request'].data['to_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            roster.from_date = from_date
            roster.to_date = to_date
            roster.status = self.validated_data.get('status')
            roster.monday = self.validated_data.get('monday')
            roster.tuesday = self.validated_data.get('tuesday')
            roster.wednesday = self.validated_data.get('wednesday')
            roster.thursday = self.validated_data.get('thursday')
            roster.friday = self.validated_data.get('friday')
            roster.saturday = self.validated_data.get('saturday')
            roster.sunday = self.validated_data.get('sunday')
            roster.department = self.validated_data['department']

            roster.save()
            if self.validated_data['members']:
                if not roster.members.all():
                    users.extend(self.validated_data['members'])
                else:
                    for user in self.validated_data['members']:
                        if user not in roster.members.all():
                            users.append(user)

            if users:
                mail_list = []
                for user in users:
                    subject = "You have been added to New Roster"
                    data = {
                        "mail_template_args": {
                            'name': '%s %s' %(user.first_name, user.last_name),
                            'domain': self.context["request"].META['HTTP_HOST'],
                            'roster': roster,
                            'protocol': 'https' if self.context["request"].is_secure() else 'http',

                        },
                        "mail_to": user.email,
                        "mail_template": "email/roster.html",
                        "mail_subject": subject

                    }
                    mail_list.append(data)

                    # msg.send()

                send_register_mail(mail_list)
            roster.members.set(self.validated_data['members'])
        if self.validated_data.get('terms_and_conditions'):
            roster.terms_and_conditions = self.validated_data.get('terms_and_conditions')
        roster.save()
        return roster


class RosterExportSerializer(serializers.ModelSerializer):
    """Export functionality for roster"""
    members = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    week_offs = serializers.SerializerMethodField()
    no_of_members = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Roster
        fields = ["name", "status", "department", "roster_no", "date", "time", "week_offs", "no_of_members", "members",
                  "from_date", "to_date"]

    def get_no_of_members(self, obj):
        return len(obj.members.all())

    def get_members(self, obj):
        return obj.members.all()

    def get_department(self, obj):
        return obj.department.department_name.capitalize()
    
    def get_status(self, obj):
        if obj.status == ROSTER_STATUS_OPTION[0][0]:
            return "Active"
        else:
            return "Inactive"
    
    def get_week_offs(self, obj):
        s = []
        if not obj.monday:
            s.append('Mon')
        if not obj.tuesday:
            s.append('Tue')
        if not obj.wednesday:
            s.append('Wed')
        if not obj.thursday:
            s.append('Thu')
        if not obj.friday:
            s.append('Fri')
        if not obj.saturday:
            s.append('Sat')
        if not obj.sunday:
            s.append('Sun')
        if len(s) > 0:
            return ", ".join(s)
        else:
            return "NA"
    
    def get_time(self, obj):
        return str(obj.from_time) + " to " + str(obj.to_time)
    
    def get_date(self, obj):
        return str(obj.from_date) + " to " + str(obj.to_date)


class RosterListingSerializer(serializers.ModelSerializer):
    """Roster listing serializer"""
    dept_name = serializers.SerializerMethodField()

    class Meta:
        model = Roster
        fields = ["id", "name", "company", "from_time", "to_time", "status", "monday", "tuesday", "wednesday",
                  "thursday", "friday", "saturday", "sunday", "terms_and_conditions", "department", "members",
                  "roster_no", 'dept_name',
                  "from_date", "to_date"]

    def get_dept_name(self, obj):
        return obj.department.department_name


class EmployeeListingSerializer(serializers.ModelSerializer):
    """Employee listing serilizer"""
    joining_date = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'company', 'contact', 'department', 'designation',
                  'profile_picture', 'joining_date', 'driving_licence', 'employee_id', 'is_active']

    def get_joining_date(self, obj):
        d = None
        if obj.joining_date:
            date = str(obj.joining_date)
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d

    def get_department(self, obj):
        d = None
        if obj.department:
            d = obj.department.department_name
        return d

    def get_designation(self, obj):
        d = None
        if obj.designation:
            d = obj.designation.designation_name
        return d


class LeavesApplicationsSerializer(serializers.Serializer):
    """leave upload serializer through file"""
    file = serializers.FileField()


class LeaveListingSerializer(serializers.ModelSerializer):
    """Leave listing serializer"""
    employee_id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    from_date = serializers.SerializerMethodField()
    to_date = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = LeaveManagement
        fields = ['id', 'department', 'designation', 'contact', 'employee_id', 'name', 'email', 'from_date', 'to_date',
                  'leave_type', 'status', 'description', 'profile_pic']

    def get_employee_id(self, obj):
        return obj.employee.employee_id

    def get_email(self, obj):
        return obj.employee.email

    def get_name(self, obj):
        return obj.employee.first_name + ' ' + obj.employee.last_name

    def get_contact(self, obj):
        return obj.employee.contact

    def get_department(self, obj):
        return obj.employee.department.department_name

    def get_designation(self, obj):
        return obj.employee.designation.designation_name

    def get_profile_pic(self, obj):
        if obj.employee.profile_picture:
            return obj.employee.profile_picture.url
        else:
            return ""

    def get_from_date(self, obj):
        d = None
        if obj.from_date:
            date = str(obj.from_date)
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
        return d

    def get_to_date(self, obj):
        d = None
        if obj.to_date:
            date = str(obj.to_date)
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
        return d


class ChangeLeaveStatusSerializer(serializers.ModelSerializer):
    """approve and dissapprove serializer"""
    class Meta:
        model = LeaveManagement
        fields = ['status', 'comments']

    def update(self, pk, request):
        leave = LeaveManagement.objects.filter(id=pk).first()
        if leave:
            leave.status = self.validated_data['status']
            if self.validated_data['status'] != "approved":
                leave.comments = self.validated_data.get('comments')
            leave.save()
            mail_list = []
            subject = "Your leave has been %s" % (self.validated_data['status'].capitalize())
            data = {
                "mail_template_args": {
                    'name': '%s %s' % (leave.employee.first_name, leave.employee.last_name),
                    'status': self.validated_data['status'].capitalize(),
                    'start': leave.from_date,
                    'end': leave.to_date,
                    'leave_type': leave.leave_type,
                    'comments': self.validated_data.get('comments'),
                    'domain': request.META['HTTP_HOST'],
                    'protocol': 'https' if request.is_secure() else 'http',
                },
                "mail_to": leave.employee.email,
                "mail_template": "email/leave_status.html",
                "mail_subject": subject

            }
            mail_list.append(data)
            send_register_mail(mail_list)
        return leave


class EmployeeListingExportSerializer(serializers.ModelSerializer):
    """Export functionality of employee serializer"""
    joining_date = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'company', 'contact', 'department', 'designation',
                  'joining_date', 'employee_id', 'is_active', 'driving_licence', 'id_proof']

    def get_company(self, obj):
        return obj.company.industry

    def get_name(self, obj):
        return obj.first_name + " " + obj.last_name

    def get_joining_date(self, obj):
        d = None
        if obj.joining_date:
            date = str(obj.joining_date)
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d

    def get_department(self, obj):
        d = None
        if obj.department:
            d = obj.department.department_name
        return d

    def get_designation(self, obj):
        d = None
        if obj.designation:
            d = obj.designation.designation_name
        return d


class BusexportSerializer(serializers.ModelSerializer):
    """Bus Export functionality serializer"""
    class Meta:
        model = BusManagement
        fields = ['bus_id', 'manufacturer', 'make_year', 'chassis_number', 'body_construction', 'status', 'bus_category',
                  'fuel_type', 'schedule_service']


class LeavesExportSerializer(serializers.ModelSerializer):
    """Leave Export functionality serializer"""
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    employee_email = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = LeaveManagement
        fields = ['employee_name', 'employee_id', 'employee_email', 'description', 'date', 'status']

    def get_employee_name(self, obj):
        return "%s %s" % (obj.employee.first_name, obj.employee.last_name)

    def get_employee_id(self, obj):
        return obj.employee.employee_id

    def get_employee_email(self, obj):
        return obj.employee.email

    def get_date(self, obj):
        return datetime.datetime.strptime(str(obj.from_date), '%Y-%m-%d').strftime('%m/%d/%y') + " to " + datetime.datetime.strptime(str(obj.to_date), '%Y-%m-%d').strftime('%m/%d/%y')


class LeaveDataWithRangeSerializer(serializers.ModelSerializer):
    """Serach employee absent between two date functionality serializer"""
    class Meta:
        model = LeaveManagement
        fields = ['employee']


class HolidaySerializer(serializers.ModelSerializer):
    """Public holidays fill automatically in the database every year functionality serializer"""
    class Meta:
        model = Holiday
        fields = '__all__'


class BusPhotosSerializer(serializers.ModelSerializer):
    """Listing of bus photos"""
    class Meta:
        model = BusPhotos
        fields = '__all__'


class WorkOrderItemsSerializer(serializers.ModelSerializer):
    """Work order items serializer"""
    class Meta:
        model = OrderItems
        fields = ['description', 'quantity', 'unit_price']


class WorkOrderManagementSerializer(serializers.ModelSerializer):
    """Work order listing serializer"""
    req_no = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    order_log = serializers.SerializerMethodField()
    bus = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderManagement
        fields = ['work_order_no', 'assigned_date', 'supervisor_description', 'req_type', 'req_no', 'items',
                  'order_status', 'order_log', 'bus', 'procedure', 'employee_assigned', 'hourly_rate',
                  'completion_date', 'labor_hours', 'mechanics_description']

    def get_bus(self, obj):
        bus = dict(bus_id='', status='', bus_system='')
        if obj.repair_req:
            bus['bus_id'] = obj.repair_req.bus.bus_id
            bus['status'] = obj.repair_req.bus.status
            bus['bus_system'] = obj.repair_req.bus_system
        if obj.service_req:
            bus['bus_id'] = obj.service_req.bus.bus_id
            bus['status'] = obj.service_req.bus.status
            bus['bus_system'] = obj.service_req.bus_system
        return bus

    def get_order_log(self, obj):
        logs = WorkOrderLog.objects.filter(order=obj)
        order_log = []
        if logs:
            for log in logs:
                order_log.append({'id': log.order.id, 'user': log.user.first_name +' '+ log.user.last_name, 'log':log.log, 'date':datetime.datetime.strptime(str(log.created_at.date()), '%Y-%m-%d').strftime('%d/%m/%y')})
        return order_log

    def get_req_no(self, obj):
        r = None
        if obj.repair_req:
            r = obj.repair_req.repair_no
        if obj.service_req:
            r = obj.service_req.service_no
        return r

    def get_items(self, obj):
        items = []
        order = OrderItems.objects.filter(order=obj)
        if order:
            for ord in order:
                items.append({'description': ord.description, 'quantity': ord.quantity, 'unit_price': ord.unit_price,
                              'tax': ord.tax, 'other': ord.other})
        return items


class WorkOrderCreateSerializer(serializers.ModelSerializer):
    """Work order create serializer"""
    req_no = serializers.CharField(max_length=20, write_only=True)
    bus_status = serializers.CharField(write_only=True, allow_null=True)
    bus_system = serializers.CharField(write_only=True, allow_null=True)

    class Meta:
        model = WorkOrderManagement
        fields = ['work_order_no', 'req_type', 'assigned_date', 'repair_req', 'service_req', 'supervisor_description',
                  'req_no', 'procedure', 'bus_system', 'employee_assigned', 'hourly_rate', 'bus_status', 'procedure']
        read_only_fields = ('date',)

    def create(self, *args, **kwargs):
        results = None
        work_order = WorkOrderManagement(
            req_by=self.context['request'].user,
            assigned_date=datetime.datetime.today().date(),
            company=self.context['request'].user.company,
            req_type=self.validated_data['req_type'],
            supervisor_description=self.validated_data['supervisor_description'],
            employee_assigned=self.validated_data['employee_assigned'],
            procedure=self.validated_data['procedure'],
            hourly_rate=self.validated_data['hourly_rate']
        )
        if self.validated_data['req_type'] == REPAIR_REQ_TYPE:
            repair = RepairRequest.objects.filter(id=self.validated_data['req_no']).first()
            repair.request_status = REPAIR_STATUS_OPTION[1][0]
            repair.bus_system = self.validated_data['bus_system']
            repair.save()
            bus = BusManagement.objects.filter(id=repair.bus.id).first()
            bus.status = self.validated_data['bus_status']
            bus.save()
            BusLog.objects.create(bus=bus, user=self.context['request'].user,
                                  log='Work Order raised', company=self.context['request'].user.company)
            work_order.repair_req = repair

        if self.validated_data['req_type'] == SERVICE_REQ_TYPE:
            service = ServiceRequest.objects.filter(id=self.validated_data['req_no']).first()
            bus = BusManagement.objects.filter(id=service.bus.id).first()
            bus.status = self.validated_data['bus_status']
            bus.save()
            BusLog.objects.create(bus=bus, user=self.context['request'].user,
                                  log='Work Order raised', company=self.context['request'].user.company)
            service.request_status = REPAIR_STATUS_OPTION[1][0]
            service.bus_system = self.validated_data['bus_system']
            service.save()

            work_order.service_req = service
        work_order.save()
        WorkOrderLog.objects.create(order=work_order, user=self.context['request'].user,
                              log='Work order is Created.', company=self.context['request'].user.company)

        if self.validated_data['employee_assigned']:
            user = self.validated_data['employee_assigned']
            mail_list = []
            try:
                subject = "A new work order request is created"
                data = {
                    "mail_template_args": {
                        'domain': self.context["request"].META['HTTP_HOST'],
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'order': work_order.work_order_no,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if self.context["request"].is_secure() else 'http',

                    },
                    "mail_to": user.email,
                    "mail_template": "email/workorder_email.html",
                    "mail_subject": subject
                }
                mail_list.append(data)
                send_register_mail(mail_list)
            except Exception as e:
                print(e)
        return work_order


class WorkOrderUpdateSerializer(serializers.ModelSerializer):
    """work order update serialzer"""
    req_no = serializers.CharField(max_length=20, read_only=True)
    bus_status = serializers.CharField(write_only=True, allow_null=True)
    bus_system = serializers.CharField(write_only=True, allow_null=True)

    class Meta:
        model = WorkOrderManagement
        fields = ['work_order_no', 'assigned_date', 'supervisor_description', 'req_no', 'order_status', 'bus_status',
                  'procedure', 'bus_system', 'employee_assigned', 'hourly_rate', 'mechanics_description', 'labor_hours',
                  'completion_date']
        read_only_fields = ('work_order_no', 'completion_date',)

    def update(self, pk, request):
        instance = WorkOrderManagement.objects.filter(id=pk).first()

        if instance:
            instance.supervisor_description = self.validated_data['supervisor_description']
            instance.mechanics_description = self.validated_data.get('mechanics_description')
            instance.labor_hours = self.validated_data['labor_hours']
            instance.hourly_rate = self.validated_data['hourly_rate']
            instance.procedure = self.validated_data['procedure']

            instance.employee_assigned = self.validated_data['employee_assigned']
            if self.context['request'].data['completion_date']:
                instance.completion_date = datetime.datetime.strptime(self.context['request'].data['completion_date'], '%d/%m/%Y').strftime('%Y-%m-%d')

        if self.validated_data['order_status'] == ORDER_STATUS[0][0]:
            instance.order_status = self.validated_data['order_status']
            instance.progress_at = datetime.datetime.now()
            WorkOrderLog.objects.create(order=instance, user=self.context['request'].user,
                                        log='Work order status changed to In progress.', company=self.context['request'].user.company)
        elif self.validated_data['order_status'] == ORDER_STATUS[1][0]:
            WorkOrderLog.objects.create(order=instance, user=self.context['request'].user,
                                        log='Work order status changed to Close.',
                                        company=self.context['request'].user.company)
            instance.order_status = self.validated_data['order_status']
            instance.close_at = datetime.datetime.now()
            if instance.req_type == REPAIR_REQ_TYPE:
                repair = RepairRequest.objects.filter(id=instance.repair_req.id).first()
                repair.request_status = REPAIR_STATUS_OPTION[2][0]
                repair.save()
            elif instance.req_type == SERVICE_REQ_TYPE:
                repair = ServiceRequest.objects.filter(id=instance.service_req.id).first()
                repair.request_status = REPAIR_STATUS_OPTION[2][0]
                repair.save()
                bus = BusManagement.objects.filter(id=instance.service_req.bus.id).first()
                if self.context['request'].data['schedule_service']:
                    bus.schedule_service = datetime.datetime.strptime(self.context['request'].data['schedule_service'], '%d/%m/%Y').strftime('%Y-%m-%d')
                bus.save()
        elif self.validated_data['order_status'] == ORDER_STATUS[2][0]:
            WorkOrderLog.objects.create(order=instance, user=self.context['request'].user,
                                        log='Work order status changed to Hold.',
                                        company=self.context['request'].user.company)
            instance.order_status = self.validated_data['order_status']

        if instance.req_type == REPAIR_REQ_TYPE:
            repair = RepairRequest.objects.filter(id=instance.repair_req.id).first()
            repair.bus_system = self.validated_data['bus_system']
            repair.save()
            bus = BusManagement.objects.filter(id=instance.repair_req.bus.id).first()
            bus.status = self.validated_data['bus_status']
            bus.save()
        elif instance.req_type == SERVICE_REQ_TYPE:
            service = ServiceRequest.objects.filter(id=instance.service_req.id).first()
            service.bus_system = self.validated_data['bus_system']
            service.save()
            bus = BusManagement.objects.filter(id=instance.service_req.bus.id).first()
            bus.status = self.validated_data['bus_status']
            bus.save()

        instance.save()
        return instance


class WorkOrderListSerializer(serializers.ModelSerializer):
    """Listin serializer for work order"""
    req_by = serializers.SerializerMethodField()
    req_no = serializers.SerializerMethodField()
    req_type = serializers.SerializerMethodField()
    bus_id = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderManagement
        fields = ['id', 'work_order_no', 'req_type', 'req_no', 'req_by', 'assigned_date', 'order_status', 'bus_id', 'bus_status']

    def get_bus_status(self, obj):
        r = None
        if obj.repair_req:
            r = obj.repair_req.bus.status
        if obj.service_req:
            r = obj.service_req.bus.status
        return r

    def get_req_by(self, obj):
        return "%s %s" % (obj.req_by.first_name, obj.req_by.last_name)

    def get_bus_id(self, obj):
        r = None
        if obj.repair_req:
            r = obj.repair_req.bus.bus_id
        if obj.service_req:
            r = obj.service_req.bus.bus_id
        return r

    def get_req_no(self, obj):
        r = None
        if obj.repair_req:
            r = obj.repair_req.repair_no
        if obj.service_req:
            r = obj.service_req.service_no
        return r

    def get_req_type(self, obj):
        r = None
        if obj.req_type == REPAIR_REQ_TYPE:
            r = "Repair Request"
        if obj.req_type == SERVICE_REQ_TYPE:
            r = "Service Request"
        return r


class WorkOrderExportSerializer(serializers.ModelSerializer):
    """Work order serializer functionality """
    req_by = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()
    req_no = serializers.SerializerMethodField()
    req_type = serializers.SerializerMethodField()
    assigned_date = serializers.SerializerMethodField()
    bus_id = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderManagement
        fields = ['work_order_no', 'req_type', 'req_no', 'req_by', 'assigned_date', 'order_status', 'bus_id', 'bus_status']

    def get_bus_status(self, obj):
        r = None
        if obj.repair_req:
            r = obj.repair_req.bus.status
        if obj.service_req:
            r = obj.service_req.bus.status
        return r

    def get_bus_id(self, obj):
        r = None
        if obj.repair_req:
            r = obj.repair_req.bus.bus_id
        if obj.service_req:
            r = obj.service_req.bus.bus_id
        return r

    def get_req_by(self, obj):
        return "%s %s" %(obj.req_by.first_name, obj.req_by.last_name)

    def get_assigned_date(self, obj):
        d = None
        if obj.assigned_date:
            date = str(obj.assigned_date)
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d

    def get_req_type(self, obj):
        if obj.req_type == REPAIR_REQ_TYPE:
            return "Repair Request"
        else:
            return "Service Request"

    def get_order_status(self, obj):
        s = ""
        if obj.order_status == ORDER_STATUS[0][0]:
            s = "In progress"
        if obj.order_status == ORDER_STATUS[1][0]:
            s = "Closed"
        if obj.order_status == ORDER_STATUS[2][0]:
            s = "Hold"
        return s

    def get_req_no(self, obj):
        r = None
        if obj.repair_req:
            r = obj.repair_req.repair_no
        if obj.service_req:
            r = obj.service_req.service_no
        return r


class ServiceRequestSerializer(serializers.ModelSerializer):
    """create service Request serializer"""
    bus_status = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = ['id', 'resolution_date', 'bus', 'description', 'request_status', 'created_at', 'bus_status',
                  'service_no', 'bus_system']
        read_only_fields = ('resolution_date',)

    def get_bus_status(self, obj):
        return obj.bus.status

    def get_created_at(self, obj):
        return obj.created_at.date()

    def create(self, *args, **kwargs):
        service = ServiceRequest(
            resolution_date=datetime.datetime.strptime(self.context['resolution_date'], '%d/%m/%Y').strftime(
                '%Y-%m-%d'),
            bus=self.validated_data['bus'],
            description=self.validated_data['description'],
            bus_system=self.validated_data['bus_system'],
            user=self.context['request'].user,
            company=self.context['request'].user.company
        )

        bus = BusManagement.objects.filter(id=self.validated_data['bus'].id).first()
        bus.status = self.context['request'].data['bus_status']
        bus.save()
        BusLog.objects.create(bus=bus, user=self.context['request'].user,
                              log='service request raised', company=self.context['request'].user.company)

        service.schedule_date = bus.schedule_service
        service.save()
        return service


class UpdateServiceRequestSerializer(serializers.ModelSerializer):
    """update service Request serializer"""
    bus_id = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = ['id', 'resolution_date', 'bus', 'description', 'created_at', 'bus_status',
                  'request_status', 'bus_id', 'service_no', 'user_name', 'bus_system']
        read_only_fields = ('resolution_date',)

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.first_name + ' ' + obj.user.last_name
        return None

    def get_bus_id(self, obj):
        return obj.bus.bus_id

    def get_bus_status(self, obj):
        return obj.bus.status

    def get_created_at(self, obj):
        return obj.created_at.date()

    def update(self, instance):
        obj = ServiceRequest.objects.filter(id=instance).first()
        if obj:
            obj.resolution_date = datetime.datetime.strptime(self.context['resolution_date'], '%d/%m/%Y').strftime(
                '%Y-%m-%d')
            obj.description = self.validated_data.get('description')   
            obj.bus_system = self.validated_data.get('bus_system')
        bus_status = BusManagement.objects.filter(id=obj.bus.id).first()
        bus_status.status = self.context['request'].data['bus_status']
        bus_status.save()
        obj.save()
        BusLog.objects.create(bus=bus_status, user=self.context['request'].user, log='service request updated',
                              company=self.context['request'].user.company)
        return obj


class ListServiceSerializer(serializers.ModelSerializer):
    """listing service Request serializer"""
    bus_id = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    resolution_date = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = ['id', 'resolution_date', 'bus', 'description', 'created_at', 'bus_status', 'service_no',
                  'request_status', 'bus_id']

    def get_bus_id(self, obj):
        return obj.bus.bus_id

    def get_bus_status(self, obj):
        return obj.bus.status

    def get_created_at(self, obj):
        date = str(obj.created_at.date())
        d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d

    def get_resolution_date(self, obj):
        date = str(obj.resolution_date)
        d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return d


class ServiceRequestExportSerializer(serializers.ModelSerializer):
    """Export service Request serializer"""
    bus_id = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    resolution_date = serializers.SerializerMethodField()
    bus_status = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = ['service_no', 'created_at', 'resolution_date', 'bus_id', 'description',  'request_status', 'bus_status']

    def get_bus_id(self, obj):
        return obj.bus.bus_id

    def get_created_at(self, obj):
        d = None
        if obj.created_at:
            date = str(obj.created_at).split(" ")[0]
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
        return d

    def get_resolution_date(self, obj):
        d = None
        if obj.resolution_date:
            date = str(obj.resolution_date).split(" ")[0]
            d = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
        return d

    def get_bus_status(self, obj):
        s = ""
        if obj.bus.status == BUS_STATUS_OPTION[0][0]:
            s = 'In Service'
        if obj.bus.status == BUS_STATUS_OPTION[1][0]:
            s = 'Out Of Service'
        if obj.bus.status == BUS_STATUS_OPTION[2][0]:
            s = 'Scheduled Service'
        if obj.bus.status == BUS_STATUS_OPTION[3][0]:
            s = 'Awaiting for parts'
        return s

    def get_request_status(self, obj):
        s = ""
        if obj.request_status == REPAIR_STATUS_OPTION[0][0]:
            s = 'Pending'
        if obj.request_status == REPAIR_STATUS_OPTION[1][0]:
            s = 'In progress'
        if obj.request_status == REPAIR_STATUS_OPTION[2][0]:
            s = 'Resolved'
        return s


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class GraphOrderSerializer(serializers.ModelSerializer):
    """Graph for work order serializer"""
    pending_percent = serializers.CharField(max_length=20, read_only=True)
    progress_percent = serializers.CharField(max_length=20, read_only=True)
    pending = serializers.CharField(max_length=20, read_only=True)
    progress = serializers.CharField(max_length=20, read_only=True)
    total = serializers.CharField(max_length=20, read_only=True)
    resolve_percent = serializers.CharField(max_length=20, read_only=True)
    hold = serializers.CharField(max_length=20, read_only=True)
    hold_percent = serializers.CharField(max_length=20, read_only=True)
    date = serializers.CharField(max_length=20, read_only=True)
    resolve = serializers.CharField(max_length=20, read_only=True)

    class Meta:
        model = WorkOrderManagement
        fields = ['date', 'pending_percent', 'progress_percent', 'pending', 'progress', 'total', 'resolve_percent',
                   'hold', 'hold_percent', 'resolve']


class ListViewBusSerializer(serializers.ModelSerializer):
    """list bus serializer"""
    request = serializers.SerializerMethodField()
    out_of_service = serializers.SerializerMethodField()
    back_in_service = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()
    fuel_input = serializers.SerializerMethodField()

    class Meta:
        model = BusManagement
        fields = ['id','bus_id', 'out_of_service', 'back_in_service', 'request', 'status', 'odo_reading', 'fuel_input',
                  'average_fuel_cost', 'labor_cost', 'editable']

    def get_fuel_input(self, obj):
        return obj.fuel_type.fuel_type if obj.fuel_type else None

    def get_editable(self, obj):
        return self.context['request'].user.designation.bus_edit

    def get_back_in_service(self, obj):
        service_date = ''
        if obj.back_in_service:
            date = str(obj.back_in_service.date())
            service_date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return service_date

    def get_out_of_service(self, obj):
        service_date = ''
        if obj.out_of_service:
            date = str(obj.out_of_service.date())
            service_date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return service_date

    def get_request(self, obj):
        result = dict(bus_system='', description='', request_no='', order_no='', id='', order_id='')
        repair = RepairRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=obj).first()
        if repair:
            result["bus_system"] = repair.bus_system if repair.bus_system else None
            result["description"] = repair.description
            result["request_no"] = repair.repair_no
            result["id"] = '/detail/'+ str(repair.id) +'/repair/'
            order = WorkOrderManagement.objects.filter(Q(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0])),
                                                       repair_req=repair).first()
            if order:
                result["order_no"] = order.work_order_no
                result["order_id"] = order.id
            else:
                result["order_no"] = "Unassigned"

        service = ServiceRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=obj).first()
        if service:
            result["bus_system"] = service.bus_system
            result["description"] = service.description
            result["request_no"] = service.service_no
            result["id"] = '/detail/'+ str(service.id) +'/service/'
            order = WorkOrderManagement.objects.filter(Q(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0])),
                                                       service_req=service).first()
            if order:
                result["order_no"] = order.work_order_no
                result["order_id"] = order.id
            else:
                result["order_no"] = "Unassigned"

        return result


class RolesAndPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'


class RolesAndPermissionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = '__all__'


class RolesAndPermissionUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = ['main_dashboard', 'bus_management', 'man_management', 'work_management', 'repair_request',
                  'service_request', 'user_admin_management']


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture', 'first_name', 'last_name', 'contact']

    def update(self):
        user = self.context["request"].user
        user.profile_picture = self.validated_data.get('profile_picture')
        user.save()
        return user

    def edit(self):
        user = self.context["request"].user
        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.contact = self.validated_data['contact']
        user.save()
        return user