from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('vote/', views.VoteView.as_view(), name='vote'),
    path('create/<int:pk>', views.create, name='create'),
    path('seal', views.seal, name='seal'),
    path('verify', views.verify, name='verify'),
    path('results', views.result, name='result'),
]