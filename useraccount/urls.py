from django.urls import path
from . import views


app_name='user'
urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('users/', views.userlist, name="userlist"),
    path('edit-users/<int:pk>/', views.useredit, name="edituser"),
    path('login/', views.userlogin, name="login"),
    path('logout/', views.userlogout, name="logout"),
]