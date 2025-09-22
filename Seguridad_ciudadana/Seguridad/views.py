import json
import os
from datetime import datetime
import uuid
from django.shortcuts import render, redirect # type: ignore
from django.conf import settings # type: ignore
from django.http import HttpResponse, JsonResponse # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.contrib.auth.hashers import make_password, check_password # type: ignore

""" Ruta del archivo json que esta funcionando como base de datos """
JSON_PATH = os.path.join(settings.BASE_DIR, 'DB/data.json')

# Función para cargar datos
def cargar_datos():
    file_path = settings.JSON_FILE_PATH
    if not os.path.exists(file_path):
        return {"Rutas_Vehiculos": [], "alertas": []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"Rutas_Vehiculos": [], "alertas": []}

# Función para guardar datos
def guardar_datos(data):
    with open(settings.JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# Vista para listar alertas
def listar_alertas(request):
    data = cargar_datos()
    return JsonResponse(data["alertas"], safe=False)


# Create your views here.

def index(request):
    return render(request, 'index.html')

# CRUD de las Alertas
def agregar_alerta(request):
    if request.method == "POST":
        # Procesar el formulario POST
        data = cargar_datos()
        alertas = data["alertas"]

        # Crear ID autoincremental
        new_id = max(a["id"] for a in alertas) + 1 if alertas else 1
        nueva_alerta = {
            "id": new_id,
            "tipo": request.POST.get("tipo"),
            "descripcion": request.POST.get("descripcion")
        }

        alertas.append(nueva_alerta)
        guardar_datos(data)
        return JsonResponse({"status": "ok", "alerta": nueva_alerta})
    
    elif request.method == "GET":
        # Especifica la ruta completa del template
        return render(request, 'CRUD/Alertas/Agregar-alerta.html')
    
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)
    


#CRUD de las Rutas

def agregar_ruta_view(request):
    if request.method == 'POST':
        # Procesar el formulario aquí
        pass
    return render(request, 'CRUD/Rutas/Agregar_ruta.html')

@csrf_exempt
def agregar_ruta(request):
    if request.method == "POST":
        try:
            # Tu código para procesar el POST aquí
            data = cargar_datos()
            
            nueva_ruta = {
                "id": len(data["Rutas_Vehiculos"]) + 1,
                "nombre": request.POST.get("nombre"),
                "vehiculo_asignado": request.POST.get("vehiculo_asignado"),
                "vehiculo_patente": request.POST.get("vehiculo_patente"),
                "vehiculo_capacidad": request.POST.get("vehiculo_capacidad"),
                "coordenada_inicio": {
                    "lat": float(request.POST.get("lat_inicio", 0)),
                    "lng": float(request.POST.get("lng_inicio", 0))
                },
                "coordenadas_termino": {
                    "lat": float(request.POST.get("lat_fin", 0)),
                    "lng": float(request.POST.get("lng_fin", 0))
                }
            }
            
            data["Rutas_Vehiculos"].append(nueva_ruta)
            guardar_datos(data)
            
            return JsonResponse({"status": "success", "ruta": nueva_ruta})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    
    elif request.method == "GET":
        # Renderizar el formulario HTML para GET
        return render(request, 'CRUD/Rutas/Agregar_ruta.html')
    
    else:
        return JsonResponse({"status": "error", "message": "Método no permitido"})

def obtener_rutas_json(request):
    try:
        file_path = settings.JSON_FILE_PATH
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return JsonResponse(data["Rutas_Vehiculos"], safe=False)
        else:
            return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def listar_rutas(request):
    file_path = settings.JSON_FILE_PATH
    if not os.path.exists(file_path):
        return JsonResponse({"error": "File not found"}, status=404)
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        context = {'rutas': data['Rutas_Vehiculos']}
        return render(request, 'CRUD/Rutas/Listar_ruta.html', context)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#Vistas Usuarios

# Funciones para usuarios
def cargar_usuarios():
    return cargar_json(USERS_FILE_PATH, {"usuarios": []})

def guardar_usuarios(data):
    guardar_json(USERS_FILE_PATH, data)

# Funciones para sesiones
def cargar_sesiones():
    return cargar_json(SESSION_FILE_PATH, {"sesiones": []})

def guardar_sesiones(data):
    guardar_json(SESSION_FILE_PATH, data)

