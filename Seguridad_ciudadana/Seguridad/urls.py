from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.iniciar_sesion, name='login'),
    path('registro/', views.registrar, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),
    
    # Dashboards según rol
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('operador/dashboard/', views.operador_dashboard, name='operador_dashboard'),
    path('conductor/dashboard/', views.conductor_dashboard, name='conductor_dashboard'),
    path('civil/dashboard/', views.civil_dashboard, name='civil_dashboard'),
    
    # Denuncias
    path('denuncias/', views.listar_denuncias, name='listar_denuncias'),
    path('denuncias/crear/', views.crear_denuncia, name='crear_denuncia'),
    
    # Placeholders para alertas y rutas (comentados hasta que crees los modelos)
    path('alertas/', views.listar_alertas, name='listar_alertas'),
    path('alertas/agregar/', views.agregar_alerta, name='agregar_alerta'),
    path('rutas/', views.listar_rutas, name='listar_rutas'),
    path('rutas/agregar/', views.agregar_ruta_view, name='agregar_ruta'),
    path('clear-alert/', views.clear_alert, name='clear_alert'),
]