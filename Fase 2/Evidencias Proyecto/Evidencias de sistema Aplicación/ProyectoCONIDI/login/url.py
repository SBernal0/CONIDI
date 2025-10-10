from django.urls import path
from . import views


urlpatterns = [
    
    path('', views.login_user, name='login'),  # raíz ahora es login
    path('home/', views.home, name='home'), 
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('logout/', views.logout_user, name='logout'),
    path('cambiar-clave/', views.cambiar_clave, name='cambiar_clave'),  #este e s pa cambiar el password de forma manual
    path('cambiar_clave_temporal/', views.cambiar_clave_temporal, name='cambiar_clave_temporal'),


]