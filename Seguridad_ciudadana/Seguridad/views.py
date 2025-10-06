from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import login, authenticate, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.http import JsonResponse # type: ignore
from django.utils import timezone # type: ignore
from .models import FamiliaDenuncia, GrupoDenuncia, Requerimiento, SubgrupoDenuncia, Usuario, Denuncia, Vehiculos, AsignacionesVehiculos, Roles, Turnos
from django.views.decorators.csrf import csrf_exempt # type: ignore
import json

# Vistas básicas de autenticación
@login_required
def index(request):
    # ✅ OBTENER DATOS SIN ELIMINARLOS (no usar pop)
    usuario_nombre = request.session.get('usuario_nombre', '')
    mostrar_bienvenida = request.session.get('mostrar_bienvenida', False)
    
    # ✅ LIMPIAR LA BANDERA DESPUÉS DE USARLA
    if 'mostrar_bienvenida' in request.session:
        del request.session['mostrar_bienvenida']
    
    context = {
        'usuario_nombre': usuario_nombre,
        'mostrar_bienvenida': mostrar_bienvenida
    }
    
    return render(request, 'index.html', context)

@login_required
def cerrar_sesion(request):
    """Cerrar sesión de forma segura"""
    try:
        usuario_info = {
            'nombre': f"{request.user.nombre_usuario} {request.user.apellido_pat_usuario}",
            'rol': request.user.id_rol.nombre_rol
        }
        
        # ✅ Cerrar sesión
        logout(request)
        
        request.session.flush()
        
        request.session['alert_type'] = 'info'
        request.session['alert_title'] = 'Sesión Cerrada'
        request.session['alert_message'] = f'Hasta pronto, {usuario_info["nombre"]}! 👋'
        
        return redirect('login')
        
    except Exception as e:
        
        return redirect('login')
    
def iniciar_sesion(request):
    if request.method == 'POST':
        correo_electronico_usuario = request.POST.get('correo_electronico_usuario')
        password = request.POST.get('password')
        user = authenticate(request, username=correo_electronico_usuario, password=password)
        
        if user is not None:
            if user.es_administrador or user.es_operador:
                login(request, user)
            
                # ✅ MENSAJE PERSONALIZADO POR ROL
                rol_mensaje = "Administrador" if user.es_administrador else "Operador"
                request.session['usuario_nombre'] = f'{user.nombre_usuario} {user.apellido_pat_usuario}'
                request.session['usuario_rol'] = rol_mensaje
                request.session['mostrar_bienvenida'] = True
            
                return redirect('index')
            else:
                # ❌ Acceso denegado - mostrar en login
                request.session['alert_type'] = 'error'
                request.session['alert_title'] = 'Acceso Denegado 🔒'
                request.session['alert_message'] = 'Solo personal autorizado puede acceder al sistema.'
                return redirect('login')
        else:
            # ❌ Credenciales inválidas - mostrar en login
            request.session['alert_type'] = 'error'
            request.session['alert_title'] = 'Error de Login ❌'
            request.session['alert_message'] = 'Credenciales inválidas. Verifique su correo y contraseña.'
            return redirect('login')
    
    # Manejar alertas en el login
    alert_type = request.session.pop('alert_type', None)
    alert_title = request.session.pop('alert_title', None) 
    alert_message = request.session.pop('alert_message', None)
    
    context = {
        'alert_type': alert_type,
        'alert_title': alert_title,
        'alert_message': alert_message
    }
    
    return render(request, 'Usuario/Inicio.html', context)

def clear_alert(request):
    """Limpiar alertas de la sesión"""
    if 'alert_type' in request.session:
        del request.session['alert_type']
        del request.session['alert_title'] 
        del request.session['alert_message']
        request.session.modified = True
    return JsonResponse({'status': 'success'})

def registrar(request):
    if request.method == 'POST':
        # Aquí iría la lógica de registro
        # Por ahora redirigimos al login
        return redirect('login')
    return render(request, 'registro.html')

# Vistas de dashboard según rol
@login_required
def admin_dashboard(request):
    if not request.user.es_administrador:
        return redirect('index')
    
    total_usuarios = Usuario.objects.count()
    total_denuncias = Denuncia.objects.count()
    vehiculos_activos = Vehiculos.objects.filter(estado_vehiculo='Disponible').count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_denuncias': total_denuncias,
        'vehiculos_activos': vehiculos_activos,
    }
    return render(request, 'Usuario/Admin.html', context)

# Vista para la página de administración
def admin_requerimientos(request):
    """Página principal de gestión de requerimientos"""
    if not request.user.is_authenticated or not request.user.es_administrador:
        return redirect('login')
    
    # Obtener todos los datos para mostrar
    familias = FamiliaDenuncia.objects.all()
    grupos = GrupoDenuncia.objects.all()
    subgrupos = SubgrupoDenuncia.objects.all()
    requerimientos = Requerimiento.objects.all()
    
    context = {
        'familias': familias,
        'grupos': grupos,
        'subgrupos': subgrupos,
        'requerimientos': requerimientos,
    }
    return render(request, 'CRUD/Admin/requerimientos.html', context)

