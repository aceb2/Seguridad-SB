from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import login, authenticate, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.http import JsonResponse # type: ignore
from django.utils import timezone # type: ignore
from .models import (
    FamiliaDenuncia, GrupoDenuncia, Requerimiento, SubgrupoDenuncia, 
    TiposVehiculos, Usuario, Denuncia, Vehiculos, 
    AsignacionVehiculo, AsignacionRadio, Roles, Turnos,
    Ciudadano, ServiciosEmergencia, MovilesDenuncia, DerivacionesDenuncia,
    Fiscalizacion, SolicitudCiudadano, Radio
)
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
            # ✅ CORREGIDO: Verificar por nombre de rol en lugar de propiedades que no existen
            rol_permitido = user.id_rol.nombre_rol.lower() in ['administrador', 'operador', 'supervisor', 'inspector']
            
            if rol_permitido:
                login(request, user)
            
                # ✅ MENSAJE PERSONALIZADO POR ROL
                rol_mensaje = user.id_rol.nombre_rol
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
    
    return render(request, 'usuario/inicio.html', context)

def clear_alert(request):
    """Limpiar alertas de la sesión"""
    if 'alert_type' in request.session:
        del request.session['alert_type']
        del request.session['alert_title'] 
        del request.session['alert_message']
        request.session.modified = True
    return JsonResponse({'status': 'success'})

@login_required
def admin_dashboard(request):
    # ✅ CORREGIDO: Verificar por nombre de rol
    if request.user.id_rol.nombre_rol.lower() != 'administrador':
        return redirect('index')
    
    total_usuarios = Usuario.objects.count()
    total_denuncias = Denuncia.objects.count()
    vehiculos_activos = Vehiculos.objects.filter(estado_vehiculo='Disponible').count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_denuncias': total_denuncias,
        'vehiculos_activos': vehiculos_activos,
    }
    return render(request, 'usuario/admin.html', context)

def admin_requerimientos(request):
    """Página principal de gestión de requerimientos"""
    if not request.user.is_authenticated or request.user.id_rol.nombre_rol.lower() != 'administrador':
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
    return render(request, 'crud/admin/requerimientos.html', context)

