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

# ✅ API PARA FAMILIAS (COMPLETA - GET, POST, DELETE)
@csrf_exempt
def api_familias(request, familia_id=None):
    """Manejar operaciones CRUD para familias"""
    try:
        if request.method == 'GET':
            familias = FamiliaDenuncia.objects.all()
            data = []
            for familia in familias:
                data.append({
                    'id_familia_denuncia': familia.id_familia_denuncia,
                    'nombre_familia_denuncia': familia.nombre_familia_denuncia,
                    'codigo_familia': familia.codigo_familia
                })
            return JsonResponse(data, safe=False)
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            nombre = data.get('nombre')
            
            if not nombre:
                return JsonResponse({'error': 'El nombre es requerido'}, status=400)
            
            # Verificar si ya existe
            if FamiliaDenuncia.objects.filter(nombre_familia_denuncia=nombre).exists():
                return JsonResponse({'error': 'La familia ya existe'}, status=400)
            
            # Obtener el último ID
            ultima_familia = FamiliaDenuncia.objects.order_by('-id_familia_denuncia').first()
            nuevo_id = ultima_familia.id_familia_denuncia + 1 if ultima_familia else 1
            
            # Crear código
            codigo_familia = nombre[:3].upper() + str(nuevo_id).zfill(3)
            
            familia = FamiliaDenuncia.objects.create(
                id_familia_denuncia=nuevo_id,
                nombre_familia_denuncia=nombre,
                codigo_familia=codigo_familia
            )
            
            return JsonResponse({
                'id_familia_denuncia': familia.id_familia_denuncia,
                'nombre_familia_denuncia': familia.nombre_familia_denuncia,
                'codigo_familia': familia.codigo_familia
            })
            
    except Exception as e:
        print(f"❌ Error en api_familias: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA DETALLE DE FAMILIA (DELETE)
@csrf_exempt
def api_familia_detalle(request, familia_id):
    """Manejar operaciones CRUD para una familia específica"""
    try:
        familia = FamiliaDenuncia.objects.get(id_familia_denuncia=familia_id)
    except FamiliaDenuncia.DoesNotExist:
        return JsonResponse({'error': 'Familia no encontrada'}, status=404)
    
    if request.method == 'DELETE':
        try:
            # Verificar si hay grupos dependientes
            grupos_dependientes = GrupoDenuncia.objects.filter(id_familia_denuncia_id=familia_id)
            if grupos_dependientes.exists():
                return JsonResponse({
                    'error': 'No se puede eliminar la familia porque tiene grupos asociados. Elimine primero los grupos.'
                }, status=400)
            
            familia.delete()
            return JsonResponse({'mensaje': 'Familia eliminada correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA GRUPOS (COMPLETA - GET, POST, DELETE)
@csrf_exempt
def api_grupos(request, grupo_id=None):
    """Manejar operaciones CRUD para grupos"""
    try:
        if request.method == 'GET':
            familia_id = request.GET.get('familia_id')
            if familia_id:
                grupos = GrupoDenuncia.objects.filter(id_familia_denuncia_id=familia_id)
            else:
                grupos = GrupoDenuncia.objects.all()
            
            data = []
            for grupo in grupos:
                data.append({
                    'id_grupo_denuncia': grupo.id_grupo_denuncia,
                    'nombre_grupo_denuncia': grupo.nombre_grupo_denuncia,
                    'codigo_grupo': grupo.codigo_grupo,
                    'id_familia_denuncia': grupo.id_familia_denuncia_id
                })
            return JsonResponse(data, safe=False)
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            nombre = data.get('nombre')
            familia_id = data.get('familia_id')
            
            if not nombre or not familia_id:
                return JsonResponse({'error': 'Nombre y familia_id son requeridos'}, status=400)
            
            # Verificar que la familia existe
            try:
                familia = FamiliaDenuncia.objects.get(id_familia_denuncia=familia_id)
            except FamiliaDenuncia.DoesNotExist:
                return JsonResponse({'error': 'La familia especificada no existe'}, status=400)
            
            # Obtener el último ID
            ultimo_grupo = GrupoDenuncia.objects.order_by('-id_grupo_denuncia').first()
            nuevo_id = ultimo_grupo.id_grupo_denuncia + 1 if ultimo_grupo else 1
            
            # Crear código
            codigo_grupo = nombre[:3].upper() + str(nuevo_id).zfill(3)
            
            grupo = GrupoDenuncia.objects.create(
                id_grupo_denuncia=nuevo_id,
                nombre_grupo_denuncia=nombre,
                id_familia_denuncia_id=familia_id,
                codigo_grupo=codigo_grupo
            )
            
            return JsonResponse({
                'id_grupo_denuncia': grupo.id_grupo_denuncia,
                'nombre_grupo_denuncia': grupo.nombre_grupo_denuncia,
                'codigo_grupo': grupo.codigo_grupo,
                'id_familia_denuncia': grupo.id_familia_denuncia_id
            })
            
    except Exception as e:
        print(f"❌ Error en api_grupos: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA DETALLE DE GRUPO (DELETE)
@csrf_exempt
def api_grupo_detalle(request, grupo_id):
    """Manejar operaciones CRUD para un grupo específico"""
    try:
        grupo = GrupoDenuncia.objects.get(id_grupo_denuncia=grupo_id)
    except GrupoDenuncia.DoesNotExist:
        return JsonResponse({'error': 'Grupo no encontrado'}, status=404)
    
    if request.method == 'DELETE':
        try:
            # Verificar si hay subgrupos dependientes
            subgrupos_dependientes = SubgrupoDenuncia.objects.filter(id_grupo_denuncia_id=grupo_id)
            if subgrupos_dependientes.exists():
                return JsonResponse({
                    'error': 'No se puede eliminar el grupo porque tiene subgrupos asociados. Elimine primero los subgrupos.'
                }, status=400)
            
            grupo.delete()
            return JsonResponse({'mensaje': 'Grupo eliminado correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA SUBGRUPOS (COMPLETA - GET, POST, DELETE)
@csrf_exempt
def api_subgrupos(request, subgrupo_id=None):
    """Manejar operaciones CRUD para subgrupos"""
    try:
        if request.method == 'GET':
            grupo_id = request.GET.get('grupo_id')
            if grupo_id:
                subgrupos = SubgrupoDenuncia.objects.filter(id_grupo_denuncia_id=grupo_id)
            else:
                subgrupos = SubgrupoDenuncia.objects.all()
            
            data = []
            for subgrupo in subgrupos:
                data.append({
                    'id_subgrupo_denuncia': subgrupo.id_subgrupo_denuncia,
                    'nombre_subgrupo_denuncia': subgrupo.nombre_subgrupo_denuncia,
                    'codigo_subgrupo': subgrupo.codigo_subgrupo,
                    'id_grupo_denuncia': subgrupo.id_grupo_denuncia_id
                })
            return JsonResponse(data, safe=False)
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            nombre = data.get('nombre')
            grupo_id = data.get('grupo_id')
            
            if not nombre or not grupo_id:
                return JsonResponse({'error': 'Nombre y grupo_id son requeridos'}, status=400)
            
            # Verificar que el grupo existe
            try:
                grupo = GrupoDenuncia.objects.get(id_grupo_denuncia=grupo_id)
            except GrupoDenuncia.DoesNotExist:
                return JsonResponse({'error': 'El grupo especificado no existe'}, status=400)
            
            # Obtener el último ID para generar uno nuevo
            ultimo_subgrupo = SubgrupoDenuncia.objects.order_by('-id_subgrupo_denuncia').first()
            nuevo_id = ultimo_subgrupo.id_subgrupo_denuncia + 1 if ultimo_subgrupo else 1
            
            # Crear código único
            codigo_subgrupo = nombre[:3].upper() + str(nuevo_id).zfill(3)
            
            subgrupo = SubgrupoDenuncia.objects.create(
                id_subgrupo_denuncia=nuevo_id,
                nombre_subgrupo_denuncia=nombre,
                id_grupo_denuncia_id=grupo_id,
                codigo_subgrupo=codigo_subgrupo
            )
            
            return JsonResponse({
                'id_subgrupo_denuncia': subgrupo.id_subgrupo_denuncia, 
                'nombre_subgrupo_denuncia': subgrupo.nombre_subgrupo_denuncia,
                'codigo_subgrupo': subgrupo.codigo_subgrupo,
                'id_grupo_denuncia': subgrupo.id_grupo_denuncia_id
            })
            
    except Exception as e:
        print(f"❌ Error en api_subgrupos: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA DETALLE DE SUBGRUPO (DELETE)
@csrf_exempt
def api_subgrupo_detalle(request, subgrupo_id):
    """Manejar operaciones CRUD para un subgrupo específico"""
    try:
        subgrupo = SubgrupoDenuncia.objects.get(id_subgrupo_denuncia=subgrupo_id)
    except SubgrupoDenuncia.DoesNotExist:
        return JsonResponse({'error': 'Subgrupo no encontrado'}, status=404)
    
    if request.method == 'DELETE':
        try:
            # Verificar si hay requerimientos dependientes
            requerimientos_dependientes = Requerimiento.objects.filter(id_subgrupo_denuncia_id=subgrupo_id)
            if requerimientos_dependientes.exists():
                return JsonResponse({
                    'error': 'No se puede eliminar el subgrupo porque tiene requerimientos asociados. Elimine primero los requerimientos.'
                }, status=400)
            
            subgrupo.delete()
            return JsonResponse({'mensaje': 'Subgrupo eliminado correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA REQUERIMIENTOS (ACTUALIZADA CON JERARQUÍA COMPLETA)
@csrf_exempt
def api_requerimientos(request):
    """Listar y crear requerimientos CON INFORMACIÓN COMPLETA DE JERARQUÍA"""
    try:
        if request.method == 'GET':
            subgrupo_id = request.GET.get('subgrupo_id')
            if subgrupo_id:
                requerimientos = Requerimiento.objects.filter(id_subgrupo_denuncia_id=subgrupo_id)
            else:
                requerimientos = Requerimiento.objects.all()
            
            # ✅ INCLUIR INFORMACIÓN COMPLETA DE JERARQUÍA
            requerimientos = requerimientos.select_related(
                'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia'
            )
            
            data = []
            for req in requerimientos:
                # Obtener información de la jerarquía
                subgrupo = req.id_subgrupo_denuncia
                grupo = subgrupo.id_grupo_denuncia
                familia = grupo.id_familia_denuncia
                
                data.append({
                    'id_requerimiento': req.id_requerimiento,
                    'nombre_requerimiento': req.nombre_requerimiento,
                    'clasificacion_requerimiento': req.clasificacion_requerimiento,
                    'descripcion_requerimiento': req.descripcion_requerimiento,
                    'codigo_requerimiento': req.codigo_requerimiento,
                    'id_subgrupo_denuncia': req.id_subgrupo_denuncia_id,
                    # ✅ INFORMACIÓN COMPLETA DE JERARQUÍA
                    'familia_nombre': familia.nombre_familia_denuncia,
                    'familia_codigo': familia.codigo_familia,
                    'grupo_nombre': grupo.nombre_grupo_denuncia,
                    'grupo_codigo': grupo.codigo_grupo,
                    'subgrupo_nombre': subgrupo.nombre_subgrupo_denuncia,
                    'subgrupo_codigo': subgrupo.codigo_subgrupo
                })
            return JsonResponse(data, safe=False)
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            nombre = data.get('nombre')
            subgrupo_id = data.get('subgrupo_id')
            clasificacion = data.get('clasificacion', 'Media')
            descripcion = data.get('descripcion', '')
            
            if not nombre or not subgrupo_id:
                return JsonResponse({'error': 'Nombre y subgrupo_id son requeridos'}, status=400)
            
            # Verificar que el subgrupo existe
            try:
                subgrupo = SubgrupoDenuncia.objects.get(id_subgrupo_denuncia=subgrupo_id)
            except SubgrupoDenuncia.DoesNotExist:
                return JsonResponse({'error': 'El subgrupo especificado no existe'}, status=400)
            
            # Obtener el último ID
            ultimo_requerimiento = Requerimiento.objects.order_by('-id_requerimiento').first()
            nuevo_id = ultimo_requerimiento.id_requerimiento + 1 if ultimo_requerimiento else 1
            
            # Crear código
            codigo_requerimiento = nombre[:3].upper() + str(nuevo_id).zfill(3)
            
            requerimiento = Requerimiento.objects.create(
                id_requerimiento=nuevo_id,
                nombre_requerimiento=nombre,
                clasificacion_requerimiento=clasificacion,
                descripcion_requerimiento=descripcion,
                id_subgrupo_denuncia_id=subgrupo_id,
                codigo_requerimiento=codigo_requerimiento
            )
            
            return JsonResponse({
                'id_requerimiento': requerimiento.id_requerimiento,
                'nombre_requerimiento': requerimiento.nombre_requerimiento,
                'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
                'descripcion_requerimiento': requerimiento.descripcion_requerimiento,
                'codigo_requerimiento': requerimiento.codigo_requerimiento,
                'id_subgrupo_denuncia': requerimiento.id_subgrupo_denuncia_id
            })
            
    except Exception as e:
        print(f"❌ Error en api_requerimientos: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA RUTA COMPLETA
@csrf_exempt
def api_requerimiento_ruta_completa(request, requerimiento_id):
    """Obtener la ruta completa (familia → grupo → subgrupo) de un requerimiento"""
    try:
        requerimiento = Requerimiento.objects.get(id_requerimiento=requerimiento_id)
        
        # Obtener la jerarquía completa
        subgrupo = requerimiento.id_subgrupo_denuncia
        grupo = subgrupo.id_grupo_denuncia
        familia = grupo.id_familia_denuncia
        
        data = {
            'familia': {
                'id': familia.id_familia_denuncia,
                'nombre': familia.nombre_familia_denuncia,
                'codigo': familia.codigo_familia
            },
            'grupo': {
                'id': grupo.id_grupo_denuncia,
                'nombre': grupo.nombre_grupo_denuncia,
                'codigo': grupo.codigo_grupo
            },
            'subgrupo': {
                'id': subgrupo.id_subgrupo_denuncia,
                'nombre': subgrupo.nombre_subgrupo_denuncia,
                'codigo': subgrupo.codigo_subgrupo
            },
            'requerimiento': {
                'id': requerimiento.id_requerimiento,
                'nombre': requerimiento.nombre_requerimiento,
                'codigo': requerimiento.codigo_requerimiento,
                'clasificacion': requerimiento.clasificacion_requerimiento
            }
        }
        
        return JsonResponse(data)
        
    except Requerimiento.DoesNotExist:
        return JsonResponse({'error': 'Requerimiento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA DETALLE DE REQUERIMIENTO (PUT, GET, DELETE)
@csrf_exempt
def api_requerimiento_detalle(request, requerimiento_id):
    """Manejar operaciones CRUD para un requerimiento específico"""
    try:
        requerimiento = Requerimiento.objects.get(id_requerimiento=requerimiento_id)
    except Requerimiento.DoesNotExist:
        return JsonResponse({'error': 'Requerimiento no encontrado'}, status=404)
    
    if request.method == 'GET':
        # Obtener información completa del requerimiento
        data = {
            'id_requerimiento': requerimiento.id_requerimiento,
            'nombre_requerimiento': requerimiento.nombre_requerimiento,
            'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
            'descripcion_requerimiento': requerimiento.descripcion_requerimiento,
            'id_subgrupo_denuncia': requerimiento.id_subgrupo_denuncia_id,
            'codigo_requerimiento': requerimiento.codigo_requerimiento,
        }
        return JsonResponse(data)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            # Actualizar campos permitidos
            if 'nombre_requerimiento' in data:
                requerimiento.nombre_requerimiento = data['nombre_requerimiento']
            if 'clasificacion_requerimiento' in data:
                requerimiento.clasificacion_requerimiento = data['clasificacion_requerimiento']
            if 'descripcion_requerimiento' in data:
                requerimiento.descripcion_requerimiento = data['descripcion_requerimiento']
            if 'id_subgrupo_denuncia' in data:
                # Verificar que el subgrupo existe
                try:
                    subgrupo = SubgrupoDenuncia.objects.get(id_subgrupo_denuncia=data['id_subgrupo_denuncia'])
                    requerimiento.id_subgrupo_denuncia = subgrupo
                except SubgrupoDenuncia.DoesNotExist:
                    return JsonResponse({'error': 'Subgrupo no encontrado'}, status=400)
            
            requerimiento.save()
            
            return JsonResponse({
                'id_requerimiento': requerimiento.id_requerimiento,
                'nombre_requerimiento': requerimiento.nombre_requerimiento,
                'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
                'descripcion_requerimiento': requerimiento.descripcion_requerimiento,
                'mensaje': 'Requerimiento actualizado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'DELETE':
        try:
            requerimiento.delete()
            return JsonResponse({'mensaje': 'Requerimiento eliminado correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)