from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from io import BytesIO
import pandas as pd
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from .forms import EmployeeForm
from .models import Employee

# Create your views here.
def search_employees(request):
    position = request.GET.get('position_title')
    branch_office = request.GET.get('branch_office_title')
    if position and branch_office:
        employees = Employee.objects.filter(Q(position=position) & Q(branch_office=branch_office)).order_by('-id')
    elif position:
        employees = Employee.objects.filter(position=position).order_by('-id')
    elif branch_office:
        employees = Employee.objects.filter(branch_office=branch_office).order_by('-id')
    else:
        employees = Employee.objects.all().order_by('-id')
    paginator = Paginator(employees, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'search_employees.html',{'page_obj': page_obj})

def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('search')
        else:
            print(form.errors)
            return HttpResponse(form.errors,400)
    else:
        form = EmployeeForm()
        return render(request,'add_employee.html',{'form':form})

def change_employee(request,emp_id):
    emp = get_object_or_404(Employee,pk=emp_id)
    if request.method == 'POST':
        form = EmployeeForm(data=request.POST)
        if form.is_valid():
            form.save_changed(emp=emp)
            return redirect('search')
        else:
            print(form.errors)
            return HttpResponse(form.errors,400)
    else:
        form = EmployeeForm(initial={'branch_office':emp.branch_office,'fio':emp.fio,'position':emp.position,'birthday':str(emp.birthday),'hire_day':str(emp.hire_day),
            'salary':emp.salary})
        return render(request,'change_employee.html',{'form':form})

def delete_employee(request):
    emp_id = request.GET.get('emp')
    if not emp_id:
        return HttpResponse(content='Нужен параметр emp (id сотрудника)',status=400)
    emp = get_object_or_404(Employee,pk=emp_id)
    emp.delete()
    return HttpResponse(content='Сотрудник был успешно удален',status=200)

def download_excel(request):
    d = Employee.objects.all().values()
    df = pd.DataFrame(data=d)
    df = df.rename(columns={'branch_office':'Филиал','fio':'ФИО','position':'Должность','birthday':'Дата рождения','hire_day':'Дата приема на работу',
        'salary':'Зарплата'})
    excel_file = BytesIO()

    xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(xlwriter, index=False)
    xlwriter.save()

    excel_file.seek(0)

    response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employees.xlsx'

    return response

def create_google_sheet(request):
    employees = Employee.objects.all().values()
    row_amount = len(employees)+1
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

    spreadsheet = service.spreadsheets().create(body = {
        'properties': {'title': 'Сотрудники', 'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                'sheetId': 0,
                                'title': 'Лист1',
                                'gridProperties': {'rowCount': row_amount, 'columnCount': 7}}}]
    }).execute()

    print(spreadsheet['spreadsheetUrl'])

    driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth)
    shareRes = driveService.permissions().create(
        fileId = spreadsheet['spreadsheetId'],
        body = {'type': 'anyone', 'role': 'reader'},  # доступ на чтение по ссылке
        fields = 'id'
    ).execute()

    data = [{"range": "Лист1!A1:G1",
            "values": [['id','Филиал','ФИО','Должность','Дата рождения','Дата приема на работу','Зарплата']]}]
    for i in range(2,row_amount+1):
        data.append({"range": f"Лист1!A{i}:G{i}","majorDimension": "ROWS","values": [[employees[i-2]['id'],employees[i-2]['branch_office'],employees[i-2]['fio'],
            employees[i-2]['position'],str(employees[i-2]['birthday']),str(employees[i-2]['hire_day']),employees[i-2]['salary']]]})
    results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheet['spreadsheetId'], body = {
        "valueInputOption": "USER_ENTERED",
        "data": data
    }).execute()

    return HttpResponse(status=200,content='Таблица создана по ссылке '+spreadsheet['spreadsheetUrl'])
