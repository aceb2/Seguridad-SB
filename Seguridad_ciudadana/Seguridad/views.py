from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import login, authenticate, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.http import JsonResponse # type: ignore
from django.utils import timezone # type: ignore
from .models import Usuario, Denuncia, Vehiculos, AsignacionesVehiculos, Roles, Turnos
import json

# Vistas básicas de autenticación
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

def cerrar_sesion(request):
    logout(request)
    return redirect('index')

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
    return render(request, 'admin/dashboard.html', context)

@login_required
def operador_dashboard(request):
    if not request.user.es_operador:
        return redirect('index')
    return render(request, 'operador/dashboard.html')

@login_required
def conductor_dashboard(request):
    if not request.user.es_conductor:
        return redirect('index')
    return render(request, 'conductor/dashboard.html')

@login_required
def civil_dashboard(request):
    if not request.user.es_ciudadano:
        return redirect('index')
    return render(request, 'civil/dashboard.html')

# Vistas de alertas (placeholder - necesitarías crear el modelo Alerta)
@login_required
def listar_alertas(request):
    # Placeholder - necesitas crear el modelo Alerta primero
    alertas = []  # Alerta.objects.all()
    return render(request, 'alertas/listar.html', {'alertas': alertas})

@login_required
def agregar_alerta(request):
    if request.method == 'POST':
        # Lógica para agregar alerta
        return redirect('listar_alertas')
    return render(request, 'alertas/agregar.html')

# Vistas de rutas (placeholder - necesitarías crear el modelo Ruta)
@login_required
def listar_rutas(request):
    # Placeholder - necesitas crear el modelo Ruta primero
    rutas = []  # RutaVehiculo.objects.all()
    return render(request, 'rutas/listar.html', {'rutas': rutas})

@login_required
def agregar_ruta_view(request):
    return render(request, 'rutas/agregar.html')

@login_required
def agregar_ruta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Lógica para agregar ruta
            return JsonResponse({'success': True, 'message': 'Ruta agregada correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def obtener_rutas_json(request):
    # Placeholder - devolver rutas en JSON
    rutas = []  # Convertir RutaVehiculo.objects.all() a JSON
    return JsonResponse({'rutas': rutas})

# Vistas adicionales para el sistema de denuncias
@login_required
def listar_denuncias(request):
    if request.user.es_administrador or request.user.es_operador:
        denuncias = Denuncia.objects.all().order_by('-fecha_denuncia')
    else:
        denuncias = Denuncia.objects.filter(id_solicitante=request.user).order_by('-fecha_denuncia')
    
    return render(request, 'denuncias/listar.html', {'denuncias': denuncias})

@login_required
def crear_denuncia(request):
    if not request.user.es_ciudadano:
        return redirect('index')
    
    if request.method == 'POST':
        # Lógica para crear denuncia
        return redirect('listar_denuncias')
    
    return render(request, 'denuncias/crear.html')