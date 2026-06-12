from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('search/', views.search_view, name='search'),
    path('health/', views.health_check_view, name='health'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]