def crear_sesion(request, email, nombre, apellido):
    sesiones = cargar_sesiones()
    
    # Eliminar sesiones expiradas
    ahora = datetime.now().isoformat()
    sesiones["sesiones"] = [s for s in sesiones["sesiones"] 
                           if datetime.fromisoformat(s["expira"]) > datetime.fromisoformat(ahora)]
    
    # Crear nueva sesión
    session_id = str(uuid.uuid4())
    nueva_sesion = {
        "session_id": session_id,
        "email": email,
        "nombre": nombre,
        "apellido": apellido,
        "creada": ahora,
        "expira": (datetime.now() + timedelta(hours=24)).isoformat()
    }
    
    sesiones["sesiones"].append(nueva_sesion)
    guardar_sesiones(sesiones)
    
    # Guardar en cookie
    response = HttpResponse()
    response.set_cookie(
        'session_id', 
        session_id, 
        max_age=24*60*60,
        httponly=True
    )
    return response

def verificar_sesion(request):
    session_id = request.COOKIES.get('session_id')
    if not session_id:
        return None
    
    sesiones = cargar_sesiones()
    ahora = datetime.now().isoformat()
    
    # Buscar sesión válida
    sesion_valida = next((s for s in sesiones["sesiones"] 
                         if s["session_id"] == session_id and 
                         datetime.fromisoformat(s["expira"]) > datetime.fromisoformat(ahora)), None)
    
    return sesion_valida

def eliminar_sesion(request):
    session_id = request.COOKIES.get('session_id')
    if session_id:
        sesiones = cargar_sesiones()
        sesiones["sesiones"] = [s for s in sesiones["sesiones"] if s["session_id"] != session_id]
        guardar_sesiones(sesiones)
    
    response = HttpResponse()
    response.delete_cookie('session_id')
    return response

# Middleware personalizado para verificar sesión
def usuario_autenticado(request):
    return verificar_sesion(request) is not None

# Vistas de autenticación
def iniciar_sesion(request):
    if usuario_autenticado(request):
        return redirect('index')
    
    if request.method == 'POST':
        try:
            data = cargar_usuarios()
            usuarios = data["usuarios"]
            
            email = request.POST.get("email")
            password = request.POST.get("password")
            
            usuario = next((user for user in usuarios if user['email'] == email), None)
            
            if usuario and check_password(password, usuario['password']):
                response = crear_sesion(request, email, usuario['nombre'], usuario['apellido'])
                response['Content-Type'] = 'application/json'
                response.content = json.dumps({
                    "status": "success", 
                    "message": "Login exitoso",
                    "redirect": "/"
                })
                return response
            else:
                return JsonResponse({
                    "status": "error", 
                    "message": "Credenciales incorrectas"
                })
                
        except Exception as e:
            return JsonResponse({
                "status": "error", 
                "message": f"Error: {str(e)}"
            })
    
    return render(request, 'Usuario/Inicio.html')

def registrar(request):
    if usuario_autenticado(request):
        return redirect('index')
    
    if request.method == 'POST':
        try:
            data = cargar_usuarios()
            usuarios = data["usuarios"]
            
            email = request.POST.get("email")
            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            
            # Validaciones
            if not all([email, nombre, apellido, password, confirm_password]):
                return JsonResponse({
                    "status": "error", 
                    "message": "Todos los campos son requeridos"
                })
            
            if password != confirm_password:
                return JsonResponse({
                    "status": "error", 
                    "message": "Las contraseñas no coinciden"
                })
            
            if len(password) < 6:
                return JsonResponse({
                    "status": "error", 
                    "message": "La contraseña debe tener al menos 6 caracteres"
                })
            
            # Verificar si el usuario ya existe
            if any(user['email'] == email for user in usuarios):
                return JsonResponse({
                    "status": "error", 
                    "message": "El usuario ya existe"
                })
            
            nuevo_usuario = {
                "email": email,
                "nombre": nombre,
                "apellido": apellido,
                "password": make_password(password),
                "fecha_registro": datetime.now().isoformat()
            }
            
            usuarios.append(nuevo_usuario)
            guardar_usuarios(data)
            
            # Auto-login después del registro
            response = crear_sesion(request, email, nombre, apellido)
            response['Content-Type'] = 'application/json'
            response.content = json.dumps({
                "status": "success", 
                "message": "Usuario registrado correctamente",
                "redirect": "/"
            })
            return response
            
        except Exception as e:
            return JsonResponse({
                "status": "error", 
                "message": f"Error: {str(e)}"
            })
    
    return render(request, 'Usuario/Registro.html')

def cerrar_sesion(request):
    response = eliminar_sesion(request)
    response['Content-Type'] = 'application/json'
    response.content = json.dumps({
        "status": "success", 
        "message": "Sesión cerrada",
        "redirect": "/Login/"
    })
    return response

# Decorador para proteger vistas
def requerir_autenticacion(view_func):
    def wrapper(request, *args, **kwargs):
        if not usuario_autenticado(request):
            return redirect('Inicio')
        return view_func(request, *args, **kwargs)
    return wrapper