from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator

class RolManager(BaseUserManager):
    def create_user(self, correo_electronico_usuario, password=None, **extra_fields):
        if not correo_electronico_usuario:
            raise ValueError('El correo electrónico es obligatorio')
        
        campos_permitidos = [
            'rut_usuario', 'nombre_usuario', 'apellido_pat_usuario', 
            'apellido_mat_usuario', 'telefono_movil_usuario', 'id_rol', 
            'id_turno', 'is_active'
        ]
        
        filtered_fields = {k: v for k, v in extra_fields.items() 
                          if k in campos_permitidos}
        
        correo = self.normalize_email(correo_electronico_usuario)
        user = self.model(correo_electronico_usuario=correo, **filtered_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'Seguridad_roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre_rol

class Turnos(models.Model):
    id_turno = models.AutoField(primary_key=True)
    nombre_turno = models.CharField(max_length=50, unique=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        db_table = 'Seguridad_turnos'
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'

    def __str__(self):
        return self.nombre_turno

class Ciudadano(models.Model):
    id_ciudadano = models.AutoField(primary_key=True)
    rut_ciudadano = models.CharField(max_length=10, unique=True)
    nombre_ciudadano = models.CharField(max_length=100)
    apellido_pat_ciudadano = models.CharField(max_length=225)
    apellido_mat_ciudadano = models.CharField(max_length=100)
    correo_electronico_ciudadano = models.CharField(max_length=100, unique=True)
    telefono_movil_ciudadano = models.CharField(max_length=13)
    fecha_creacion_ciudadano = models.DateTimeField(default=timezone.now)
    fecha_actualizacion_ciudadano = models.DateTimeField(auto_now=True)
    contraseña_ciudadano = models.CharField(max_length=225)
    ultimo_inicio_ciudadano = models.DateTimeField(null=True, blank=True)
    is_active_ciudadano = models.BooleanField(default=True)

    class Meta:
        db_table = 'Seguridad_ciudadano'
        verbose_name = 'Ciudadano'
        verbose_name_plural = 'Ciudadanos'

    def __str__(self):
        return f"{self.nombre_ciudadano} {self.apellido_pat_ciudadano}"

class Usuario(AbstractBaseUser):
    # Validadores
    rut_validator = RegexValidator(
        regex=r'^\d{7,8}-[\dkK]$',
        message='El RUT debe tener el formato: 12345678-9'
    )
    telefono_validator = RegexValidator(
        regex=r'^\+?56?9?\d{8}$',
        message='El teléfono debe tener formato: +56912345678'
    )
    
    # Campos básicos
    id_usuario = models.AutoField(primary_key=True)
    rut_usuario = models.CharField(
        max_length=12, 
        unique=True, 
        validators=[rut_validator],
        help_text='Formato: 12345678-9'
    )
    nombre_usuario = models.CharField(max_length=100)
    apellido_pat_usuario = models.CharField(max_length=100)
    apellido_mat_usuario = models.CharField(max_length=100)
    correo_electronico_usuario = models.EmailField(max_length=254, unique=True)
    telefono_movil_usuario = models.CharField(
        max_length=20, 
        validators=[telefono_validator]
    )
    
    # Relaciones
    id_rol = models.ForeignKey(Roles, on_delete=models.PROTECT, db_column='id_rol')
    id_turno = models.ForeignKey(Turnos, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_turno')
    
    # Campos de control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Campos para authentication
    USERNAME_FIELD = 'correo_electronico_usuario'
    REQUIRED_FIELDS = ['rut_usuario', 'nombre_usuario', 'apellido_pat_usuario']
    
    objects = RolManager()
    
    # ✅ MÉTODOS REQUERIDOS PARA DJANGO AUTH
    def has_perm(self, perm, obj=None):
        """
        ¿El usuario tiene un permiso específico?
        Solo los administradores tienen todos los permisos
        """
        return self.id_rol_id == 1  # ID 1 = Administrador
    
    def has_module_perms(self, app_label):
        """
        ¿El usuario tiene permisos para ver la app en el admin?
        Solo los administradores pueden acceder al admin
        """
        return self.id_rol_id == 1  # ID 1 = Administrador
    
    # ✅ PROPERTY PARA COMPATIBILIDAD CON DJANGO ADMIN
    @property
    def is_staff(self):
        """
        Django admin usa esta propiedad para determinar si puede acceder al admin
        Solo los administradores son considerados "staff"
        """
        return self.id_rol_id == 1  # ID 1 = Administrador
    
    def __str__(self):
        return f"{self.nombre_usuario} {self.apellido_pat_usuario} - {self.rut_usuario}"
    
    def get_full_name(self):
        return f"{self.nombre_usuario} {self.apellido_pat_usuario} {self.apellido_mat_usuario}"
    
    def get_short_name(self):
        return self.nombre_usuario
    
    class Meta:
        db_table = 'Seguridad_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class TiposVehiculos(models.Model):
    id_tipo_vehiculo = models.AutoField(primary_key=True)
    nombre_tipo_vehiculo = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'Seguridad_tiposvehiculos'
        verbose_name = 'Tipo de Vehículo'
        verbose_name_plural = 'Tipos de Vehículos'

    def __str__(self):
        return self.nombre_tipo_vehiculo

class Vehiculos(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    patente_vehiculo = models.CharField(max_length=10, unique=True)
    marca_vehiculo = models.CharField(max_length=50)
    modelo_vehiculo = models.CharField(max_length=50)
    codigo_vehiculo = models.CharField(max_length=10)
    estado_vehiculo = models.CharField(max_length=20)
    total_kilometraje = models.IntegerField(default=0)  # NUEVO CAMPO
    fecha_creacion = models.DateTimeField(default=timezone.now)
    id_tipo_vehiculo = models.ForeignKey(TiposVehiculos, on_delete=models.PROTECT, db_column='id_tipo_vehiculo_id')

    class Meta:
        db_table = 'Seguridad_vehiculos'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f"{self.patente_vehiculo} - {self.marca_vehiculo} {self.modelo_vehiculo}"

class Radio(models.Model):
    id_radio = models.AutoField(primary_key=True)
    nombre_radio = models.CharField(max_length=50, unique=True)
    codigo_radio = models.CharField(max_length=20, unique=True)
    descripcion_radio = models.TextField()
    estado_radio = models.CharField(max_length=20)
    fecha_creacion_radio = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Seguridad_radio'
        verbose_name = 'Radio'
        verbose_name_plural = 'Radios'

    def __str__(self):
        return self.nombre_radio

class AsignacionRadio(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_radio = models.ForeignKey(Radio, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Seguridad_asignacion_radio'
        verbose_name = 'Asignación de Radio'
        verbose_name_plural = 'Asignaciones de Radio'
        unique_together = (('id_usuario', 'id_radio', 'fecha_asignacion'),)

    def __str__(self):
        return f"Radio {self.id_radio} - {self.id_usuario} - {self.fecha_asignacion}"

class AsignacionVehiculo(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_vehiculo = models.ForeignKey(Vehiculos, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    kilometraje_inicial = models.IntegerField()  # NUEVO CAMPO
    kilometraje_recorrido = models.IntegerField(default=0)  # NUEVO CAMPO

    class Meta:
        db_table = 'Seguridad_asignacion_vehiculo'
        verbose_name = 'Asignación de Vehículo'
        verbose_name_plural = 'Asignaciones de Vehículo'
        unique_together = (('id_usuario', 'id_vehiculo', 'fecha_asignacion'),)

    def __str__(self):
        return f"Vehículo {self.id_vehiculo} - {self.id_usuario} - {self.fecha_asignacion}"

class FamiliaDenuncia(models.Model):
    id_familia_denuncia = models.AutoField(primary_key=True)
    nombre_familia_denuncia = models.CharField(max_length=100, unique=True)
    codigo_familia = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'Seguridad_familiadenuncia'
        verbose_name = 'Familia de Denuncia'
        verbose_name_plural = 'Familias de Denuncia'

    def __str__(self):
        return self.nombre_familia_denuncia

class GrupoDenuncia(models.Model):
    id_grupo_denuncia = models.AutoField(primary_key=True)
    nombre_grupo_denuncia = models.CharField(max_length=100)
    codigo_grupo = models.CharField(max_length=10)
    id_familia_denuncia = models.ForeignKey(FamiliaDenuncia, on_delete=models.PROTECT, db_column='id_familia_denuncia_id')

    class Meta:
        db_table = 'Seguridad_grupodenuncia'
        verbose_name = 'Grupo de Denuncia'
        verbose_name_plural = 'Grupos de Denuncia'
        unique_together = (('id_familia_denuncia', 'codigo_grupo'),)

    def __str__(self):
        return self.nombre_grupo_denuncia

class SubgrupoDenuncia(models.Model):
    id_subgrupo_denuncia = models.AutoField(primary_key=True)
    nombre_subgrupo_denuncia = models.CharField(max_length=100)
    codigo_subgrupo = models.CharField(max_length=10)
    id_grupo_denuncia = models.ForeignKey(GrupoDenuncia, on_delete=models.PROTECT, db_column='id_grupo_denuncia_id')

    class Meta:
        db_table = 'Seguridad_subgrupodenuncia'
        verbose_name = 'Subgrupo de Denuncia'
        verbose_name_plural = 'Subgrupos de Denuncia'
        unique_together = (('id_grupo_denuncia', 'codigo_subgrupo'),)

    def __str__(self):
        return self.nombre_subgrupo_denuncia

class Requerimiento(models.Model):
    id_requerimiento = models.AutoField(primary_key=True)
    nombre_requerimiento = models.CharField(max_length=200)
    codigo_requerimiento = models.CharField(max_length=10)
    clasificacion_requerimiento = models.CharField(max_length=10)
    descripcion_requerimiento = models.TextField()
    id_subgrupo_denuncia = models.ForeignKey(SubgrupoDenuncia, on_delete=models.PROTECT, db_column='id_subgrupo_denuncia_id')

    class Meta:
        db_table = 'Seguridad_requerimiento'
        verbose_name = 'Requerimiento'
        verbose_name_plural = 'Requerimientos'
        unique_together = (('id_subgrupo_denuncia', 'codigo_requerimiento'),)

    def __str__(self):
        return self.nombre_requerimiento

class ServiciosEmergencia(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_servicio = models.CharField(max_length=100, unique=True)
    codigo_servicio = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'Seguridad_serviciosemergencia'
        verbose_name = 'Servicio de Emergencia'
        verbose_name_plural = 'Servicios de Emergencia'

    def __str__(self):
        return self.nombre_servicio

class Denuncia(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    id_denuncia = models.AutoField(primary_key=True)
    hora_denuncia = models.DateTimeField()
    fecha_denuncia = models.DateField()
    direccion_denuncia = models.CharField(max_length=100)
    direccion_denuncia_1 = models.CharField(max_length=225)
    cuadrante_denuncia = models.IntegerField()
    detalle_denuncia = models.TextField()
    visibilidad_camaras_denuncia = models.BooleanField()
    hora_llegada_movil_denuncia = models.DateTimeField()
    labor_realizada_denuncia = models.TextField()
    termino_evento = models.DateTimeField(null=True, blank=True)
    tiempo_total_procedimiento_denuncia = models.IntegerField(null=True, blank=True)
    estado_denuncia = models.CharField(max_length=100, choices=ESTADO_CHOICES)
    fecha_creacion_denuncia = models.DateTimeField(default=timezone.now)
    fecha_actualizacion_denuncia = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='denuncias_registradas')
    id_ciudadano = models.ForeignKey(Ciudadano, on_delete=models.PROTECT)
    id_requerimiento = models.ForeignKey(Requerimiento, on_delete=models.PROTECT, db_column='id_requerimiento_denuncia')

    class Meta:
        db_table = 'Seguridad_denuncia'
        verbose_name = 'Denuncia'
        verbose_name_plural = 'Denuncias'

    def __str__(self):
        return f"Denuncia {self.id_denuncia} - {self.fecha_denuncia}"

class MovilesDenuncia(models.Model):
    id_movil_denuncia = models.AutoField(primary_key=True)
    orden_asignacion = models.IntegerField()
    hora_asignacion = models.DateTimeField()
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    id_denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, db_column='id_denuncia_id')
    id_vehiculo = models.ForeignKey(Vehiculos, on_delete=models.PROTECT, db_column='id_vehiculo_id')
    id_conductor = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='id_conductor_id')

    class Meta:
        db_table = 'Seguridad_movilesdenuncia'
        verbose_name = 'Móvil de Denuncia'
        verbose_name_plural = 'Móviles de Denuncia'
        unique_together = (('id_denuncia', 'orden_asignacion'),)

    def __str__(self):
        return f"Móvil {self.orden_asignacion} - Denuncia {self.id_denuncia_id}"

class DerivacionesDenuncia(models.Model):
    TIPO_DERIVACION_CHOICES = [
        ('emergencia', 'Emergencia'),
        ('especializada', 'Especializada'),
        ('seguimiento', 'Seguimiento'),
    ]

    id_derivacion = models.AutoField(primary_key=True)
    tipo_derivacion = models.CharField(max_length=20, choices=TIPO_DERIVACION_CHOICES)
    hora_derivacion = models.DateTimeField()
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    id_denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, db_column='id_denuncia_id')
    id_servicio = models.ForeignKey(ServiciosEmergencia, on_delete=models.PROTECT, null=True, blank=True, db_column='id_servicio_id')
    id_conductor = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, db_column='id_conductor_id')

    class Meta:
        db_table = 'Seguridad_derivacionesdenuncia'
        verbose_name = 'Derivación de Denuncia'
        verbose_name_plural = 'Derivaciones de Denuncia'

    def __str__(self):
        return f"Derivación {self.id_derivacion} - {self.tipo_derivacion}"

class AsignacionDerivacionEmergencia(models.Model):
    id_servicio = models.ForeignKey(ServiciosEmergencia, on_delete=models.CASCADE)
    id_derivacion = models.ForeignKey(DerivacionesDenuncia, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField()
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Seguridad_asignacion_derivacion_emergencia'
        verbose_name = 'Asignación de Derivación de Emergencia'
        verbose_name_plural = 'Asignaciones de Derivación de Emergencia'
        unique_together = (('id_servicio', 'id_derivacion', 'fecha_asignacion'),)

    def __str__(self):
        return f"Derivación {self.id_derivacion} - Servicio {self.id_servicio}"

class SolicitudCiudadano(models.Model):
    ESTADO_SOLICITUD_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    id_solicitud = models.AutoField(primary_key=True)
    tipo_solicitante = models.CharField(max_length=100)
    nombre_solicitante = models.CharField(max_length=225)
    telefono_solicitante = models.CharField(max_length=20, blank=True, null=True)
    correo_solicitante = models.CharField(max_length=225)
    rut_solicitante = models.CharField(max_length=20)
    direccion_solicitante = models.TextField()
    detalle_solicitud = models.TextField()
    estado_solicitud = models.CharField(max_length=100, choices=ESTADO_SOLICITUD_CHOICES)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    id_ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE, db_column='id_ciudadano_id')

    class Meta:
        db_table = 'Seguridad_solicitud_ciudadano'
        verbose_name = 'Solicitud de Ciudadano'
        verbose_name_plural = 'Solicitudes de Ciudadanos'

    def __str__(self):
        return f"Solicitud {self.id_solicitud} - {self.nombre_solicitante}"

class SolicitudTrabajador(models.Model):
    ESTADO_SOLICITUD_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    id_solicitud_trabajador = models.AutoField(primary_key=True)
    rol_solicitante = models.CharField(max_length=100)
    nombre_solicitante_trabajador = models.CharField(max_length=225)
    telefono_solicitante_trabajador = models.CharField(max_length=20, blank=True, null=True)
    correo_solicitante_trabajador = models.CharField(max_length=225)
    rut_solicitante_trabajador = models.CharField(max_length=20)
    direccion_solicitante_trabajador = models.TextField()
    detalle_solicitud_trabajador = models.TextField()
    estado_solicitud_trabajador = models.CharField(max_length=100, choices=ESTADO_SOLICITUD_CHOICES)
    fecha_creacion_trabajador = models.DateTimeField(default=timezone.now)
    turno_solicitante_trabajador = models.DateField()
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario_id')

    class Meta:
        db_table = 'Seguridad_solicitud_trabajador'
        verbose_name = 'Solicitud de Trabajador'
        verbose_name_plural = 'Solicitudes de Trabajadores'

    def __str__(self):
        return f"Solicitud Trabajador {self.id_solicitud_trabajador} - {self.nombre_solicitante_trabajador}"

class DocumentoSolicitud(models.Model):
    id_documento = models.AutoField(primary_key=True)
    nombre_archivo = models.CharField(max_length=225)
    tipo_archivo = models.CharField(max_length=50)
    ruta_archivo = models.CharField(max_length=500)
    tamaño_archivo = models.IntegerField(null=True, blank=True)
    fecha_subida = models.DateTimeField(default=timezone.now)
    id_solicitud = models.ForeignKey(SolicitudCiudadano, on_delete=models.CASCADE, db_column='id_solicitud_id')

    class Meta:
        db_table = 'Seguridad_documento_solicitud'
        verbose_name = 'Documento de Solicitud'
        verbose_name_plural = 'Documentos de Solicitud'

    def __str__(self):
        return self.nombre_archivo

class Fiscalizacion(models.Model):
    id_fiscalizacion = models.AutoField(primary_key=True)
    hora_fiscalizacion = models.DateTimeField()
    tipo_fiscalizacion = models.CharField(max_length=100)
    detalle_fiscalizacion = models.TextField()
    nombre_conductor = models.CharField(max_length=225)
    apellido_conductor = models.CharField(max_length=225)
    rut_conductor = models.CharField(max_length=20)
    patente_vehiculo_fiscalizacion = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='id_usuario_id')

    class Meta:
        db_table = 'Seguridad_fiscalizacion'
        verbose_name = 'Fiscalización'
        verbose_name_plural = 'Fiscalizaciones'

    def __str__(self):
        return f"Fiscalización {self.id_fiscalizacion} - {self.patente_vehiculo_fiscalizacion}"