from django.urls import path
from . import views

urlpatterns = [
    path('search',views.search_employees,name='search'),
    path('add_employee',views.add_employee,name='add_employee')
]