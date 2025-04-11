from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_page, name="chat"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    # path('chat/', views.chat_view, name='chat'),
    path('clear/', views.clear_chat, name='clear_chat'),
    
]
