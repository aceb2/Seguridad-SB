from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.iniciar_sesion, name='login'),
    path('Logout/', views.cerrar_sesion, name='logout'),
    path('Home/', views.index, name='index'),
    path('Registro/', views.registrar, name='registro'),
    path('Admin/', views.admin_dashboard, name='Admin'),
    path('Admin/requerimientos/', views.admin_requerimientos, name='admin_requerimientos'),
    
    # APIs para requerimientos
    path('api/familias/', views.api_familias, name='api_familias'),
    path('api/grupos/', views.api_grupos, name='api_grupos'),
    path('api/subgrupos/', views.api_subgrupos, name='api_subgrupos'),
    path('api/requerimientos/', views.api_requerimientos, name='api_requerimientos'),
    

]