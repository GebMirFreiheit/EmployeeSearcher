from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('search',views.search_employees,name='search'),
    path('add_employee',views.add_employee,name='add_employee'),
    path('change_employee/<int:emp_id>',views.change_employee,name='change_employee'),
    path('delete_employee',views.delete_employee,name='delete_employee'),
    path('download_excel',views.download_excel,name='download_excel')
]