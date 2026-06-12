from django.urls import path
from . import views

app_name = 'communities'

urlpatterns = [
    path('', views.community_list_view, name='list'),
    path('create/', views.community_create_view, name='create'),
    path('<slug:slug>/', views.community_detail_view, name='detail'),
    path('<slug:slug>/join/', views.join_community_view, name='join'),
]
