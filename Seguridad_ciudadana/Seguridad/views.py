from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import login, authenticate, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.http import JsonResponse # type: ignore
from django.utils import timezone # type: ignore
from .models import FamiliaDenuncia, GrupoDenuncia, Requerimiento, SubgrupoDenuncia, TiposVehiculos, Usuario, Denuncia, Vehiculos, AsignacionesVehiculos, Roles, Turnos
from django.views.decorators.csrf import csrf_exempt # type: ignore
import json
from django.db.models import Q # type: ignore

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

# ✅ VISTA PARA PÁGINA DE ADMINISTRACIÓN DE USUARIOS
@login_required
def admin_usuarios(request):
    """Página principal de gestión de usuarios"""
    if not request.user.is_authenticated or not request.user.es_administrador:
        return redirect('login')
    
    # Obtener estadísticas de usuarios
    total_usuarios = Usuario.objects.count()
    total_administradores = Usuario.objects.filter(id_rol__nombre_rol='Administrador').count()
    total_activos = Usuario.objects.filter(is_active=True).count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_administradores': total_administradores,
        'total_activos': total_activos,
    }
    return render(request, 'CRUD/Admin/usuarios.html', context)

# ✅ API PARA CREAR USUARIOS
@csrf_exempt
@login_required
def api_usuarios(request):
    """Manejar operaciones CRUD para usuarios"""
    try:
        if request.method == 'GET':
            # Obtener lista de usuarios
            usuarios = Usuario.objects.all().select_related('id_rol', 'id_turno')
            data = []
            for usuario in usuarios:
                data.append({
                    'id_usuario': usuario.id_usuario,
                    'nombre_usuario': usuario.nombre_usuario,
                    'apellido_pat_usuario': usuario.apellido_pat_usuario,
                    'apellido_mat_usuario': usuario.apellido_mat_usuario,
                    'rut_usuario': usuario.rut_usuario,
                    'telefono_movil_usuario': usuario.telefono_movil_usuario,
                    'correo_electronico_usuario': usuario.correo_electronico_usuario,
                    'estado_usuario': usuario.is_active,  # ✅ Esto está correcto
                    'id_rol': usuario.id_rol_id,
                    'rol_nombre': usuario.id_rol.nombre_rol if usuario.id_rol else '',
                    'id_turno': usuario.id_turno_id if usuario.id_turno else None,
                    'turno_nombre': usuario.id_turno.nombre_turno if usuario.id_turno else '',
                    'fecha_creacion': usuario.fecha_creacion.strftime('%d/%m/%Y %H:%M') if usuario.fecha_creacion else ''
                })
            return JsonResponse(data, safe=False)
        
        elif request.method == 'POST':
            # Crear nuevo usuario
            data = json.loads(request.body)
            
            # Validar campos requeridos según tu modelo
            campos_requeridos = [
                'nombre_usuario', 'apellido_pat_usuario', 'apellido_mat_usuario',
                'rut_usuario', 'telefono_movil_usuario', 'correo_electronico_usuario',
                'password_usuario', 'id_rol'
            ]
            
            for campo in campos_requeridos:
                if not data.get(campo):
                    return JsonResponse({'error': f'El campo {campo} es requerido'}, status=400)
            
            # Verificar si el correo ya existe
            if Usuario.objects.filter(correo_electronico_usuario=data['correo_electronico_usuario']).exists():
                return JsonResponse({'error': 'El correo electrónico ya está registrado'}, status=400)
            
            # Verificar si el RUT ya existe
            if Usuario.objects.filter(rut_usuario=data['rut_usuario']).exists():
                return JsonResponse({'error': 'El RUT ya está registrado'}, status=400)
            
            try:
                # Crear el usuario usando el manager personalizado
                usuario = Usuario.objects.create_user(
                    correo_electronico_usuario=data['correo_electronico_usuario'],
                    password=data['password_usuario'],
                    nombre_usuario=data['nombre_usuario'],
                    apellido_pat_usuario=data['apellido_pat_usuario'],
                    apellido_mat_usuario=data['apellido_mat_usuario'],
                    rut_usuario=data['rut_usuario'],
                    telefono_movil_usuario=data['telefono_movil_usuario'],  # Cambiado a telefono_movil_usuario
                    id_rol_id=data['id_rol'],
                    id_turno_id=data.get('id_turno'),
                    is_active=data.get('estado_usuario', True)  # Cambiado a is_active
                )
                
                return JsonResponse({
                    'id_usuario': usuario.id_usuario,
                    'nombre_completo': f"{usuario.nombre_usuario} {usuario.apellido_pat_usuario} {usuario.apellido_mat_usuario}",
                    'correo_electronico_usuario': usuario.correo_electronico_usuario,
                    'rut_usuario': usuario.rut_usuario,
                    'mensaje': 'Usuario creado correctamente'
                })
                
            except Exception as e:
                return JsonResponse({'error': f'Error al crear usuario: {str(e)}'}, status=500)
            
    except Exception as e:
        print(f"❌ Error en api_usuarios: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def api_usuario_detalle(request, usuario_id):
    """Manejar operaciones CRUD para un usuario específico"""
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    
    if request.method == 'GET':
        data = {
            'id_usuario': usuario.id_usuario,
            'nombre_usuario': usuario.nombre_usuario,
            'apellido_pat_usuario': usuario.apellido_pat_usuario,
            'apellido_mat_usuario': usuario.apellido_mat_usuario,
            'rut_usuario': usuario.rut_usuario,
            'telefono_movil_usuario': usuario.telefono_movil_usuario,
            'correo_electronico_usuario': usuario.correo_electronico_usuario,
            'estado_usuario': usuario.is_active,
            'id_rol': usuario.id_rol_id,
            'id_turno': usuario.id_turno_id if usuario.id_turno else None
        }
        return JsonResponse(data)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            print(f"📥 Datos recibidos para actualizar usuario {usuario_id}: {data}")
            
            # Actualizar campos permitidos según tu modelo
            campos_permitidos = [
                'nombre_usuario', 'apellido_pat_usuario', 'apellido_mat_usuario',
                'telefono_movil_usuario', 'correo_electronico_usuario'
            ]
            
            for campo in campos_permitidos:
                if campo in data:
                    setattr(usuario, campo, data[campo])
            
            if 'estado_usuario' in data:
                usuario.is_active = bool(data['estado_usuario'])
                print(f"✅ Estado actualizado a: {'Activo' if usuario.is_active else 'Inactivo'}")
            
            if 'id_rol' in data:
                try:
                    rol = Roles.objects.get(id_rol=data['id_rol'])
                    usuario.id_rol = rol
                    print(f"✅ Rol actualizado a: {rol.nombre_rol}")
                except Roles.DoesNotExist:
                    return JsonResponse({'error': 'El rol especificado no existe'}, status=400)
            
            if 'id_turno' in data:
                if data['id_turno']:
                    try:
                        turno = Turnos.objects.get(id_turno=data['id_turno'])
                        usuario.id_turno = turno
                        print(f"✅ Turno actualizado a: {turno.nombre_turno}")
                    except Turnos.DoesNotExist:
                        return JsonResponse({'error': 'El turno especificado no existe'}, status=400)
                else:
                    usuario.id_turno = None
                    print("✅ Turno eliminado (seteado a None)")
            
            if 'password_usuario' in data and data['password_usuario']:
                usuario.set_password(data['password_usuario'])
                print("✅ Contraseña actualizada")
            
            usuario.save()
            print(f"✅ Usuario {usuario_id} actualizado correctamente")
            
            return JsonResponse({
                'mensaje': 'Usuario actualizado correctamente',
                'id_usuario': usuario.id_usuario,
                'nombre_completo': f"{usuario.nombre_usuario} {usuario.apellido_pat_usuario}",
                'correo_electronico_usuario': usuario.correo_electronico_usuario,
                'estado_actual': 'Activo' if usuario.is_active else 'Inactivo'
            })
            
        except Exception as e:
            print(f"❌ Error actualizando usuario {usuario_id}: {str(e)}")
            return JsonResponse({'error': f'Error al actualizar usuario: {str(e)}'}, status=500)
    
    elif request.method == 'DELETE':
        try:
            # ✅ VALIDACIÓN: Verificar que el usuario no sea ciudadano
            if usuario.id_rol.nombre_rol == 'Ciudadano':
                return JsonResponse({
                    'error': 'No se puede eliminar usuarios con rol de Ciudadano'
                }, status=400)
            
            # ✅ LISTA DE ROLES PERMITIDOS PARA ELIMINAR
            roles_permitidos_eliminar = ['Administrador', 'Operador', 'Conductor', 'Inspector']
            
            if usuario.id_rol.nombre_rol not in roles_permitidos_eliminar:
                return JsonResponse({
                    'error': f'No se puede eliminar usuarios con rol de {usuario.id_rol.nombre_rol}'
                }, status=400)
            
            # Verificar si el usuario tiene denuncias asociadas
            from django.db.models import Q
            denuncias_asociadas = Denuncia.objects.filter(
                Q(id_operador1=usuario_id) | 
                Q(id_operador2=usuario_id) | 
                Q(id_solicitante=usuario_id)
            )
            if denuncias_asociadas.exists():
                return JsonResponse({
                    'error': 'No se puede eliminar el usuario porque tiene denuncias asociadas'
                }, status=400)
            
            usuario.delete()
            return JsonResponse({'mensaje': 'Usuario eliminado correctamente'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def api_usuarios_buscar(request):
    """Buscar usuarios por nombre, email o RUT"""
    try:
        query = request.GET.get('q', '')
        
        if not query:
            return JsonResponse([], safe=False)
        
        usuarios = Usuario.objects.filter(
            Q(nombre_usuario__icontains=query) |
            Q(apellido_pat_usuario__icontains=query) |
            Q(apellido_mat_usuario__icontains=query) |
            Q(correo_electronico_usuario__icontains=query) |
            Q(rut_usuario__icontains=query)
        ).select_related('id_rol')[:10]  # Limitar a 10 resultados
        
        data = []
        for usuario in usuarios:
            data.append({
                'id_usuario': usuario.id_usuario,
                'nombre_completo': f"{usuario.nombre_usuario} {usuario.apellido_pat_usuario} {usuario.apellido_mat_usuario}",
                'rut_usuario': usuario.rut_usuario,
                'correo_electronico_usuario': usuario.correo_electronico_usuario,
                'rol_nombre': usuario.id_rol.nombre_rol if usuario.id_rol else '',
                'estado_usuario': usuario.is_active
            })
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        print(f"❌ Error en api_usuarios_buscar: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
    
# ========== APIs ESPECÍFICAS PARA IONIC ==========

@csrf_exempt
def api_login_ionic(request):
    """API de login específica para Ionic (sin sesiones)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({'success': False, 'error': 'Email y contraseña requeridos'}, status=400)
            
            # Autenticar usuario
            user = authenticate(request, username=email, password=password)
            
            if user is not None and user.is_active:
                # Login exitoso - devolver datos del usuario
                user_data = {
                    'id_usuario': user.id_usuario,
                    'nombre_usuario': user.nombre_usuario,
                    'apellido_pat_usuario': user.apellido_pat_usuario,
                    'apellido_mat_usuario': user.apellido_mat_usuario,
                    'correo_electronico_usuario': user.correo_electronico_usuario,
                    'telefono_movil_usuario': user.telefono_movil_usuario,
                    'id_rol': user.id_rol.id_rol,
                    'nombre_rol': user.id_rol.nombre_rol,
                    'es_administrador': user.es_administrador,
                    'es_operador': user.es_operador,
                    'es_conductor': user.es_conductor,
                    'es_ciudadano': user.es_ciudadano,
                    'is_active': user.is_active
                }
                
                return JsonResponse({
                    'success': True, 
                    'user': user_data,
                    'message': 'Login exitoso'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Credenciales inválidas o usuario inactivo'
                }, status=401)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def api_register_ciudadano(request):
    """API para registro de ciudadanos desde Ionic"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"📥 Datos recibidos para registro: {data}")
            
            # Validar campos requeridos
            required_fields = [
                'rut_usuario', 'nombre_usuario', 'apellido_pat_usuario',
                'apellido_mat_usuario', 'correo_electronico_usuario',
                'telefono_movil_usuario', 'password'
            ]
            
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False, 
                        'error': f'El campo {field} es requerido'
                    }, status=400)
            
            # Verificar si el correo ya existe
            if Usuario.objects.filter(correo_electronico_usuario=data['correo_electronico_usuario']).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'El correo electrónico ya está registrado'
                }, status=400)
            
            # Verificar si el RUT ya existe
            if Usuario.objects.filter(rut_usuario=data['rut_usuario']).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'El RUT ya está registrado'
                }, status=400)
            
            # Asignar automáticamente rol de Ciudadano (id=3)
            try:
                rol_ciudadano = Roles.objects.get(id_rol=3)
                print(f"✅ Rol Ciudadano encontrado: {rol_ciudadano.nombre_rol}")
            except Roles.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Rol Ciudadano no configurado en el sistema'
                }, status=500)
            
            print("✅ Creando usuario con datos:", {
                'correo': data['correo_electronico_usuario'],
                'rut': data['rut_usuario'],
                'nombre': data['nombre_usuario'],
                'rol': rol_ciudadano.id_rol
            })
            
            # Crear el usuario usando el manager personalizado
            usuario = Usuario.objects.create_user(
                correo_electronico_usuario=data['correo_electronico_usuario'],
                password=data['password'],
                rut_usuario=data['rut_usuario'],
                nombre_usuario=data['nombre_usuario'],
                apellido_pat_usuario=data['apellido_pat_usuario'],
                apellido_mat_usuario=data['apellido_mat_usuario'],
                telefono_movil_usuario=data['telefono_movil_usuario'],
                id_rol=rol_ciudadano,  # Rol Ciudadano
                is_active=True  # Ciudadanos activos por defecto
            )
            
            print(f"✅ Usuario creado exitosamente: {usuario.id_usuario}")
            
            return JsonResponse({
                'success': True,
                'message': 'Usuario registrado correctamente',
                'user': {
                    'id_usuario': usuario.id_usuario,
                    'nombre_completo': f"{usuario.nombre_usuario} {usuario.apellido_pat_usuario}",
                    'correo_electronico_usuario': usuario.correo_electronico_usuario,
                    'rut_usuario': usuario.rut_usuario,
                    'rol': usuario.id_rol.nombre_rol
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            print(f"❌ Error en registro de ciudadano: {str(e)}")
            import traceback
            print(f"❌ Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)

@csrf_exempt
def api_vehiculos(request):
    """API para gestión de vehículos"""
    try:
        if request.method == 'GET':
            vehiculos = Vehiculos.objects.all().select_related('id_tipo_vehiculo')
            data = []
            for vehiculo in vehiculos:
                data.append({
                    'id_vehiculo': vehiculo.id_vehiculo,
                    'patente_vehiculo': vehiculo.patente_vehiculo,
                    'marca_vehiculo': vehiculo.marca_vehiculo,
                    'modelo_vehiculo': vehiculo.modelo_vehiculo,
                    'codigo_vehiculo': vehiculo.codigo_vehiculo,
                    'id_tipo_vehiculo': vehiculo.id_tipo_vehiculo.id_tipo_vehiculo,
                    'nombre_tipo_vehiculo': vehiculo.id_tipo_vehiculo.nombre_tipo_vehiculo,
                    'estado_vehiculo': vehiculo.estado_vehiculo,
                    'fecha_creacion': vehiculo.fecha_creacion.isoformat() if vehiculo.fecha_creacion else None
                })
            return JsonResponse({'success': True, 'vehiculos': data})
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            # Validar campos requeridos
            campos_requeridos = ['patente_vehiculo', 'marca_vehiculo', 'modelo_vehiculo', 'codigo_vehiculo', 'id_tipo_vehiculo']
            for campo in campos_requeridos:
                if not data.get(campo):
                    return JsonResponse({'success': False, 'error': f'Campo {campo} es requerido'}, status=400)
            
            # Verificar patente única
            if Vehiculos.objects.filter(patente_vehiculo=data['patente_vehiculo']).exists():
                return JsonResponse({'success': False, 'error': 'La patente ya existe'}, status=400)
            
            # Crear vehículo
            vehiculo = Vehiculos.objects.create(
                patente_vehiculo=data['patente_vehiculo'],
                marca_vehiculo=data['marca_vehiculo'],
                modelo_vehiculo=data['modelo_vehiculo'],
                codigo_vehiculo=data['codigo_vehiculo'],
                id_tipo_vehiculo_id=data['id_tipo_vehiculo'],
                estado_vehiculo=data.get('estado_vehiculo', 'Disponible')
            )
            
            return JsonResponse({
                'success': True,
                'vehiculo': {
                    'id_vehiculo': vehiculo.id_vehiculo,
                    'patente_vehiculo': vehiculo.patente_vehiculo,
                    'marca_vehiculo': vehiculo.marca_vehiculo,
                    'modelo_vehiculo': vehiculo.modelo_vehiculo,
                    'codigo_vehiculo': vehiculo.codigo_vehiculo,
                    'estado_vehiculo': vehiculo.estado_vehiculo
                },
                'message': 'Vehículo creado exitosamente'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def api_tipos_vehiculos(request):
    """API para obtener tipos de vehículos"""
    try:
        tipos = TiposVehiculos.objects.all()
        data = [{
            'id_tipo_vehiculo': tipo.id_tipo_vehiculo,
            'nombre_tipo_vehiculo': tipo.nombre_tipo_vehiculo
        } for tipo in tipos]
        
        return JsonResponse({'success': True, 'tipos_vehiculos': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def api_denuncias_ionic(request):
    """API para gestión de denuncias desde Ionic"""
    try:
        if request.method == 'GET':
            denuncias = Denuncia.objects.all().select_related(
                'id_operador1', 'id_solicitante', 'id_requerimiento', 'id_turno'
            )
            data = []
            for denuncia in denuncias:
                data.append({
                    'id_denuncia': denuncia.id_denuncia,
                    'hora_denuncia': denuncia.hora_denuncia.isoformat(),
                    'fecha_denuncia': denuncia.fecha_denuncia.isoformat(),
                    'id_solicitante': denuncia.id_solicitante.id_usuario,
                    'nombre_solicitante': denuncia.id_solicitante.get_full_name(),
                    'direccion': denuncia.direccion,
                    'detalle_denuncia': denuncia.detalle_denuncia,
                    'estado_denuncia': denuncia.estado_denuncia,
                    'id_requerimiento': denuncia.id_requerimiento.id_requerimiento,
                    'nombre_requerimiento': denuncia.id_requerimiento.nombre_requerimiento,
                    'visibilidad_camaras_denuncia': denuncia.visibilidad_camaras_denuncia,
                    'labor_realizada_denuncia': denuncia.labor_realizada_denuncia,
                    'fecha_creacion': denuncia.fecha_creacion.isoformat() if denuncia.fecha_creacion else None
                })
            return JsonResponse({'success': True, 'denuncias': data})
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            # Validar campos requeridos
            campos_requeridos = [
                'hora_denuncia', 'fecha_denuncia', 'id_solicitante', 'direccion',
                'id_requerimiento', 'detalle_denuncia', 'id_turno'
            ]
            for campo in campos_requeridos:
                if not data.get(campo):
                    return JsonResponse({'success': False, 'error': f'Campo {campo} es requerido'}, status=400)
            
            # Crear denuncia
            denuncia = Denuncia.objects.create(
                hora_denuncia=data['hora_denuncia'],
                fecha_denuncia=data['fecha_denuncia'],
                id_solicitante_id=data['id_solicitante'],
                direccion=data['direccion'],
                id_requerimiento_id=data['id_requerimiento'],
                detalle_denuncia=data['detalle_denuncia'],
                id_turno_id=data['id_turno'],
                visibilidad_camaras_denuncia=data.get('visibilidad_camaras_denuncia', False),
                labor_realizada_denuncia=data.get('labor_realizada_denuncia', ''),
                estado_denuncia=data.get('estado_denuncia', 'Recibido'),
                id_operador1_id=data.get('id_operador1')  # Opcional, puede ser el usuario actual
            )
            
            return JsonResponse({
                'success': True,
                'denuncia': {
                    'id_denuncia': denuncia.id_denuncia,
                    'estado_denuncia': denuncia.estado_denuncia,
                    'fecha_creacion': denuncia.fecha_creacion.isoformat()
                },
                'message': 'Denuncia creada exitosamente'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def api_dashboard_stats(request):
    """API para obtener estadísticas del dashboard"""
    try:
        total_usuarios = Usuario.objects.count()
        total_denuncias = Denuncia.objects.count()
        vehiculos_activos = Vehiculos.objects.filter(estado_vehiculo='Disponible').count()
        denuncias_pendientes = Denuncia.objects.filter(estado_denuncia='Recibido').count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_usuarios': total_usuarios,
                'total_denuncias': total_denuncias,
                'vehiculos_activos': vehiculos_activos,
                'denuncias_pendientes': denuncias_pendientes
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ========== APIs PARA DATOS MAESTROS ==========

@csrf_exempt
def api_roles_ionic(request):
    """API para obtener roles"""
    try:
        roles = Roles.objects.all()
        data = [{
            'id_rol': rol.id_rol,
            'nombre_rol': rol.nombre_rol
        } for rol in roles]
        
        return JsonResponse({'success': True, 'roles': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def api_turnos_ionic(request):
    """API para obtener turnos"""
    try:
        turnos = Turnos.objects.all()
        data = []
        for turno in turnos:
            data.append({
                'id_turno': turno.id_turno,
                'nombre_turno': turno.nombre_turno,
                'hora_inicio': turno.hora_inicio.strftime('%H:%M'),
                'hora_fin': turno.hora_fin.strftime('%H:%M')
            })
        
        return JsonResponse({'success': True, 'turnos': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)