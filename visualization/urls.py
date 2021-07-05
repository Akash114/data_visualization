from django.urls import path,include
from . import views
from django.conf.urls import url


urlpatterns = [
    path('',views.home),
    url('columns',views.get_columns,name='columns'),
    url('visualize',views.visualize,name='visualize'),
    url('two_variables',views.two_variables,name='two_variables'),
]
