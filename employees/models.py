from django.db import models

# Create your models here.
class Employee(models.Model):
    branch_office = models.CharField(max_length=100, verbose_name='Филиал')
    fio = models.CharField(max_length=100, verbose_name='ФИО')
    position = models.CharField(max_length=100, verbose_name='Должность')
    birthday = models.DateField(verbose_name='Дата рождения')
    hire_day = models.DateField(verbose_name='Дата приема на работу')
    salary = models.IntegerField(verbose_name='Зарплата')