# API para gestionar familias
@csrf_exempt
def api_familias(request):
    if request.method == 'GET':
        try:
            familias = list(FamiliaDenuncia.objects.values('id_familia_denuncia', 'nombre_familia_denuncia'))
            return JsonResponse(familias, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            
            if FamiliaDenuncia.objects.filter(nombre_familia_denuncia=nombre).exists():
                return JsonResponse({'error': 'La familia ya existe'}, status=400)
            
            # Obtener el último ID para generar uno nuevo
            ultima_familia = FamiliaDenuncia.objects.order_by('-id_familia_denuncia').first()
            nuevo_id = ultima_familia.id_familia_denuncia + 1 if ultima_familia else 1
            
            familia = FamiliaDenuncia.objects.create(
                id_familia_denuncia=nuevo_id,
                nombre_familia_denuncia=nombre,
                codigo_familia=nombre[:3].upper() + str(nuevo_id).zfill(3)
            )
            return JsonResponse({
                'id': familia.id_familia_denuncia, 
                'nombre': familia.nombre_familia_denuncia
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# API para gestionar grupos
@csrf_exempt
def api_grupos(request):
    if request.method == 'GET':
        try:
            familia_id = request.GET.get('familia_id')
            if familia_id:
                grupos = list(GrupoDenuncia.objects.filter(
                    id_familia_denuncia_id=familia_id
                ).values('id_grupo_denuncia', 'nombre_grupo_denuncia'))
            else:
                grupos = list(GrupoDenuncia.objects.values('id_grupo_denuncia', 'nombre_grupo_denuncia', 'id_familia_denuncia_id'))
            return JsonResponse(grupos, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            familia_id = data.get('familia_id')
            
            # Obtener el último ID para generar uno nuevo
            ultimo_grupo = GrupoDenuncia.objects.order_by('-id_grupo_denuncia').first()
            nuevo_id = ultimo_grupo.id_grupo_denuncia + 1 if ultimo_grupo else 1
            
            grupo = GrupoDenuncia.objects.create(
                id_grupo_denuncia=nuevo_id,
                nombre_grupo_denuncia=nombre,
                id_familia_denuncia_id=familia_id,
                codigo_grupo=nombre[:3].upper() + str(nuevo_id).zfill(3)
            )
            return JsonResponse({
                'id': grupo.id_grupo_denuncia, 
                'nombre': grupo.nombre_grupo_denuncia
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# API para gestionar subgrupos
@csrf_exempt
def api_subgrupos(request):
    if request.method == 'GET':
        try:
            grupo_id = request.GET.get('grupo_id')
            if grupo_id:
                subgrupos = list(SubgrupoDenuncia.objects.filter(
                    id_grupo_denuncia_id=grupo_id
                ).values('id_subgrupo_denuncia', 'nombre_subgrupo_denuncia'))
            else:
                subgrupos = list(SubgrupoDenuncia.objects.values('id_subgrupo_denuncia', 'nombre_subgrupo_denuncia', 'id_grupo_denuncia_id'))
            return JsonResponse(subgrupos, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            grupo_id = data.get('grupo_id')
            
            # Obtener el último ID para generar uno nuevo
            ultimo_subgrupo = SubgrupoDenuncia.objects.order_by('-id_subgrupo_denuncia').first()
            nuevo_id = ultimo_subgrupo.id_subgrupo_denuncia + 1 if ultimo_subgrupo else 1
            
            subgrupo = SubgrupoDenuncia.objects.create(
                id_subgrupo_denuncia=nuevo_id,
                nombre_subgrupo_denuncia=nombre,
                id_grupo_denuncia_id=grupo_id,
                codigo_subgrupo=nombre[:3].upper() + str(nuevo_id).zfill(3)
            )
            return JsonResponse({
                'id': subgrupo.id_subgrupo_denuncia, 
                'nombre': subgrupo.nombre_subgrupo_denuncia
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# API para gestionar requerimientos
@csrf_exempt
def api_requerimientos(request):
    if request.method == 'GET':
        try:
            subgrupo_id = request.GET.get('subgrupo_id')
            if subgrupo_id:
                requerimientos = list(Requerimiento.objects.filter(
                    id_subgrupo_denuncia_id=subgrupo_id
                ).values('id_requerimiento', 'nombre_requerimiento', 'clasificacion_requerimiento'))
            else:
                requerimientos = list(Requerimiento.objects.values(
                    'id_requerimiento', 'nombre_requerimiento', 'clasificacion_requerimiento', 'id_subgrupo_denuncia_id'
                ))
            return JsonResponse(requerimientos, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            subgrupo_id = data.get('subgrupo_id')
            clasificacion = data.get('clasificacion', 'Media')
            descripcion = data.get('descripcion', '')
            
            # Obtener el último ID para generar uno nuevo
            ultimo_requerimiento = Requerimiento.objects.order_by('-id_requerimiento').first()
            nuevo_id = ultimo_requerimiento.id_requerimiento + 1 if ultimo_requerimiento else 1
            
            requerimiento = Requerimiento.objects.create(
                id_requerimiento=nuevo_id,
                nombre_requerimiento=nombre,
                id_subgrupo_denuncia_id=subgrupo_id,
                clasificacion_requerimiento=clasificacion,
                descripcion_requerimiento=descripcion,
                codigo_requerimiento=nombre[:3].upper() + str(nuevo_id).zfill(3)
            )
            return JsonResponse({
                'id': requerimiento.id_requerimiento, 
                'nombre': requerimiento.nombre_requerimiento,
                'clasificacion': requerimiento.clasificacion_requerimiento
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)