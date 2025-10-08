from django.urls import path
from . import views

urlpatterns = [
    path('controles/<int:nino_id>/', views.controles, name='controles'),
]