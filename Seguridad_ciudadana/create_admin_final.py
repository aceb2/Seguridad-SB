import os
import sys

# Configurar Django
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Seguridad_ciudadana.settings')

import django
django.setup()

from Seguridad.models import Usuario, Roles
from django.contrib.auth.hashers import make_password

print("🔧 Iniciando creación de usuario administrador...")

try:
    # 1. Verificar o crear rol administrador
    rol_admin, created = Roles.objects.get_or_create(
        id_rol=1,
        defaults={'nombre_rol': 'administrador'}
    )
    
    if created:
        print("✅ Rol administrador creado")
    else:
        print(f"✅ Rol administrador encontrado: {rol_admin.nombre_rol}")
    
    # 2. Eliminar usuario existente si existe
    usuarios_eliminados = Usuario.objects.filter(rut_usuario='123456789').delete()[0]
    if usuarios_eliminados > 0:
        print("✅ Usuario existente eliminado")
    
    # 3. Crear nuevo usuario administrador
    admin_user = Usuario(
        rut_usuario='123456789',
        nombre_usuario='Administrador',
        apellido_pat_usuario='Sistema', 
        apellido_mat_usuario='Principal',
        correo_electronico_usuario='admin@municipalidad.cl',
        telefono_movil_usuario='+56912345678',
        password=make_password('admin123'),
        is_active=True,
        id_rol=1
    )
    
    admin_user.save()
    
    print("🎉 USUARIO ADMINISTRADOR CREADO EXITOSAMENTE!")
    print("═" * 50)
    print(f"📧 EMAIL: admin@municipalidad.cl")
    print(f"🔑 CONTRASEÑA: admin123")
    print(f"👤 RUT: 123456789")
    print("═" * 50)
    print("🌐 Ve a: http://localhost:8000/admin/")
    print("💡 Usa el EMAIL como usuario para hacer login")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Posibles soluciones:")
    print("   1. Verifica que tu models.py no tenga django.setup()")
    print("   2. Revisa que todos los imports en models.py sean correctos")