import json
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

""" Ruta del archivo json que esta funcionando como base de datos """
from django.conf import settings
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
