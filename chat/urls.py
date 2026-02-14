from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:thread_id>/', views.chat_room, name='chat_room'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('<int:thread_id>/upload_media/', views.upload_chat_media, name='upload_media'),
]
