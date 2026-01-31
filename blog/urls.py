from django.urls import path, re_path
from blog import views

urlpatterns = [
    path('', views.index),
    path('about/', views.about, kwargs={'name': 'Tom', 'age': 38}),
    re_path(r'^contact/', views.contact),
    re_path(r'^user/(?P<name>\D+)/(?P<age>\d+)/', views.user),
]
