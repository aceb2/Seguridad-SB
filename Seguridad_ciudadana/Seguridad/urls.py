from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('agregar/', views.agregar_alerta, name='Agregar-alerta'),
    path('rutas/',views.listar_rutas, name='Listar-ruta'),
    path('agregar-ruta/', views.agregar_ruta, name='agregar-ruta'),
    path('rutas/json/', views.obtener_rutas_json, name='rutas-json'),
    path('agregar-ruta/', views.agregar_ruta_view, name='agregar-ruta'),
]