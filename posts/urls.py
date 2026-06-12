from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.post_list_view, name='list'),
    path('create/', views.post_create_view, name='create'),
    path('<int:pk>/', views.post_detail_view, name='detail'),
    path('<int:pk>/delete/', views.delete_post_view, name='delete'),
    path('<int:post_pk>/comment/', views.add_comment_view, name='add_comment'),
    path('<int:pk>/vote/', views.vote_post_view, name='vote'),
]
