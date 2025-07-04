"""
URL configuration for Restaurant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path
from django.conf.urls.static import static

from django.conf import settings
import os

from Restaurant.settings import BASE_DIR

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Accountapp/', include('Accountapp.urls')),
    path('Adminapp/', include('Adminapp.urls')),
    path('Managerapp/', include('Managerapp.urls')),
    path('Waiterapp/', include('Waiterapp.urls')),
    path('Kitchenapp/', include('Kitchenapp.urls')),
    path('Userapp/', include('Userapp.urls')),
    path('Deliveryboyapp/', include('Deliveryboyapp.urls')),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
