from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

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
