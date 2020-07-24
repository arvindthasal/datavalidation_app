from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage,name="Homepage"),
     path('file_upload', views.file_upload,name="file_upload"),
     path('validate',views.validateExcel,name="validateExcel"),
  
]