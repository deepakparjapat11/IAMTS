"""IAMTS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'IAMTS'
admin.site.site_title = "IAMTS"
admin.site.index_title = 'Welcome to IAMTS Admin Portal'
urlpatterns = [
    path('', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path(r'accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path(r'accounts/reset/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('base/', TemplateView.as_view(template_name='base.html')),
    path('api/docs/', include_docs_urls(title="IAMTS Api", permission_classes=(AllowAny,),)),
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'accounts.views.error_404_view'