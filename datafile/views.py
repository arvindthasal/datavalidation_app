from django.shortcuts import render,redirect
from django.http import HttpResponse
import pathlib
import openpyxl
from collections import OrderedDict
from . models import Exceldata
from .resources import ExceldataResource
from django.contrib import messages
from tablib import Dataset
import os


def homepage(request):
   
    return redirect(file_upload)
    

# This function is used for rule calculation on uploaded excel data 
def get_validated_data():
    result = Exceldata.get_excelvalidate_data()
    data = []
    for value in result:
        data_set = {}
        data_set['country'] = value.country
        data_set['bevarage_type'] = value.bevarage_type
        data_set['category'] = value.category
        data_set['total_volume'] = value.total_volume
        data_set['total_value'] = round(value.total_value, 2)
        data_set['unit_price'] = value.unit_price
        data_set['volume_share'] = round(
            (value.total_volume/value.total_vol)*100)
        data_set['check_value'] = round(
            data_set['total_volume'] * data_set['unit_price'], 2)
        data_set['rule1'] = 1 if data_set['volume_share'] <= 50 else 0 #Rule-1:for validation of volume more than 50%
        data_set['rule2'] = 1 if data_set['check_value'] == data_set['total_value'] else 0 #Rule-2:for validation of category value
        data_set['error_color'] = "errorrow" if (data_set['rule1'] + data_set['rule2'])!=2 else ""
        data.append(data_set)

    return data
# This function is used to list of error rows
def get_error_rows():
    result = Exceldata.get_excelvalidate_data()
    data = []
    i=0
    for value in result:
        data_set = {}
        i+=1
#rows having both errors Rule-1&Rule-2
        if round((value.total_volume/value.total_vol)*100) >50 and round(value.total_volume * value.unit_price, 2)!=value.total_value:
            data_set['error_row']="Row  : " + str(i) +"->  Rule-1 ,Rule-2"
            data.append(data_set)
#rows having Rule-2 error
        elif  round(value.total_volume * value.unit_price, 2) != value.total_value :
            data_set['error_row']="Row  : " + str(i) +"->  Rule-2"
            data.append(data_set)
#rows having Rule-1 error
        elif round((value.total_volume/value.total_vol)*100) >50 :
            data_set['error_row']="Row  : " + str(i) +"->  Rule-1"
            data.append(data_set)
        
    return data



def validateExcel(request):
    data = get_validated_data()
    exceldata_resource = ExceldataResource()
    dataset = exceldata_resource.export()
    response = HttpResponse(
        dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="datavalidation.xls"'
    return response

#This function is used for excel upload and display
def file_upload(request):
    if request.method == "GET":
        return render(request, 'upload.html')
    else:
        Exceldata.objects.all().delete()
        new_exceldata = request.FILES['data_file']
        file_ext = os.path.splitext(str(new_exceldata))
        cell_error_counter = 0
        #Check valid file extension
        if not file_ext[1] in ['.xlsx']:
            messages.error(
                request, " File type is not supported.Please upload .xlsx file...")

        else:

            dataset = Dataset()
            imported_data = dataset.load(new_exceldata.read())
            wb = openpyxl.load_workbook(new_exceldata)
            worksheet = wb.worksheets[0]
            row_count = worksheet.max_row
            
#Check for Blank excel sheet
            if row_count-1 == 0:
                messages.error(request, "Blank Excel sheet is uploaded..")
#Check for Blank Columns or Cell values
            for id, data in enumerate(imported_data):
                if data.count(None) != 0 and data.count(None) < len(data):
                    cell_error_counter += 1
                    messages.error(request, "Some Columns or Cell values may be blank ,Please check the excel rows at : " +
                                   str(id+2))

                else:
                    try:
                        value = Exceldata(
                            id,
                            data[0],
                            data[1],
                            data[2],
                            data[3],
                            data[4],
                            data[5],
                        )
                        value.save()
                    except:
                        messages.error(
                            request, "There is some issues in cell values type.Please check the excel rows at :" +
                            str(id+2))
                        cell_error_counter += 1
#if found some errors is excel then remove the saved records
        if cell_error_counter != 0:
            Exceldata.objects.all().delete()
#Fetch file data and error list for display
    data = get_validated_data()
    error_list=get_error_rows()
    return render(request, 'upload.html', {'rows': data,'error_list':error_list})
