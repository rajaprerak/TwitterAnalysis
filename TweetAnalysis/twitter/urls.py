from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies, name='movies'),
    path('songs/', views.songs, name='songs'),
    path('autoscaling/', views.autoscaling, name='autoscaling'),
    path('send_mail/', views.send_mail_to_user, name='send_mail')
]