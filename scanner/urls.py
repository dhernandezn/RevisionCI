from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('prohibidos/', views.listar_prohibidos, name='listar_prohibidos'),
    path('prohibidos/agregar/', views.agregar_prohibido, name='agregar_prohibido'),
    path('prohibidos/editar/<int:pk>/', views.editar_prohibido, name='editar_prohibido'),
    path('prohibidos/eliminar/<int:pk>/', views.eliminar_prohibido, name='eliminar_prohibido'),
]
