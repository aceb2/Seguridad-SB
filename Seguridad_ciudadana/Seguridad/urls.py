from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.iniciar_sesion, name='login'),
    path('Logout/', views.cerrar_sesion, name='logout'),
    path('Home/', views.index, name='index'),
    path('Admin/', views.admin_dashboard, name='Admin'),
    path('Admin/requerimientos/', views.admin_requerimientos, name='admin_requerimientos'),
    path('Admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    
    # APIs para requerimientos
    path('api/requerimientos/', views.api_requerimientos, name='api_requerimientos'),
    path('api/requerimientos/<int:requerimiento_id>/', views.api_requerimiento_detalle, name='api_requerimiento_detalle'),
    path('api/requerimientos/<int:requerimiento_id>/ruta/', views.api_requerimiento_ruta_completa, name='api_requerimiento_ruta_completa'),
    
    # APIs para familias, grupos, subgrupos
    path('api/familias/', views.api_familias, name='api_familias'),
    path('api/familias/<int:familia_id>/', views.api_familia_detalle, name='api_familia_detalle'),
    path('api/grupos/', views.api_grupos, name='api_grupos'),
    path('api/grupos/<int:grupo_id>/', views.api_grupo_detalle, name='api_grupo_detalle'),
    path('api/subgrupos/', views.api_subgrupos, name='api_subgrupos'),
    path('api/subgrupos/<int:subgrupo_id>/', views.api_subgrupo_detalle, name='api_subgrupo_detalle'),
    
    # APIs para usuarios
    path('api/usuarios/', views.api_usuarios, name='api_usuarios'),
    path('api/usuarios/buscar/', views.api_usuarios_buscar, name='api_usuarios_buscar'),
    path('api/usuarios/<int:usuario_id>/', views.api_usuario_detalle, name='api_usuario_detalle'),
    
        # ========== NUEVAS APIs PARA IONIC ==========
    path('ionic/login/', views.api_login_ionic, name='api_login_ionic'),
    path('ionic/register/', views.api_register_ciudadano, name='api_register_ciudadano'),
    path('ionic/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('ionic/vehiculos/', views.api_vehiculos, name='api_vehiculos'),
    path('ionic/tipos-vehiculos/', views.api_tipos_vehiculos, name='api_tipos_vehiculos'),
    path('ionic/denuncias/', views.api_denuncias_ionic, name='api_denuncias_ionic'),
    path('ionic/roles/', views.api_roles_ionic, name='api_roles_ionic'),
    path('ionic/turnos/', views.api_turnos_ionic, name='api_turnos_ionic'),
]
