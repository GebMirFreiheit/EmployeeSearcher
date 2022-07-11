from django import forms

from .models import Employee

class EmployeeForm(forms.Form):
    branch_office = forms.CharField(max_length=100, widget=forms.TextInput(),label='Филиал')
    fio = forms.CharField(max_length=100, widget=forms.TextInput(),label='ФИО')
    position = forms.CharField(max_length=100, widget=forms.TextInput(),label='Должность')
    birthday = forms.DateField(widget=forms.DateInput(format=('%d.%m.%Y'),attrs={'class': 'form-control', 
               'placeholder': 'Select a date',
               'type': 'date'
              }),label='Дата рождения')
    hire_day = forms.DateField(widget=forms.DateInput(format=('%d.%m.%Y'),attrs={'class': 'form-control', 
               'placeholder': 'Select a date',
               'type': 'date'
              }),label='Дата приема на работу')
    salary = forms.IntegerField(widget=forms.NumberInput(),label='Зарплата')

    class Meta:
        model = Employee
        fields = ['branch_office','fio','position','birthday','hire_day','salary']

    def save(self):
        employee = Employee(branch_office=self.cleaned_data['branch_office'],fio=self.cleaned_data['fio'],position=self.cleaned_data['position'],
            birthday=self.cleaned_data['birthday'],hire_day=self.cleaned_data['hire_day'],salary=self.cleaned_data['salary'])
        employee.save()