# ✅ API PARA FAMILIAS (CORREGIDA SEGÚN BD REAL)
@csrf_exempt
def api_familias(request, familia_id=None):
    """Manejar operaciones CRUD para familias"""
    try:
        if request.method == 'GET':
            familias = FamiliaDenuncia.objects.all()
            data = []
            for familia in familias:
                data.append({
                    'id': familia.id_familia_denuncia,  # CAMBIADO: id en lugar de id_familia_denuncia
                    'nombre_familia_denuncia': familia.nombre_familia_denuncia,
                    'codigo_familia': familia.codigo_familia  # CAMBIADO: codigo_familia en lugar de codigo_familia_denuncia
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
            
            # Crear familia con el campo correcto
            familia = FamiliaDenuncia.objects.create(
                nombre_familia_denuncia=nombre,
                codigo_familia=nombre[:3].upper() + str(FamiliaDenuncia.objects.count() + 1).zfill(3)
            )
            
            return JsonResponse({
                'id': familia.id_familia_denuncia,  # CAMBIADO: id en lugar de id_familia_denuncia
                'nombre_familia_denuncia': familia.nombre_familia_denuncia,
                'codigo_familia': familia.codigo_familia  # CAMBIADO: codigo_familia en lugar de codigo_familia_denuncia
            })
            
    except Exception as e:
        print(f"❌ Error en api_familias: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA GRUPOS (CORREGIDA SEGÚN BD REAL)
@csrf_exempt
def api_grupos(request, grupo_id=None):
    """Manejar operaciones CRUD para grupos - CORREGIDA"""
    try:
        if request.method == 'GET':
            familia_id = request.GET.get('familia_id')
            
            if familia_id:
                # ✅ FILTRAR POR FAMILIA
                grupos = GrupoDenuncia.objects.filter(id_familia_denuncia_id=familia_id)
            else:
                # ✅ OBTENER TODOS LOS GRUPOS
                grupos = GrupoDenuncia.objects.all()
            
            data = []
            for grupo in grupos:
                data.append({
                    'id_grupo_denuncia': grupo.id_grupo_denuncia,
                    'nombre_grupo_denuncia': grupo.nombre_grupo_denuncia,
                    'codigo_grupo': grupo.codigo_grupo,  # ✅ CAMPO CORRECTO según tu modelo
                    'id_familia_denuncia': grupo.id_familia_denuncia_id
                })
            
            print(f"✅ Grupos encontrados: {len(data)}")
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
            
            # Crear grupo con campos correctos
            grupo = GrupoDenuncia.objects.create(
                nombre_grupo_denuncia=nombre,
                id_familia_denuncia_id=familia_id,
                codigo_grupo=nombre[:3].upper() + str(GrupoDenuncia.objects.count() + 1).zfill(3)
            )
            
            return JsonResponse({
                'id_grupo_denuncia': grupo.id_grupo_denuncia,
                'nombre_grupo_denuncia': grupo.nombre_grupo_denuncia,
                'codigo_grupo': grupo.codigo_grupo,  # ✅ CAMPO CORRECTO
                'id_familia_denuncia': grupo.id_familia_denuncia_id
            })
            
    except Exception as e:
        print(f"❌ Error en api_grupos: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)
    
# ✅ API PARA SUBGRUPOS (CORREGIDA SEGÚN BD REAL)
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
                    'id': subgrupo.id_subgrupo_denuncia,  # CAMBIADO: id en lugar de id_subgrupo_denuncia
                    'nombre_subgrupo_denuncia': subgrupo.nombre_subgrupo_denuncia,
                    'codigo_subgrupo': subgrupo.codigo_subgrupo,  # CAMBIADO: codigo_subgrupo en lugar de codigo_subgrupo_denuncia
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
            
            # Crear subgrupo con campo correcto
            subgrupo = SubgrupoDenuncia.objects.create(
                nombre_subgrupo_denuncia=nombre,
                id_grupo_denuncia_id=grupo_id,
                codigo_subgrupo=nombre[:3].upper() + str(SubgrupoDenuncia.objects.count() + 1).zfill(3)
            )
            
            return JsonResponse({
                'id': subgrupo.id_subgrupo_denuncia,  # CAMBIADO: id en lugar de id_subgrupo_denuncia
                'nombre_subgrupo_denuncia': subgrupo.nombre_subgrupo_denuncia,
                'codigo_subgrupo': subgrupo.codigo_subgrupo,  # CAMBIADO: codigo_subgrupo en lugar de codigo_subgrupo_denuncia
                'id_grupo_denuncia': subgrupo.id_grupo_denuncia_id
            })
            
    except Exception as e:
        print(f"❌ Error en api_subgrupos: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA REQUERIMIENTOS (OPTIMIZADA CON SELECT_RELATED)
@csrf_exempt
def api_requerimientos(request):
    """Listar y crear requerimientos - OPTIMIZADA PARA RENDIMIENTO"""
    try:
        if request.method == 'GET':
            subgrupo_id = request.GET.get('subgrupo_id')
            
            # ✅ OPTIMIZACIÓN: Cargar todas las relaciones en una sola consulta
            if subgrupo_id:
                requerimientos = Requerimiento.objects.filter(
                    id_subgrupo_denuncia_id=subgrupo_id
                ).select_related(
                    'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia'
                )
            else:
                requerimientos = Requerimiento.objects.all().select_related(
                    'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia'
                )
            
            data = []
            for req in requerimientos:
                # ✅ ACCESO DIRECTO A LAS RELACIONES PRE-CARGADAS
                try:
                    # Estas relaciones ya están cargadas en memoria, no generan consultas adicionales
                    subgrupo = req.id_subgrupo_denuncia
                    grupo = subgrupo.id_grupo_denuncia
                    familia = grupo.id_familia_denuncia
                    
                    requerimiento_data = {
                        'id': req.id_requerimiento,
                        'id_requerimiento': req.id_requerimiento,
                        'nombre_requerimiento': req.nombre_requerimiento,
                        'clasificacion_requerimiento': req.clasificacion_requerimiento,
                        'descripcion_requerimiento': req.descripcion_requerimiento,
                        'codigo_requerimiento': req.codigo_requerimiento,
                        'id_subgrupo_denuncia': req.id_subgrupo_denuncia_id,
                        
                        # ✅ INFORMACIÓN DE JERARQUÍA (cargada eficientemente)
                        'familia_nombre': familia.nombre_familia_denuncia,
                        'grupo_nombre': grupo.nombre_grupo_denuncia,
                        'subgrupo_nombre': subgrupo.nombre_subgrupo_denuncia,
                        
                        # ✅ IDs para referencia
                        'id_familia_denuncia': familia.id_familia_denuncia,
                        'id_grupo_denuncia': grupo.id_grupo_denuncia,
                        'id_subgrupo_denuncia_completo': subgrupo.id_subgrupo_denuncia,
                        
                        # ✅ Códigos de jerarquía
                        'codigo_familia': familia.codigo_familia,
                        'codigo_grupo': grupo.codigo_grupo,
                        'codigo_subgrupo': subgrupo.codigo_subgrupo
                    }
                except Exception as e:
                    print(f"⚠️ Error obteniendo jerarquía para requerimiento {req.id_requerimiento}: {e}")
                    # Estructura básica en caso de error
                    requerimiento_data = {
                        'id': req.id_requerimiento,
                        'id_requerimiento': req.id_requerimiento,
                        'nombre_requerimiento': req.nombre_requerimiento,
                        'clasificacion_requerimiento': req.clasificacion_requerimiento,
                        'descripcion_requerimiento': req.descripcion_requerimiento,
                        'codigo_requerimiento': req.codigo_requerimiento,
                        'id_subgrupo_denuncia': req.id_subgrupo_denuncia_id,
                        'familia_nombre': 'No disponible',
                        'grupo_nombre': 'No disponible',
                        'subgrupo_nombre': 'No disponible',
                    }
                
                data.append(requerimiento_data)
            
            print(f"✅ Requerimientos cargados: {len(data)} con información de jerarquía (OPTIMIZADO)")
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
            
            # Crear requerimiento
            requerimiento = Requerimiento.objects.create(
                nombre_requerimiento=nombre,
                clasificacion_requerimiento=clasificacion,
                descripcion_requerimiento=descripcion,
                id_subgrupo_denuncia_id=subgrupo_id,
                codigo_requerimiento=nombre[:3].upper() + str(Requerimiento.objects.count() + 1).zfill(3)
            )
            
            # ✅ OPTIMIZAR: Cargar relaciones para la respuesta
            requerimiento_con_relaciones = Requerimiento.objects.select_related(
                'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia'
            ).get(id_requerimiento=requerimiento.id_requerimiento)
            
            try:
                subgrupo = requerimiento_con_relaciones.id_subgrupo_denuncia
                grupo = subgrupo.id_grupo_denuncia
                familia = grupo.id_familia_denuncia
                
                return JsonResponse({
                    'id': requerimiento.id_requerimiento,
                    'id_requerimiento': requerimiento.id_requerimiento,
                    'nombre_requerimiento': requerimiento.nombre_requerimiento,
                    'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
                    'descripcion_requerimiento': requerimiento.descripcion_requerimiento,
                    'codigo_requerimiento': requerimiento.codigo_requerimiento,
                    'id_subgrupo_denuncia': requerimiento.id_subgrupo_denuncia_id,
                    
                    # ✅ JERARQUÍA
                    'familia_nombre': familia.nombre_familia_denuncia,
                    'grupo_nombre': grupo.nombre_grupo_denuncia,
                    'subgrupo_nombre': subgrupo.nombre_subgrupo_denuncia,
                    'id_familia_denuncia': familia.id_familia_denuncia,
                    'id_grupo_denuncia': grupo.id_grupo_denuncia
                })
            except Exception as e:
                print(f"⚠️ Error obteniendo jerarquía para nuevo requerimiento: {e}")
                return JsonResponse({
                    'id': requerimiento.id_requerimiento,
                    'nombre_requerimiento': requerimiento.nombre_requerimiento,
                    'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
                    'descripcion_requerimiento': requerimiento.descripcion_requerimiento,
                    'codigo_requerimiento': requerimiento.codigo_requerimiento,
                    'id_subgrupo_denuncia': requerimiento.id_subgrupo_denuncia_id,
                    'familia_nombre': 'No disponible',
                    'grupo_nombre': 'No disponible',
                    'subgrupo_nombre': 'No disponible'
                })
            
    except Exception as e:
        print(f"❌ Error en api_requerimientos: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ API PARA DETALLE DE FAMILIA (CORREGIDA)
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

# ✅ API PARA DETALLE DE GRUPO (CORREGIDA)
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

# ✅ API PARA DETALLE DE SUBGRUPO (CORREGIDA)
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

@csrf_exempt
def api_requerimiento_detalle(request, requerimiento_id):
    """Manejar operaciones CRUD para un requerimiento específico - COMPLETAMENTE CORREGIDO"""
    try:
        # ✅ OPTIMIZACIÓN: Cargar relaciones para el detalle
        requerimiento = Requerimiento.objects.select_related(
            'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia'
        ).get(id_requerimiento=requerimiento_id)
    except Requerimiento.DoesNotExist:
        return JsonResponse({'error': 'Requerimiento no encontrado'}, status=404)
    
    if request.method == 'GET':
        # ✅ OBTENER INFORMACIÓN DE JERARQUÍA (ya cargada eficientemente)
        try:
            subgrupo = requerimiento.id_subgrupo_denuncia
            grupo = subgrupo.id_grupo_denuncia
            familia = grupo.id_familia_denuncia
            
            data = {
                'id_requerimiento': requerimiento.id_requerimiento,
                'nombre_requerimiento': requerimiento.nombre_requerimiento,
                'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
                'descripcion_requerimiento': requerimiento.descripcion_requerimiento,
                'codigo_requerimiento': requerimiento.codigo_requerimiento,
                'id_subgrupo_denuncia': requerimiento.id_subgrupo_denuncia_id,  # ✅ CORREGIDO: usar _id
                
                # ✅ INFORMACIÓN DE JERARQUÍA
                'familia_nombre': familia.nombre_familia_denuncia,
                'grupo_nombre': grupo.nombre_grupo_denuncia,
                'subgrupo_nombre': subgrupo.nombre_subgrupo_denuncia,
                'id_familia_denuncia': familia.id_familia_denuncia,
                'id_grupo_denuncia': grupo.id_grupo_denuncia,
            }
        except Exception as e:
            print(f"⚠️ Error obteniendo jerarquía: {e}")
            data = {
                'id_requerimiento': requerimiento.id_requerimiento,
                'nombre_requerimiento': requerimiento.nombre_requerimiento,
                'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
                'descripcion_requerimiento': requerimiento.descripcion_requerimiento,
                'codigo_requerimiento': requerimiento.codigo_requerimiento,
                'id_subgrupo_denuncia': requerimiento.id_subgrupo_denuncia_id,  # ✅ CORREGIDO: usar _id
                'familia_nombre': 'No disponible',
                'grupo_nombre': 'No disponible',
                'subgrupo_nombre': 'No disponible',
            }
        
        return JsonResponse(data)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            print(f"📥 Datos recibidos para actualizar requerimiento {requerimiento_id}: {data}")
            
            # ✅ DEBUG: Mostrar estado actual del requerimiento
            print(f"🔍 Estado actual:")
            print(f"  - Subgrupo: {requerimiento.id_subgrupo_denuncia_id}")  # ✅ CORREGIDO: usar _id
            print(f"  - Nombre: {requerimiento.nombre_requerimiento}")
            print(f"  - Clasificación: {requerimiento.clasificacion_requerimiento}")
            
            # ✅ ACTUALIZAR CAMPOS CON NOMBRES CORRECTOS
            campos_actualizados = []
            
            # ✅ ACTUALIZAR NOMBRE SI EXISTE Y ES DIFERENTE
            if 'nombre_requerimiento' in data and data['nombre_requerimiento'] != requerimiento.nombre_requerimiento:
                requerimiento.nombre_requerimiento = data['nombre_requerimiento']
                campos_actualizados.append('nombre')
                print(f"✅ Nombre actualizado a: {data['nombre_requerimiento']}")
            
            # ✅ ACTUALIZAR CLASIFICACIÓN SI EXISTE Y ES DIFERENTE
            if 'clasificacion_requerimiento' in data and data['clasificacion_requerimiento'] != requerimiento.clasificacion_requerimiento:
                requerimiento.clasificacion_requerimiento = data['clasificacion_requerimiento']
                campos_actualizados.append('clasificación')
                print(f"✅ Clasificación actualizada a: {data['clasificacion_requerimiento']}")
            
            # ✅ ACTUALIZAR DESCRIPCIÓN
            if 'descripcion_requerimiento' in data:
                requerimiento.descripcion_requerimiento = data['descripcion_requerimiento']
                campos_actualizados.append('descripción')
                print(f"✅ Descripción actualizada")
            
            # ✅ CORREGIDO: ACTUALIZAR SUBGRUPO SI SE ENVÍA Y ES DIFERENTE
            subgrupo_cambiado = False
            nuevo_subgrupo_id = None
            
            # ✅ VERIFICAR DIFERENTES FORMAS EN QUE PUEDE VENIR EL SUBGRUPO
            posibles_campos_subgrupo = ['id_subgrupo_denuncia_id', 'id_subgrupo_denuncia', 'subgrupo_id']
            
            for campo in posibles_campos_subgrupo:
                if campo in data and data[campo] is not None:
                    nuevo_subgrupo_id = data[campo]
                    print(f"🔍 Nuevo subgrupo recibido en campo '{campo}': {nuevo_subgrupo_id}")
                    break
            
            if nuevo_subgrupo_id is not None:
                # ✅ CONVERTIR A ENTERO PARA COMPARACIÓN
                try:
                    nuevo_subgrupo_id = int(nuevo_subgrupo_id)
                    subgrupo_actual_id = int(requerimiento.id_subgrupo_denuncia_id)  # ✅ CORREGIDO: usar _id
                    
                    print(f"🔍 Comparando subgrupos:")
                    print(f"  - Nuevo: {nuevo_subgrupo_id} (tipo: {type(nuevo_subgrupo_id)})")
                    print(f"  - Actual: {subgrupo_actual_id} (tipo: {type(subgrupo_actual_id)})")
                    print(f"  - ¿Son diferentes?: {nuevo_subgrupo_id != subgrupo_actual_id}")
                    
                    # ✅ VERIFICAR SI REALMENTE ESTÁ CAMBIANDO EL SUBGRUPO
                    if nuevo_subgrupo_id != subgrupo_actual_id:
                        print(f"🔄 Cambiando subgrupo de {subgrupo_actual_id} a {nuevo_subgrupo_id}")
                        
                        # ✅ VERIFICAR QUE EL SUBGRUPO EXISTE
                        try:
                            subgrupo = SubgrupoDenuncia.objects.get(id_subgrupo_denuncia=nuevo_subgrupo_id)
                            requerimiento.id_subgrupo_denuncia = subgrupo
                            campos_actualizados.append('subgrupo')
                            subgrupo_cambiado = True
                            print(f"✅ Subgrupo actualizado a ID: {nuevo_subgrupo_id}")
                            
                            # ✅ OBTENER LA NUEVA JERARQUÍA
                            grupo = subgrupo.id_grupo_denuncia
                            familia = grupo.id_familia_denuncia
                            print(f"📋 Nueva jerarquía: {familia.nombre_familia_denuncia} → {grupo.nombre_grupo_denuncia} → {subgrupo.nombre_subgrupo_denuncia}")
                            
                        except SubgrupoDenuncia.DoesNotExist:
                            print(f"❌ Subgrupo no encontrado: {nuevo_subgrupo_id}")
                            return JsonResponse({'error': 'Subgrupo no encontrado'}, status=400)
                    else:
                        print("ℹ️  Subgrupo sin cambios (mismo ID)")
                except (ValueError, TypeError) as e:
                    print(f"❌ Error convirtiendo subgrupo_id: {e}")
                    return JsonResponse({'error': 'ID de subgrupo inválido'}, status=400)
            else:
                print("ℹ️  No se envió id_subgrupo_denuncia_id o es None")
            
            # ✅ GUARDAR SOLO SI HAY CAMBIOS
            if campos_actualizados:
                requerimiento.save()
                print(f"✅ Requerimiento {requerimiento_id} actualizado correctamente. Campos: {', '.join(campos_actualizados)}")
                
                # ✅ CARGAR RELACIONES ACTUALIZADAS PARA LA RESPUESTA
                requerimiento.refresh_from_db()
                requerimiento_actualizado = Requerimiento.objects.select_related(
                    'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia'
                ).get(id_requerimiento=requerimiento_id)
                
                # ✅ OBTENER JERARQUÍA ACTUALIZADA
                try:
                    subgrupo_actual = requerimiento_actualizado.id_subgrupo_denuncia
                    grupo_actual = subgrupo_actual.id_grupo_denuncia
                    familia_actual = grupo_actual.id_familia_denuncia
                    
                    respuesta = {
                        'id_requerimiento': requerimiento_actualizado.id_requerimiento,
                        'nombre_requerimiento': requerimiento_actualizado.nombre_requerimiento,
                        'clasificacion_requerimiento': requerimiento_actualizado.clasificacion_requerimiento,
                        'descripcion_requerimiento': requerimiento_actualizado.descripcion_requerimiento,
                        'mensaje': 'Requerimiento actualizado correctamente',
                        # ✅ INCLUIR INFORMACIÓN DE JERARQUÍA ACTUALIZADA
                        'jerarquia_actual': {
                            'familia': {
                                'id': familia_actual.id_familia_denuncia,
                                'nombre': familia_actual.nombre_familia_denuncia
                            },
                            'grupo': {
                                'id': grupo_actual.id_grupo_denuncia,
                                'nombre': grupo_actual.nombre_grupo_denuncia
                            },
                            'subgrupo': {
                                'id': subgrupo_actual.id_subgrupo_denuncia,
                                'nombre': subgrupo_actual.nombre_subgrupo_denuncia
                            }
                        }
                    }
                    print(f"📤 Respuesta con jerarquía actualizada: {respuesta['jerarquia_actual']}")
                    
                except Exception as e:
                    print(f"⚠️ Error obteniendo jerarquía actualizada: {e}")
                    respuesta = {
                        'id_requerimiento': requerimiento_actualizado.id_requerimiento,
                        'nombre_requerimiento': requerimiento_actualizado.nombre_requerimiento,
                        'clasificacion_requerimiento': requerimiento_actualizado.clasificacion_requerimiento,
                        'descripcion_requerimiento': requerimiento_actualizado.descripcion_requerimiento,
                        'mensaje': 'Requerimiento actualizado correctamente'
                    }
                
                return JsonResponse(respuesta)
            else:
                print("ℹ️  No hay cambios para guardar")
                return JsonResponse({
                    'mensaje': 'No se realizaron cambios',
                    'id_requerimiento': requerimiento.id_requerimiento,
                    'nombre_requerimiento': requerimiento.nombre_requerimiento,
                    'clasificacion_requerimiento': requerimiento.clasificacion_requerimiento,
                    'descripcion_requerimiento': requerimiento.descripcion_requerimiento
                })
            
        except Exception as e:
            print(f"❌ Error actualizando requerimiento {requerimiento_id}: {str(e)}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return JsonResponse({'error': f'Error al actualizar requerimiento: {str(e)}'}, status=500)
    
    elif request.method == 'DELETE':
        try:
            requerimiento.delete()
            return JsonResponse({'mensaje': 'Requerimiento eliminado correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
# ✅ API PARA RUTA COMPLETA - CORREGIDA
@csrf_exempt
def api_requerimiento_ruta_completa(request, requerimiento_id):
    """Obtener la ruta completa (familia → grupo → subgrupo) de un requerimiento"""
    try:
        # ✅ OPTIMIZACIÓN: Cargar todas las relaciones en una consulta
        requerimiento = Requerimiento.objects.select_related(
            'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia'
        ).get(id_requerimiento=requerimiento_id)
        
        # Obtener la jerarquía completa (ya cargada)
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
        print(f"❌ Error en api_requerimiento_ruta_completa: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def admin_usuarios(request):
    """Página principal de gestión de usuarios"""
    if not request.user.is_authenticated or request.user.id_rol.nombre_rol.lower() != 'administrador':
        return redirect('login')
    
    # Obtener estadísticas de usuarios
    total_usuarios = Usuario.objects.count()
    total_administradores = Usuario.objects.filter(id_rol__nombre_rol='administrador').count()
    total_activos = Usuario.objects.filter(is_active=True).count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_administradores': total_administradores,
        'total_activos': total_activos,
    }
    return render(request, 'crud/admin/usuarios.html', context)

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
                    'estado_usuario': usuario.is_active,
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
                'password', 'id_rol'
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
                    password=data['password'],
                    nombre_usuario=data['nombre_usuario'],
                    apellido_pat_usuario=data['apellido_pat_usuario'],
                    apellido_mat_usuario=data['apellido_mat_usuario'],
                    rut_usuario=data['rut_usuario'],
                    telefono_movil_usuario=data['telefono_movil_usuario'],
                    id_rol_id=data['id_rol'],
                    id_turno_id=data.get('id_turno'),
                    is_active=data.get('estado_usuario', True)
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
            
            if 'password' in data and data['password']:
                usuario.set_password(data['password'])
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
            # ✅ LISTA DE ROLES PERMITIDOS PARA ELIMINAR
            roles_permitidos_eliminar = ['administrador', 'operador', 'supervisor', 'inspector']
            
            if usuario.id_rol.nombre_rol not in roles_permitidos_eliminar:
                return JsonResponse({
                    'error': f'No se puede eliminar usuarios con rol de {usuario.id_rol.nombre_rol}'
                }, status=400)
            
            # Verificar si el usuario tiene denuncias asociadas
            denuncias_asociadas = Denuncia.objects.filter(id_usuario=usuario_id)
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
    """API de login específica para Ionic - Adaptada para Supabase"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({'success': False, 'error': 'Email y contraseña requeridos'}, status=400)
            
            print(f"🔐 Intentando login para: {email}")
            
            # PRIMERO: Intentar autenticar como Usuario (trabajador)
            user = authenticate(request, username=email, password=password)
            
            if user is not None and user.is_active:
                # ✅ Es un trabajador (Usuario)
                print(f"✅ Login exitoso como trabajador: {user.nombre_usuario}")
                
                user_data = {
                    'id_usuario': user.id_usuario,
                    'nombre_usuario': user.nombre_usuario,
                    'apellido_pat_usuario': user.apellido_pat_usuario,
                    'apellido_mat_usuario': user.apellido_mat_usuario,
                    'correo_electronico_usuario': user.correo_electronico_usuario,
                    'telefono_movil_usuario': user.telefono_movil_usuario,
                    'id_rol': user.id_rol.id_rol,
                    'nombre_rol': user.id_rol.nombre_rol,
                    'is_active': user.is_active,
                    'tipo_usuario': 'trabajador'
                }
                
                return JsonResponse({
                    'success': True, 
                    'user': user_data,
                    'message': 'Login exitoso como trabajador'
                })
            
            # SEGUNDO: Intentar autenticar como Ciudadano desde Supabase
            try:
                ciudadano = Ciudadano.objects.get(
                    correo_electronico_ciudadano=email,
                    is_active_ciudadano=True
                )
                
                # Como Supabase maneja autenticación, podrías necesitar:
                # 1. Llamar a la API de Supabase Auth, O
                # 2. Usar una contraseña hasheada consistente
                
                # Opción temporal: verificar contraseña directamente
                # EN PRODUCCIÓN: Implementar autenticación con Supabase Auth
                if ciudadano.contraseña_ciudadano == password:
                    print(f"✅ Login exitoso como ciudadano: {ciudadano.nombre_ciudadano}")
                    
                    ciudadano_data = {
                        'id_ciudadano': ciudadano.id_ciudadano,
                        'nombre_ciudadano': ciudadano.nombre_ciudadano,
                        'apellido_pat_ciudadano': ciudadano.apellido_pat_ciudadano,
                        'apellido_mat_ciudadano': ciudadano.apellido_mat_ciudadano,
                        'correo_electronico_ciudadano': ciudadano.correo_electronico_ciudadano,
                        'telefono_movil_ciudadano': ciudadano.telefono_movil_ciudadano,
                        'id_rol': 3,
                        'nombre_rol': 'ciudadano',
                        'is_active': ciudadano.is_active_ciudadano,
                        'tipo_usuario': 'ciudadano'
                    }
                    
                    # Actualizar último inicio de sesión
                    ciudadano.ultimo_inicio_ciudadano = timezone.now()
                    ciudadano.save()
                    
                    return JsonResponse({
                        'success': True, 
                        'user': ciudadano_data,
                        'message': 'Login exitoso como ciudadano'
                    })
                else:
                    print("❌ Contraseña incorrecta para ciudadano")
                    return JsonResponse({
                        'success': False, 
                        'error': 'Credenciales inválidas'
                    }, status=401)
                    
            except Ciudadano.DoesNotExist:
                print("❌ Ciudadano no encontrado o inactivo")
                return JsonResponse({
                    'success': False, 
                    'error': 'Credenciales inválidas'
                }, status=401)
                
        except Exception as e:
            print(f"❌ Error en login: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Método no permitido'
    }, status=405)

@csrf_exempt
def api_register_ciudadano(request):
    """API para registro de ciudadanos - Adaptada para Supabase"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"📥 Datos recibidos para registro: {data}")
            
            # Validar campos requeridos
            required_fields = [
                'rut_ciudadano', 'nombre_ciudadano', 'apellido_pat_ciudadano',
                'apellido_mat_ciudadano', 'correo_electronico_ciudadano',
                'telefono_movil_ciudadano', 'contraseña_ciudadano'
            ]
            
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False, 
                        'error': f'El campo {field} es requerido'
                    }, status=400)
            
            # Validaciones de formato
            rut_valido = re.match(r'^\d{7,8}-[\dkK]$', data['rut_ciudadano'])
            if not rut_valido:
                return JsonResponse({
                    'success': False,
                    'error': 'El RUT debe tener formato: 12345678-9'
                }, status=400)
            
            email_valido = re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', data['correo_electronico_ciudadano'])
            if not email_valido:
                return JsonResponse({
                    'success': False,
                    'error': 'El correo electrónico no tiene un formato válido'
                }, status=400)
            
            # Verificar duplicados en Supabase
            if Ciudadano.objects.filter(correo_electronico_ciudadano=data['correo_electronico_ciudadano']).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'El correo electrónico ya está registrado'
                }, status=400)
            
            if Ciudadano.objects.filter(rut_ciudadano=data['rut_ciudadano']).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'El RUT ya está registrado'
                }, status=400)
            
            # EN PRODUCCIÓN: Hashear contraseña antes de guardar
            # from django.contrib.auth.hashers import make_password
            # contraseña_hasheada = make_password(data['contraseña_ciudadano'])
            
            # Crear ciudadano en Supabase
            ciudadano = Ciudadano.objects.create(
                rut_ciudadano=data['rut_ciudadano'],
                nombre_ciudadano=data['nombre_ciudadano'],
                apellido_pat_ciudadano=data['apellido_pat_ciudadano'],
                apellido_mat_ciudadano=data['apellido_mat_ciudadano'],
                correo_electronico_ciudadano=data['correo_electronico_ciudadano'],
                telefono_movil_ciudadano=data['telefono_movil_ciudadano'],
                contraseña_ciudadano=data['contraseña_ciudadano'],  # Hashear en producción
                is_active_ciudadano=True
            )
            
            print(f"✅ Ciudadano registrado exitosamente en Supabase: {ciudadano.nombre_ciudadano}")
            
            return JsonResponse({
                'success': True,
                'message': 'Ciudadano registrado correctamente',
                'ciudadano': {
                    'id_ciudadano': ciudadano.id_ciudadano,
                    'nombre_completo': f"{ciudadano.nombre_ciudadano} {ciudadano.apellido_pat_ciudadano}",
                    'correo_electronico_ciudadano': ciudadano.correo_electronico_ciudadano,
                    'rut_ciudadano': ciudadano.rut_ciudadano
                }
            }, status=201)
            
        except Exception as e:
            print(f"❌ Error en registro de ciudadano: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error al registrar en la base de datos: {str(e)}'
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
                'id_usuario', 'id_ciudadano', 'id_requerimiento_id'
            )
            data = []
            for denuncia in denuncias:
                data.append({
                    'id_denuncia': denuncia.id_denuncia,
                    'hora_denuncia': denuncia.hora_denuncia.isoformat(),
                    'fecha_denuncia': denuncia.fecha_denuncia.isoformat(),
                    'id_ciudadano': denuncia.id_ciudadano.id_ciudadano,
                    'nombre_ciudadano': f"{denuncia.id_ciudadano.nombre_ciudadano} {denuncia.id_ciudadano.apellido_pat_ciudadano}",
                    'direccion_denuncia': denuncia.direccion_denuncia,
                    'detalle_denuncia': denuncia.detalle_denuncia,
                    'estado_denuncia': denuncia.estado_denuncia,
                    'id_requerimiento': denuncia.id_requerimiento_id.id_requerimiento,
                    'nombre_requerimiento': denuncia.id_requerimiento_id.nombre_requerimiento_denuncia,
                    'visibilidad_camaras_denuncia': denuncia.visibilidad_camaras_denuncia,
                    'labor_realizada_denuncia': denuncia.labor_realizada_denuncia,
                    'fecha_creacion_denuncia': denuncia.fecha_creacion_denuncia.isoformat() if denuncia.fecha_creacion_denuncia else None
                })
            return JsonResponse({'success': True, 'denuncias': data})
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            # Validar campos requeridos
            campos_requeridos = [
                'hora_denuncia', 'fecha_denuncia', 'id_ciudadano', 'direccion_denuncia',
                'id_requerimiento_id', 'detalle_denuncia', 'id_usuario'
            ]
            for campo in campos_requeridos:
                if not data.get(campo):
                    return JsonResponse({'success': False, 'error': f'Campo {campo} es requerido'}, status=400)
            
            # Crear denuncia
            denuncia = Denuncia.objects.create(
                hora_denuncia=data['hora_denuncia'],
                fecha_denuncia=data['fecha_denuncia'],
                id_ciudadano_id=data['id_ciudadano'],
                direccion_denuncia=data['direccion_denuncia'],
                direccion_denuncia_1=data.get('direccion_denuncia_1', ''),
                cuadrante_denuncia=data.get('cuadrante_denuncia', 0),
                id_requerimiento_id_id=data['id_requerimiento_id'],
                detalle_denuncia=data['detalle_denuncia'],
                id_usuario_id=data['id_usuario'],
                visibilidad_camaras_denuncia=data.get('visibilidad_camaras_denuncia', False),
                labor_realizada_denuncia=data.get('labor_realizada_denuncia', ''),
                hora_llegada_movil_denuncia=data.get('hora_llegada_movil_denuncia'),
                estado_denuncia=data.get('estado_denuncia', 'Recibido')
            )
            
            return JsonResponse({
                'success': True,
                'denuncia': {
                    'id_denuncia': denuncia.id_denuncia,
                    'estado_denuncia': denuncia.estado_denuncia,
                    'fecha_creacion_denuncia': denuncia.fecha_creacion_denuncia.isoformat()
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