from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404, HttpResponse
from .serializers import (RegistrationSerializer, NewPasswordSerializer, BusManagementSerializer,
                         PasswordResetSerializer, UpdateBusManagementSerializer, RepairRequestSerializer,
                         UpdateRepairRequestSerializer, LsitBusManagementSerializer,ListRepairSerializer,
                         UpdateEmployeeSerializer, RepairRequestExportSerializer, RosterSerializer,
                         EmployeeListingSerializer, UpdateRosterSerializer, LeavesApplicationsSerializer,
                         LeaveListingSerializer, ChangeLeaveStatusSerializer, RosterListingSerializer,
                         EmployeeListingExportSerializer, RosterExportSerializer, BusexportSerializer,
                         LeavesExportSerializer, LeaveDataWithRangeSerializer, HolidaySerializer,
                         WorkOrderManagementSerializer, WorkOrderExportSerializer, WorkOrderListSerializer, WorkOrderUpdateSerializer, WorkOrderCreateSerializer,
                         ServiceRequestSerializer, UpdateServiceRequestSerializer, ListServiceSerializer, ServiceRequestExportSerializer,
                         ManufacturerSerializer, GraphOrderSerializer, ListViewBusSerializer, RolesAndPermissionSerializer,
                          RolesAndPermissionListSerializer, UserEditSerializer, RolesAndPermissionUpdateSerializer, BusLogSerializer)

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from .models import User, BusManagement, RepairRequest, Roster, BusLog, LeaveManagement, Holiday, BusPhotos, \
    Manufacturer,  WorkOrderManagement, ServiceRequest, Designation

from rest_framework.decorators import action
from helper_functions import AdminPagination, DefaultPagination, DashboardPagination
from django.db.models import Q
import datetime
from constants import *
from django.db.models import Count
from .leave_csv_reader import CSVImporter
from .export_helper import get_file, export_as_email
from dateutil.relativedelta import relativedelta
from helper_functions import send_register_mail


class RegistrationApi(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = AdminPagination

    def get_serializer_class(self):
        serializer = RegistrationSerializer
        if self.action == 'list':
            serializer = EmployeeListingSerializer
        elif self.action == 'update' or 'retrieve':
            serializer = UpdateEmployeeSerializer

        return serializer

    def get_queryset(self):
        check = self.request.query_params
        if 'search' in check and check['search'] != '':
            user = User.objects.filter(company=self.request.user.company)
            for term in check["search"].split():
                queryset = user.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term) |
                                   Q(email__icontains=term) | Q(employee_id__iexact=term))
        else:
            queryset = User.objects.filter(company=self.request.user.company).order_by('-created_at')
        return queryset

    def create(self, request, *args, **kwargs):
        serialized = RegistrationSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            register = serialized.create()
            serialized = RegistrationSerializer(register)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        raise Http404

    def update(self, request, pk=None):
        serialized = UpdateEmployeeSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            application = serialized.update(pk)
            serialized = UpdateEmployeeSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404

    @action(methods=['put'], detail=False)
    def modules(self, request):
        user = User.objects.filter(email=request.user.email).first()
        if user:
            if 'all_buses' in request.data:
                user.all_buses = True if request.data['all_buses'] == 'true' else False
            elif 'total_wo' in request.data:
                user.total_wo = True if request.data['total_wo'] == 'true' else False
            elif 'bus_analytics' in request.data:
                user.bus_analytics = True if request.data['bus_analytics'] == 'true' else False
            elif 'bus_calendar' in request.data:
                user.bus_calendar = True if request.data['bus_calendar'] == 'true' else False
            elif 'dark_mode' in request.data:
                user.dark_mode = True if request.data['dark_mode'] == 'true' else False
            user.save()
            return Response(status=201)


    @action(methods=['GET'],detail=False)
    def check_user(self, request):
        email, employee_id = None, None
        if 'email' in request.GET:
            email = request.GET['email']
        if 'employee_id' in request.GET:
            employee_id = request.GET['employee_id']
        if email:
            if User.objects.filter(email=email).exists():
                result = False
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = True
                return Response(result, status=status.HTTP_200_OK)
        if employee_id:
            if User.objects.filter(employee_id=employee_id).exists():
                result = False
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = True
                return Response(result, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=False)
    def get_designation(self, request):
        if 'design' in request.GET:
            emp = User.objects.filter(id=request.GET['design']).first()
            return Response(emp.designation.designation_name, status=status.HTTP_201_CREATED)


class PasswordView(viewsets.GenericViewSet):

    def get_serializer_class(self):
        if self.action == 'change_password':
            serializer = NewPasswordSerializer
        elif self.action == 'reset_password':
            serializer = PasswordResetSerializer
        return serializer

    @action(methods=['POST'], detail=False)
    def reset_password(self, request):
        '''send email forgot password'''
        serialized = PasswordResetSerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            subscription = serialized.send_email(by=request.data['email'], request=request)
            serialized = PasswordResetSerializer(subscription)
            return Response({"success": "Your request to reset password has been received. Please check "
                                        "your email to reset your password."}, status=status.HTTP_201_CREATED)
        raise Http404

    @action(methods=['POST'], detail=False, url_path='change_password/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)',
            url_name='change_password')
    def change_password(self, request, uidb64, token):
        '''confirm password view'''
        self.token_generator = default_token_generator
        self.user = self.get_user(uidb64)
        if self.token_generator.check_token(self.user, token):
            serialized = NewPasswordSerializer(data=request.data, context={'request': request})
            if serialized.is_valid(raise_exception=True):
                subscription = serialized.change_password(by=self.user)
                serialized = NewPasswordSerializer(subscription)
                return Response({'success':'password reset succesfully.'}, status=status.HTTP_201_CREATED)
        raise Http404

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user


