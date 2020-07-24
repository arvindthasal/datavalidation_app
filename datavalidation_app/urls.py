from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index,name="Index"),
    path('',include('datafile.urls')),
    path('file_upload',include('datafile.urls')),
    path('validate',include('datafile.urls')) , 
]

