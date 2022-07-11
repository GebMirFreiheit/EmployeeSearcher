from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import EmployeeForm
from .models import Employee

# Create your views here.
def search_employees(request):
    employees = Employee.objects.all().order_by('-id')
    # print(employees)
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