class BusManagementApi(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                       mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = AdminPagination

    def get_serializer_class(self):
        serializer = ListViewBusSerializer
        if self.action == 'create':
            serializer = BusManagementSerializer
        elif self.action == 'update':
            serializer = UpdateBusManagementSerializer
        elif self.action == 'retrieve':
            serializer = UpdateBusManagementSerializer
        return serializer

    def get_queryset(self):
        queryset = BusManagement.objects.filter(company=self.request.user.company).order_by('-created_at')

        return queryset

    def create(self, request, *args, **kwargs):
        serialized = BusManagementSerializer(data=request.data, context={'request': request, 'file': request.FILES.getlist('bus_photos'),
                                                                         'schedule_service': request.data["schedule_service"],
                                                                         'schedule_repair': request.data["schedule_repair"]})
        if serialized.is_valid(raise_exception=True):
            register = serialized.create()
            serialized = BusManagementSerializer(register)
            return Response({'success': 'Created successfully'}, status=status.HTTP_201_CREATED)
        raise Http404

    @action(methods=['GET'], detail=False)
    def bus_data(self, request):
        query = self.get_queryset()
        start_date = datetime.datetime.now()
        lt_date = start_date + relativedelta(months=-1, day=1)
        back_month = datetime.datetime(lt_date.year, (lt_date + relativedelta(months=1)).month,
                                       1) - datetime.timedelta(days=1)
        last_month = query.filter(created_at__date__range=[lt_date.date(), back_month.date()]).count()
        this_month = query.filter(created_at__date__range=[(start_date + relativedelta(day=1)).date(), start_date.date()]).count()

        all_bus = query.count()
        active_bus = query.filter(status='1').count()
        ss = query.filter(status='3').count()
        oos = query.filter(status='2').count()
        wp = query.filter(status='4').count()
        tem = {'in_service': active_bus, 'ss': ss, 'os': oos, 'total': all_bus, "wp": wp, 'last_month': last_month,
               'this_month' :this_month}
        return Response(tem, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def calender_data(self, request):

        service = BusManagement.objects.filter(~Q(schedule_service=None), Q(company=request.user.company)).values(
            'schedule_service', ).annotate(
            buses=Count('bus_id'))
        service_data = []

        for data in service:
            service_list = BusManagement.objects.filter(schedule_service=data['schedule_service'], company=request.user.company
                                             ).values_list('bus_id')
            data['bus_no'] = list(service_list)
            service_data.append(data)

        licensing_data = []
        license = BusManagement.objects.filter(~Q(vehicle_licensing=None), Q(company=request.user.company)).values(
            'vehicle_licensing', ).annotate(
            buses=Count('bus_id'))

        for vehicle in license:
            vehicle_list = BusManagement.objects.filter(vehicle_licensing=vehicle['vehicle_licensing'], company=request.user.company
                                             ).values_list('bus_id')
            vehicle['bus_no'] = list(vehicle_list)
            licensing_data.append(vehicle)
        return Response({'service_data': service_data, 'licensing_data': licensing_data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial,
                                         context={'request': request, 'file': request.FILES.getlist('bus_photos'),
                                                  'schedule_service': request.data["schedule_service"],
                                                  'schedule_repair': request.data["schedule_repair"]
                                                  })
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        repair = RepairRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=instance)
        if repair:
            return Response({'error': "This bus has pending Repair request."}, status=status.HTTP_404_NOT_FOUND)
        service = ServiceRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=instance)
        if service:
            return Response({'error': "This bus has pending Service request."}, status=status.HTTP_404_NOT_FOUND)
        BusLog.objects.create(bus=instance, user=request.user,
                              log='Deleted the bus', company=request.user.company)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepairRequestApi(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = AdminPagination

    def get_queryset(self):

        if 'active' in self.request.query_params:
            queryset = RepairRequest.objects.filter(Q(company=self.request.user.company) & (Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0]))).order_by('-created_at')
        elif 'completed' in self.request.query_params:
            queryset = RepairRequest.objects.filter(Q(company=self.request.user.company) & Q(request_status=REPAIR_STATUS_OPTION[2][0])).order_by('-created_at')
        else:
            queryset = RepairRequest.objects.filter(company=self.request.user.company).order_by('-created_at')
        return queryset

    def get_serializer_class(self):
        serializer = RepairRequestSerializer
        if self.action == 'create':
            serializer = RepairRequestSerializer
        elif self.action == 'update':
            serializer = UpdateRepairRequestSerializer
        elif self.action == 'list':
            serializer = ListRepairSerializer
        elif self.action == 'retrieve':
            serializer = UpdateRepairRequestSerializer
        return serializer

    def create(self, request, *args, **kwargs):
        serialized = RepairRequestSerializer(data=request.data, context={'request': request, 'resolution_date': request.data["resolution_date"]})
        if serialized.is_valid(raise_exception=True):
            create = serialized.create()
            serialized = RepairRequestSerializer(create)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        raise Http404

    def update(self, request, pk=None):
        serialized = UpdateRepairRequestSerializer(data=request.data, context={'request': request, 'resolution_date': request.data["resolution_date"]})
        if serialized.is_valid(raise_exception=True):
            application = serialized.update(pk)
            serialized = UpdateRepairRequestSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404

    @action(methods=['GET'], detail=False)
    def check_request(self, request):
        if 'bus_id' in request.GET:
            bus_no = request.GET['bus_id']
            if RepairRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=bus_no).exists() or \
                    ServiceRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=bus_no).exists():
                return Response(False, status=status.HTTP_200_OK)
            return Response(True, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def bus_status(self, request):
        if 'bus_id' in request.GET:
            bus_no = request.GET['bus_id']
            bus = BusManagement.objects.filter(id=bus_no).first()
            return Response(bus.status, status=status.HTTP_200_OK)\

    @action(methods=['GET'], detail=False)
    def get_bus(self, request):
        if 'req_no' in request.GET:
            req_no = request.GET['req_no']
            req = RepairRequest.objects.filter(id=req_no).first()
            return Response({'bus_id': req.bus.bus_id, 'status': req.bus.status, 'bus_system': req.bus_system}, status=status.HTTP_200_OK)
        if 'service_no' in request.GET:
            service_no = request.GET['service_no']
            req = ServiceRequest.objects.filter(id=service_no).first()
            return Response({'bus_id': req.bus.bus_id, 'status': req.bus.status, 'bus_system': req.bus_system}, status=status.HTTP_200_OK)


class MainDashboardBusData(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LsitBusManagementSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = BusManagement.objects.filter(company=self.request.user.company).order_by('-created_at')
        return queryset


class BusLogsApi(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = BusLogSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]


    @action(methods=['GET'], detail=False)
    def logs(self, request):
        logs = BusLog.objects.filter(company=request.user.company).last()
        if logs:
            serizaler = BusLogSerializer(logs)
            return Response(serizaler.data, status=status.HTTP_200_OK)
        raise Http404


class RosterApi(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):

    def get_serializer_class(self):
        serializer = RosterSerializer
        if self.action == 'update':
            serializer = UpdateRosterSerializer
        elif self.action == 'list':
            serializer = RosterListingSerializer
        return serializer

    permission_classes = [IsAuthenticated]
    pagination_class = AdminPagination

    def get_queryset(self):
        check = self.request.query_params
        queryset = Roster.objects.filter(company=self.request.user.company).order_by('-created_at')
        if 'search' in check and check["search"] != '' and check["dept"] == '':
            queryset = queryset.filter(Q(name__icontains=check["search"]) | Q(roster_no__iexact=check["search"]))
        elif 'search' in check and check["search"] != '' and 'dept' in check and check["dept"] != '':
            queryset = queryset.filter(Q(name__icontains=check["search"]) | Q(roster_no__iexact=check["search"]), department=check["dept"])
        elif 'dept' in check and check["dept"] != '':
            queryset = queryset.filter(department=check["dept"])
        elif 'department' in self.request.query_params:
            queryset = Roster.objects.filter(company=self.request.user.company, department=self.request.query_params['department']).order_by('-created_at')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from_date = datetime.datetime.strptime(request.data['from_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        to_date = datetime.datetime.strptime(request.data['to_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        serializer.save(company=self.request.user.company, from_date=from_date, to_date=to_date)
        mail_list = []
        for member in serializer.data['members']:
            user = User.objects.filter(id=member).first()
            subject = "You have been added to New Roster"
            data = {
                "mail_template_args": {
                    'name': '%s %s' % (user.first_name, user.last_name),
                    'roster': serializer.data,
                    'domain': request.META['HTTP_HOST'],

                    'protocol': 'https' if request.is_secure() else 'http',

                },
                "mail_to": user.email,
                "mail_template": "email/roster.html",
                "mail_subject": subject

            }
            mail_list.append(data)
        send_register_mail(mail_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        serialized = UpdateRosterSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            application = serialized.update(pk)
            serialized = UpdateRosterSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404

    @action(methods=['GET'], detail=False)
    def check_roster(self, request):
        roster_no, department, roster_id = None, None, None
        if 'roster_no' in request.GET:
            roster_no = request.GET['roster_no']

        if 'department' in request.GET:
            department = request.GET['department']
        if 'id' in request.GET:
            roster_id = request.GET['id']

        if roster_id !='NaN':
            roster = Roster.objects.filter(id=roster_id).first()

            if int(roster_no) != roster.roster_no:

                if Roster.objects.filter(roster_no=roster_no, department=department).exists():
                    return Response(False, status=status.HTTP_200_OK)
                return Response(True, status=status.HTTP_200_OK)
            return Response(True, status=status.HTTP_200_OK)
        else:
            if roster_no:
                if Roster.objects.filter(roster_no=roster_no, department=department).exists():
                    return Response(False, status=status.HTTP_200_OK)
                return Response(True, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)


class RosterDashboardApi(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        q = Roster.objects.filter(company=self.request.user.company)
        return q

    @action(methods=['GET'], detail=False)
    def roster_data(self, request):
        query = self.get_queryset()
        all_roster = query.count()
        active_roster = query.filter(status='1').count()
        inactive_roster = query.filter(status='2').count()
        start_date = datetime.datetime.now()
        lt_date = start_date + relativedelta(months=-1, day=1)
        back_month = datetime.datetime(lt_date.year, (lt_date + relativedelta(months=1)).month,
                                       1) - datetime.timedelta(days=1)
        last_month = query.filter(created_at__date__range=[lt_date.date(), back_month.date()]).count()
        this_month = query.filter(created_at__date__range=[(start_date + relativedelta(day=1)).date(), start_date.date()]).count()
        tem = {'all_roster': all_roster, 'active_roster': active_roster, 'inactive_roster': inactive_roster,
               'last_month': last_month, 'this_month': this_month}
        return Response(tem, status=status.HTTP_200_OK)


class UserListingApi(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = EmployeeListingSerializer

    # def get_serializer_class(self):
    #     return EmployeeListingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = User.objects.filter(company=self.request.user.company)
        if 'dept' in self.request.query_params:
            queryset = queryset.filter(department=self.request.query_params['dept'])
        return queryset


class UploadCsvLeavesApi(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    def get_serializer_class(self):
        serializer = LeaveListingSerializer
        if self.action == 'create':
            serializer = LeavesApplicationsSerializer
        elif self.action == 'update':
            serializer = ChangeLeaveStatusSerializer
        return serializer

    permission_classes = [IsAuthenticated]
    pagination_class = AdminPagination

    def get_queryset(self):
        queryset = LeaveManagement.objects.filter(company=self.request.user.company)
        if 'pending' in self.request.query_params:
            queryset = LeaveManagement.objects.filter(company=self.request.user.company, status="pending") 
        elif 'approved' in self.request.query_params:
            queryset = LeaveManagement.objects.filter(company=self.request.user.company, status="approved")
        elif 'rejected' in self.request.query_params:
            queryset = LeaveManagement.objects.filter(company=self.request.user.company, status="rejected")
        return queryset

    def create(self, request, *args, **kwargs):
        fileobj = request.FILES['file']
        importer = CSVImporter()
        results = importer.upsert(fileobj, request, as_string_obj=False)
        return Response(results)

    def update(self, request, pk=None):
        serialized = ChangeLeaveStatusSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            application = serialized.update(pk, request)
            serialized = ChangeLeaveStatusSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404


class LeaveListingApi(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LeaveListingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        start = datetime.datetime.today().date()
        end = datetime.datetime.today().date()

        queryset = LeaveManagement.objects.filter(company=self.request.user.company, status='approved')
        q = queryset.filter(
            (Q(from_date__lte=start) & Q(to_date__gte=start)) | (Q(to_date__gte=end) & Q(from_date__lte=end)) | (
                        Q(from_date__gte=start) & Q(to_date__lte=end)))
        return q


class ExportApi(viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action == 'repair_requests':
            return RepairRequestExportSerializer
        elif self.action == 'rosters':
            return RosterExportSerializer
        elif self.action == 'employees':
            return EmployeeListingExportSerializer
        elif self.action == 'buses':
            return ListViewBusSerializer
        elif self.action == 'leaves':
            return LeavesExportSerializer
        elif self.action == 'work_orders':
            return WorkOrderExportSerializer
        elif self.action == 'service_requests':
            return ServiceRequestExportSerializer

    def get_queryset(self):
        if self.action == 'repair_requests':
            if self.request.query_params['active'] == 'active':
                return RepairRequest.objects.filter(Q(company=self.request.user.company) & (Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0]))).order_by('-created_at')
            elif self.request.query_params['completed'] == 'completed':
                return RepairRequest.objects.filter(company=self.request.user.company, request_status=REPAIR_STATUS_OPTION[2][0]).order_by('-created_at')
            elif self.request.query_params['all'] == 'all':
                return RepairRequest.objects.filter(company=self.request.user.company).order_by('-created_at')
        elif self.action == 'rosters':
            if 'department' in self.request.query_params:
                return Roster.objects.filter(company=self.request.user.company, department=self.request.query_params['department']).order_by('-created_at')
            else:
                return Roster.objects.filter(company=self.request.user.company).order_by('-created_at')
        elif self.action == 'employees':
            return User.objects.filter(company=self.request.user.company).order_by('-created_at')
        elif self.action == 'buses':
            return BusManagement.objects.filter(company=self.request.user.company).order_by('-created_at')
        elif self.action == 'leaves':
            return LeaveManagement.objects.filter(company=self.request.user.company)
        elif self.action == 'work_orders':
            if 'request' in self.request.query_params:
                if self.request.query_params['active'] == 'active':
                    return WorkOrderManagement.objects.filter(Q(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0])),
                                                              company=self.request.user.company, req_type=self.request.query_params['request']).order_by('-created_at')
                elif self.request.query_params['closed'] == 'closed':
                    return WorkOrderManagement.objects.filter(order_status=ORDER_STATUS[1][0], company=self.request.user.company,
                                                              req_type=self.request.query_params['request']).order_by('-created_at')
                elif self.request.query_params['all'] == 'all':
                    return WorkOrderManagement.objects.filter(company=self.request.user.company,req_type=self.request.
                                                              query_params['request']).order_by('-created_at')
            else:
                if self.request.query_params['active'] == 'active':
                    return WorkOrderManagement.objects.filter(Q(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0])),
                                                              company=self.request.user.company).order_by('-created_at')
                elif self.request.query_params['closed'] == 'closed':
                    return WorkOrderManagement.objects.filter(order_status=ORDER_STATUS[1][0],company=self.request.user.company,
                                                              ).order_by('-created_at')
                elif self.request.query_params['all'] == 'all':
                    return WorkOrderManagement.objects.filter(company=self.request.user.company).order_by('-created_at')
        elif self.action == 'service_requests':
            if self.request.query_params['active'] == 'active':
                return ServiceRequest.objects.filter(Q(company=self.request.user.company) & (Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0]))).order_by('-created_at')
            elif self.request.query_params['completed'] == 'completed':
                return ServiceRequest.objects.filter(company=self.request.user.company, request_status=REPAIR_STATUS_OPTION[2][0]).order_by('-created_at')
            elif self.request.query_params['all'] == 'all':
                return ServiceRequest.objects.filter(company=self.request.user.company).order_by('-created_at')
    def list(self, request):
        exports = self.get_extra_action_url_map()
        return Response(exports)

    @action(methods=['GET'], detail=False)
    def repair_requests(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = []
        file_type = 'pdf'
        output_file = None
        count = 1
        for item in serializer.data:
            temp = {
                    'repair_no' : item['repair_no'],
                    'created_at' : item['created_at'],
                    'resolution_date' : item['resolution_date'],
                    'bus_id' : item['bus_id'],
                    'description' : item['description'],
                    'request_status' : item['request_status'],
                    'bus_status' : item['bus_status']          
            }
            data.append(temp)
            count = count + 1
        if 'file_type' in request.query_params:
            file_type = request.query_params['file_type']
        output_file = get_file(data, self.action, file_type, request)
        if output_file:
            if 'email' in request.query_params:
                try:
                    export_as_email(self.action, request, "Repair Requests File", output_file, file_type)
                    return Response("Email Sent.", status.HTTP_200_OK)
                except Exception as e:
                    return Response("Something went wrong. "+str(e), status.HTTP_503_SERVICE_UNAVAILABLE)  
            response = HttpResponse(output_file, content_type='application/%s' % file_type)
            time_str = datetime.datetime.today().date()
            filename = "repair_requests-%s.%s" % (time_str, file_type)
            content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response

        return Response("Something went wrong.", status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['GET'], detail=False)
    def rosters(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = []
        file_type = 'pdf'
        output_file = None
        count = 1
        for item in serializer.data:
            leave_class = '#000'
            for get in item['members']:
                queryset = LeaveManagement.objects.filter(company=self.request.user.company, status='approved', employee=get)
                leaves = queryset.filter((Q(from_date__lte=item['from_date']) & Q(to_date__gte=item['from_date'])) |
                                         (Q(to_date__gte=item['to_date']) & Q(from_date__lte=item['to_date'])) |
                                         (Q(from_date__gte=item['from_date']) & Q(to_date__lte=item['to_date'])))
                if leaves:
                    leave_class = "#FF0000"
            temp = {
                "count": count,
                "name": item['name'],
                "status": item['status'],
                "department": item['department'],
                "roster_no": item['roster_no'],
                "date": item['date'],
                "time": item['time'],
                "week_offs": item['week_offs'],
                "no_of_members": item['no_of_members'],
                "leave_class": leave_class
            }
            data.append(temp)
            count = count+1
        if 'file_type' in request.query_params:
            file_type = request.query_params['file_type']
        output_file = get_file(data, self.action, file_type, request)
        if output_file:
            if 'email' in request.query_params:
                try:
                    export_as_email(self.action, request, "Rosters File", output_file, file_type)
                    return Response("Email Sent.", status.HTTP_200_OK)
                except Exception as e:
                    return Response("Something went wrong. "+str(e), status.HTTP_503_SERVICE_UNAVAILABLE)  
            response = HttpResponse(output_file, content_type='application/%s' % file_type)
            time_str = datetime.datetime.today().date()
            filename = "rosters-%s.%s" % (time_str, file_type)
            content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response

        return Response("Something went wrong.", status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['GET'], detail=False)
    def employees(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = []
        file_type = 'pdf'
        output_file = None
        count = 1
        for item in serializer.data:
            temp = {
                    "count": count,
                    "email": item['email'],
                    "name": item['name'],
                    "company": item['company'],
                    "contact": item['contact'] if item['contact'] else "NA",
                    "department": item['department'],
                    "designation": item['designation'],
                    "joining_date": "NA",
                    "employee_id": item['employee_id'],
                    "driving_licence": "",
                    "id_proof": "",
                    }
            if item['joining_date']:
                temp['joining_date'] = item['joining_date']
            if item['driving_licence']:
                temp['driving_licence'] = "DL"
            if item['id_proof']:
                temp['id_proof'] = "ID"
            data.append(temp)
            count = count + 1
        if 'file_type' in request.query_params:
            file_type = request.query_params['file_type']
        output_file = get_file(data, self.action, file_type, request)
        if output_file:
            if 'email' in request.query_params:
                try:
                    export_as_email(self.action, request, "Employees File", output_file, file_type)
                    return Response("Email Sent.", status.HTTP_200_OK)
                except Exception as e:
                    return Response("Something went wrong. "+str(e), status.HTTP_503_SERVICE_UNAVAILABLE)  
            response = HttpResponse(output_file, content_type='application/%s' % file_type)
            time_str = datetime.datetime.today().date()
            filename = "employees-%s.%s" % (time_str, file_type)
            content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response

        return Response("Something went wrong.", status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['GET'], detail=False)
    def buses(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = []
        file_type = 'pdf'
        output_file = None
        count = 1
        for item in serializer.data:
            temp = {
                    'count': count,
                    'bus_id': item['bus_id'],
                    'out_of_service': item['out_of_service'],
                    'back_in_service': item['back_in_service'],
                    'bus_system': item['request']['bus_system'],
                    'description': item['request']['description'],
                    'request_no': item['request']['request_no'],
                    'order_no': item['request']['order_no'],
                    'status': None,
                    'domain': request.META['HTTP_HOST'],
                    'protocol': 'https' if request.is_secure() else 'http',
                    }
            if int(item['status']) == 1:
                temp['status'] = "IS"
            if int(item['status']) == 2:
                temp['status'] = "OOS"
            if int(item['status']) == 3:
                temp['status'] = "SS"
            if int(item['status']) == 4:
                temp['status'] = "WP"
            data.append(temp)
            count = count + 1

        if 'file_type' in request.query_params:
            file_type = request.query_params['file_type']
        output_file = get_file(data, self.action, file_type, request)
        if output_file :
            if 'email' in request.query_params:
                try:
                    export_as_email(self.action, request, "Buses File", output_file, file_type)
                    return Response("Email Sent.", status.HTTP_200_OK)
                except Exception as e:
                    return Response("Something went wrong. "+str(e), status.HTTP_503_SERVICE_UNAVAILABLE)  
            response = HttpResponse(output_file, content_type='application/%s' % file_type)
            time_str = datetime.datetime.today().date()
            filename = "buses-%s.%s" % (time_str, file_type)
            content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response

        return Response("Something went wrong.", status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['GET'], detail=False)
    def leaves(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = []
        file_type = 'pdf'
        output_file = None
        count = 1
        for item in serializer.data:
            temp = {
                    'employee_name' : item['employee_name'],
                    'employee_id' : item['employee_id'],
                    'employee_email' : item['employee_email'],
                    'description' : item['description'],
                    'date' : item['date'],
                    'status' : item['status']
                    }
            data.append(temp)
            count = count + 1
        if 'file_type' in request.query_params:
            file_type = request.query_params['file_type'].lower()
        output_file = get_file(data, self.action, file_type, request)
        if output_file:
            if 'email' in request.query_params:
                try:
                    export_as_email(self.action, request, "Leaves File", output_file, file_type)
                    return Response("Email Sent.", status.HTTP_200_OK)
                except Exception as e:
                    return Response("Something went wrong. "+str(e), status.HTTP_503_SERVICE_UNAVAILABLE)  
            response = HttpResponse(output_file, content_type='application/%s' % file_type)
            time_str = datetime.datetime.today().date()
            filename = "leaves-%s.%s" % (time_str, file_type)
            content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response

        return Response("Something went wrong.", status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['GET'], detail=False)
    def work_orders(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = []
        file_type = 'pdf'
        output_file = None
        count = 1
        for item in serializer.data:
            temp = {
                    'count': count,
                    'work_order_no': item['work_order_no'],
                    'req_type': item['req_type'],
                    'req_no': item['req_no'],
                    'req_by': item['req_by'],
                    'date' : item['assigned_date'],
                    'order_status' : item['order_status'],
                    'bus_id': item['bus_id'],
                    'bus_status': None
            }
            if item['bus_status'] == BUS_STATUS_OPTION[0][0]:
                temp['bus_status'] = "IS"
            elif item['bus_status'] == BUS_STATUS_OPTION[1][0]:
                temp['bus_status'] = "OOS"
            elif item['bus_status'] == BUS_STATUS_OPTION[2][0]:
                temp['bus_status'] = "SS"
            elif item['bus_status'] == BUS_STATUS_OPTION[3][0]:
                temp['bus_status'] = "WP"
            count = count + 1
            data.append(temp) 
        if 'file_type' in request.query_params:
            file_type = request.query_params['file_type'].lower()
        output_file = get_file(data, self.action, file_type, request)
        if output_file:
            if 'email' in request.query_params:
                try:
                    export_as_email(self.action, request.user.email, "Work Orders File", output_file, file_type)
                    return Response("Email Sent.", status.HTTP_200_OK)
                except Exception as e:
                    return Response("Something went wrong. "+str(e), status.HTTP_503_SERVICE_UNAVAILABLE)  
            response = HttpResponse(output_file, content_type='application/%s' % file_type)
            time_str = datetime.datetime.today().date()
            filename = "work_orders-%s.%s" % (time_str, file_type)
            content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response

        return Response("Something went wrong.", status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['GET'], detail=False)
    def service_requests(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = []
        file_type = 'pdf'
        output_file = None
        count = 1
        for item in serializer.data:
            temp = {
                'count':count,
                'service_no': item['service_no'],
                'created_at': item['created_at'],
                'resolution_date': item['resolution_date'],
                'bus_id': item['bus_id'],
                'description': item['description'],
                'request_status': item['request_status'],
                'bus_status': item['bus_status']
            }
            count = count + 1
            data.append(temp)
        if 'file_type' in request.query_params:
            file_type = request.query_params['file_type'].lower()
        output_file = get_file(data, self.action, file_type, request)
        if output_file:
            if 'email' in request.query_params:
                try:
                    export_as_email(self.action, request.user.email, "Work Orders File", output_file, file_type)
                    return Response("Email Sent.", status.HTTP_200_OK)
                except Exception as e:
                    return Response("Something went wrong. "+str(e), status.HTTP_503_SERVICE_UNAVAILABLE)  
            response = HttpResponse(output_file, content_type='application/%s' % file_type)
            time_str = datetime.datetime.today().date()
            filename = "service_requests-%s.%s" % (time_str, file_type)
            content = "attachment; filename=%s" % filename
            response['Content-Disposition'] = content
            return response

        return Response("Something went wrong.", status.HTTP_503_SERVICE_UNAVAILABLE)


class LeaveDataWithRangeApi(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LeaveDataWithRangeSerializer
    pagination_class = None

    def get_queryset(self):
        if 'start' and 'end' in self.request.query_params:
            start = self.request.query_params["start"]
            end = self.request.query_params["end"]
        queryset = LeaveManagement.objects.filter(company=self.request.user.company, status='approved')
        q = queryset.filter((Q(from_date__lte=start) & Q(to_date__gte=start)) | (Q(to_date__gte=end) & Q(from_date__lte=end)) | (Q(from_date__gte=start) & Q(to_date__lte=end)))
        return q


class HolidayView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = HolidaySerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        current_date = datetime.datetime.now()
        queryset = Holiday.objects.filter(holiday_date__year=current_date.year, is_public_holiday=True
                                          ).order_by('holiday_date')
        return queryset


class BusListingApi(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LsitBusManagementSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DashboardPagination

    def get_queryset(self):
        queryset = BusManagement.objects.filter(company=self.request.user.company).order_by('-created_at')
        return queryset


class UserListingDashboardApi(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = EmployeeListingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DashboardPagination

    def get_queryset(self):
        check = self.request.query_params
        if 'search' in check:
            user = User.objects.filter(company=self.request.user.company)
            queryset = user.filter(Q(first_name__icontains=check["search"]) | Q(last_name__icontains=check["search"]) |
                                   Q(email__icontains=check["search"]) | Q(employee_id__iexact=check["search"]))
        else:
            queryset = User.objects.filter(company=self.request.user.company).order_by('-created_at')
        return queryset


class BusPhotosApi(viewsets.GenericViewSet, mixins.DestroyModelMixin):
    serializer_class = LsitBusManagementSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DashboardPagination
    queryset = BusPhotos.objects.all()


class WorkOrderManagementAPI(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = AdminPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkOrderListSerializer
        elif self.action == 'update':
            return WorkOrderUpdateSerializer
        elif self.action == 'create':
            return WorkOrderCreateSerializer
        else:
            return WorkOrderManagementSerializer

    def get_queryset(self):
        queryset = WorkOrderManagement.objects.filter(company=self.request.user.company, employee_assigned=self.request.user).order_by('-created_at')
        if self.request.user.designation.work_show:
            queryset = WorkOrderManagement.objects.filter(company=self.request.user.company).order_by('-created_at')

        if 'repair' in self.request.query_params and 'active' in self.request.query_params:
            queryset = queryset.filter(Q(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0])), req_type=1)
        elif 'repair' in self.request.query_params and 'closed' in self.request.query_params:
            queryset = queryset.filter(order_status=ORDER_STATUS[1][0], req_type=1)
        elif 'repair' in self.request.query_params and 'all' in self.request.query_params:
            queryset = queryset.filter(req_type=1)
        elif 'service' in self.request.query_params and 'active' in self.request.query_params:
            queryset = queryset.filter(Q(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0])), req_type=2)
        elif 'service' in self.request.query_params and 'closed' in self.request.query_params:
            queryset = queryset.filter(order_status=ORDER_STATUS[1][0], req_type=2)
        elif 'service' in self.request.query_params and 'all' in self.request.query_params:
            queryset = queryset.filter(req_type=2)
        elif 'request' in self.request.query_params and 'active' in self.request.query_params:
            queryset = queryset.filter(Q(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0])))
        elif 'request' in self.request.query_params and 'closed' in self.request.query_params:
            queryset = queryset.filter(order_status=ORDER_STATUS[1][0])
        elif 'request' in self.request.query_params and 'all' in self.request.query_params:
            queryset = queryset
        return queryset

    def create(self, request, *args, **kwargs):
        serialized = WorkOrderCreateSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            create = serialized.create()
            serialized = WorkOrderCreateSerializer(create)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        raise Http404

    def update(self, request, pk=None):
        serialized = WorkOrderUpdateSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            application = serialized.update(pk, request)
            serialized = WorkOrderUpdateSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404


class ServiceRequestApi(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = AdminPagination

    def get_queryset(self):
        if 'active' in self.request.query_params:
            queryset = ServiceRequest.objects.filter(Q(company=self.request.user.company) & Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0]))).order_by('-created_at')
        elif 'completed' in self.request.query_params:
            queryset = ServiceRequest.objects.filter(company=self.request.user.company, request_status=REPAIR_STATUS_OPTION[2][0]).order_by('-created_at')
        else:
            queryset = ServiceRequest.objects.filter(company=self.request.user.company).order_by('-created_at')
        return queryset

    def get_serializer_class(self):
        serializer = ServiceRequestSerializer
        if self.action == 'create':
            serializer = ServiceRequestSerializer
        elif self.action == 'update':
            serializer = UpdateServiceRequestSerializer
        elif self.action == 'list':
            serializer = ListServiceSerializer
        elif self.action == 'retrieve':
            serializer = UpdateServiceRequestSerializer
        return serializer

    def create(self, request, *args, **kwargs):
        serialized = ServiceRequestSerializer(data=request.data, context={'request': request, 'resolution_date': request.data['resolution_date']})
        if serialized.is_valid(raise_exception=True):
            create = serialized.create()
            serialized = ServiceRequestSerializer(create)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        raise Http404

    def update(self, request, pk=None):
        serialized = UpdateServiceRequestSerializer(data=request.data, context={'request': request, 'resolution_date': request.data['resolution_date']})
        if serialized.is_valid(raise_exception=True):
            application = serialized.update(pk)
            serialized = UpdateServiceRequestSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404

    @action(methods=['GET'], detail=False)
    def check_request(self, request):
        if 'bus_id' in request.GET:
            bus_no = request.GET['bus_id']
            if ServiceRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=bus_no).exists() or \
                    RepairRequest.objects.filter(Q(Q(request_status=REPAIR_STATUS_OPTION[0][0]) | Q(request_status=REPAIR_STATUS_OPTION[1][0])), bus=bus_no).exists():
                return Response(False, status=status.HTTP_200_OK)
            return Response(True, status=status.HTTP_200_OK)


class ManufacturerApi(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ManufacturerSerializer
    queryset = Manufacturer.objects.filter(enable=True)
    pagination_class = None


class PendingRepairRequestApi(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RepairRequestSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = RepairRequest.objects.filter(request_status=REPAIR_STATUS_OPTION[0][0], company=self.request.user.company)
        return queryset


class PendingServiceRequestApi(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ListServiceSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = ServiceRequest.objects.filter(request_status=REPAIR_STATUS_OPTION[0][0], company=self.request.user.company)
        return queryset


class WorkOrderListAPI(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    serializer_class = WorkOrderListSerializer

    def get_queryset(self):
        queryset = WorkOrderManagement.objects.filter(Q(order_status=ORDER_STATUS[0][0]) | Q(order_status=ORDER_STATUS[2][0]), company=self.request.user.company).order_by('-created_at')
        return queryset


class GraphOrderApi(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    serializer_class = GraphOrderSerializer

    def get_queryset(self):
        store = []
        queryset = WorkOrderManagement.objects.filter(company=self.request.user.company)
        total = queryset.count()
        progress = queryset.filter(order_status=ORDER_STATUS[0][0]).count()
        resolve = queryset.filter(order_status=ORDER_STATUS[1][0]).count()
        hold = queryset.filter(order_status=ORDER_STATUS[2][0]).count()
        store.append({'total': total, 'progress':progress, 'hold':hold, 'resolve': resolve})
        return store


class GraphServiceApi(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    serializer_class = GraphOrderSerializer

    def get_queryset(self):
        store = []
        queryset = ServiceRequest.objects.filter(company=self.request.user.company)
        total = queryset.count()
        pending = queryset.filter(request_status=REPAIR_STATUS_OPTION[0][0]).count()
        progress = queryset.filter(request_status=REPAIR_STATUS_OPTION[1][0]).count()
        resolve = queryset.filter(request_status=REPAIR_STATUS_OPTION[2][0]).count()
        store.append({'total': total, 'pending': pending, 'progress': progress, 'resolve': resolve})
        return store


class MainDashboardorderApi(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = WorkOrderListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DashboardPagination

    def get_queryset(self):
        queryset = WorkOrderManagement.objects.filter(company=self.request.user.company).order_by('-created_at')
        return queryset


class RolesAndPermissionApi(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        serializer = RolesAndPermissionSerializer
        if self.action == 'list':
            serializer = RolesAndPermissionListSerializer
        elif self.action == 'update':
            serializer = RolesAndPermissionUpdateSerializer
        return serializer

    def get_queryset(self):
        if 'department' in self.request.query_params:
            queryset = Designation.objects.filter(company=self.request.user.company,
                                                  department=self.request.query_params['department'])
        else:
            queryset = Designation.objects.filter(company=self.request.user.company)
        return queryset

    def update(self, request, pk=None):
        designation = Designation.objects.filter(id=pk).first()
        if not designation:
            raise Http404
        if 'main_dashboard' in request.data:
            designation.main_dashboard = True if request.data['main_dashboard'] == 'true' else False
        elif 'bus_management' in request.data:
            designation.bus_management = True if request.data['bus_management'] == 'true' else False
        elif 'repair_request' in request.data:
            designation.repair_request = True if request.data['repair_request'] == 'true' else False
        elif 'man_management' in request.data:
            designation.man_management = True if request.data['man_management'] == 'true' else False
        elif 'work_management' in request.data:
            designation.work_management = True if request.data['work_management'] == 'true' else False
        elif 'service_request' in request.data:
            designation.service_request = True if request.data['service_request'] == 'true' else False
        elif 'user_admin_management' in request.data:
            designation.user_admin_management = True if request.data['user_admin_management'] == 'true' else False
        elif 'work_show' in request.data:
            designation.work_show = True if request.data['work_show'] == 'true' else False
        elif 'bus_edit' in request.data:
            designation.bus_edit = True if request.data['bus_edit'] == 'true' else False
        elif 'email_rr' in request.data:
            designation.email_rr = True if request.data['email_rr'] == 'true' else False
        designation.save()
        return Response(status=201)


class UserEditApi(viewsets.GenericViewSet):
    serializer_class = UserEditSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(email=self.request.user.email)

    @action(methods=['PUT'], detail=False)
    def update_profile(self, request):
        serialized = UserEditSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            application = serialized.update()
            serialized = UserEditSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404

    @action(methods=['PUT'], detail=False)
    def edit(self, request):
        serialized = UserEditSerializer(data=request.data, context={'request': request})
        if serialized.is_valid(raise_exception=True):
            application = serialized.edit()
            serialized = UserEditSerializer(application)
            return Response(serialized.data, status=201)
        raise Http404


