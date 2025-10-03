from django.contrib import admin # type: ignore
from django.contrib.auth.admin import UserAdmin # type: ignore
from .models import (
    Roles, Turnos, TiposVehiculos, Usuario, Vehiculos, AsignacionesVehiculos,
    FamiliaDenuncia, GrupoDenuncia, SubgrupoDenuncia, Requerimiento,
    ServiciosEmergencia, VillasCuadrantes, Denuncia, DerivacionesDenuncia, MovilesDenuncia
)

# Configuración personalizada para el admin de Usuario
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut_usuario', 'nombre_usuario', 'apellido_pat_usuario', 'correo_electronico_usuario', 'id_rol', 'id_turno', 'is_active')
    list_filter = ('id_rol', 'id_turno', 'is_active')
    search_fields = ('rut_usuario', 'nombre_usuario', 'apellido_pat_usuario', 'correo_electronico_usuario')
    ordering = ('apellido_pat_usuario', 'nombre_usuario')
    
    fieldsets = (
        (None, {'fields': ('rut_usuario', 'correo_electronico_usuario', 'password')}),
        ('Información Personal', {'fields': ('nombre_usuario', 'apellido_pat_usuario', 'apellido_mat_usuario', 'telefono_movil_usuario')}),
        ('Permisos', {'fields': ('id_rol', 'id_turno', 'is_active', 'is_staff', 'is_superuser')}),
        ('Fechas importantes', {'fields': ('last_login', 'fecha_creacion', 'fecha_actualizacion')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut_usuario', 'nombre_usuario', 'apellido_pat_usuario', 'correo_electronico_usuario', 'password1', 'password2', 'id_rol', 'id_turno'),
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'last_login')

# Registros simples para modelos básicos
admin.site.register(Roles)
admin.site.register(Turnos)
admin.site.register(TiposVehiculos)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Vehiculos)

# Configuración para modelos relacionados
class AsignacionesVehiculosAdmin(admin.ModelAdmin):
    list_display = ('id_conductor', 'id_vehiculo', 'id_turno', 'fecha_asignacion')
    list_filter = ('id_turno', 'fecha_asignacion')
    search_fields = ('id_conductor__nombre_usuario', 'id_vehiculo__patente_vehiculo')

admin.site.register(AsignacionesVehiculos, AsignacionesVehiculosAdmin)

# Configuración para el sistema de denuncias
class GrupoDenunciaInline(admin.TabularInline):
    model = GrupoDenuncia
    extra = 1

class SubgrupoDenunciaInline(admin.TabularInline):
    model = SubgrupoDenuncia
    extra = 1

class RequerimientoInline(admin.TabularInline):
    model = Requerimiento
    extra = 1

class FamiliaDenunciaAdmin(admin.ModelAdmin):
    inlines = [GrupoDenunciaInline]
    list_display = ('nombre_familia_denuncia', 'codigo_familia')

class GrupoDenunciaAdmin(admin.ModelAdmin):
    inlines = [SubgrupoDenunciaInline]
    list_display = ('nombre_grupo_denuncia', 'codigo_grupo', 'id_familia_denuncia')
    list_filter = ('id_familia_denuncia',)

class SubgrupoDenunciaAdmin(admin.ModelAdmin):
    inlines = [RequerimientoInline]
    list_display = ('nombre_subgrupo_denuncia', 'codigo_subgrupo', 'id_grupo_denuncia')
    list_filter = ('id_grupo_denuncia__id_familia_denuncia', 'id_grupo_denuncia')

class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre_requerimiento', 'codigo_requerimiento', 'clasificacion_requerimiento', 'id_subgrupo_denuncia')
    list_filter = ('clasificacion_requerimiento', 'id_subgrupo_denuncia__id_grupo_denuncia__id_familia_denuncia')
    search_fields = ('nombre_requerimiento', 'codigo_requerimiento')

# Configuración para derivaciones y móviles en línea
class DerivacionesDenunciaInline(admin.TabularInline):
    model = DerivacionesDenuncia
    extra = 1

class MovilesDenunciaInline(admin.TabularInline):
    model = MovilesDenuncia
    extra = 1

class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('id_denuncia', 'fecha_denuncia', 'id_solicitante', 'id_requerimiento', 'id_villa_cuadrante', 'id_turno')
    list_filter = ('fecha_denuncia', 'id_requerimiento__clasificacion_requerimiento', 'id_turno', 'id_villa_cuadrante')
    search_fields = ('id_solicitante__nombre_usuario', 'direccion', 'detalle_denuncia')
    inlines = [DerivacionesDenunciaInline, MovilesDenunciaInline]
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'tiempo_total_procedimiento_minutos')

# Registro de modelos de denuncias
admin.site.register(FamiliaDenuncia, FamiliaDenunciaAdmin)
admin.site.register(GrupoDenuncia, GrupoDenunciaAdmin)
admin.site.register(SubgrupoDenuncia, SubgrupoDenunciaAdmin)
admin.site.register(Requerimiento, RequerimientoAdmin)
admin.site.register(ServiciosEmergencia)
admin.site.register(VillasCuadrantes)
admin.site.register(Denuncia, DenunciaAdmin)
admin.site.register(DerivacionesDenuncia)
admin.site.register(MovilesDenuncia)