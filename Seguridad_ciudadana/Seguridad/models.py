from django.db import models # type: ignore
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager # type: ignore
from django.core.validators import MinLengthValidator, RegexValidator # type: ignore

class RolManager(BaseUserManager):
    def create_user(self, correo_electronico_usuario, password=None, **extra_fields):
        if not correo_electronico_usuario:
            raise ValueError('El correo electrónico es obligatorio')
        
        # ✅ CORREGIDO: Incluir solo los campos que existen en el modelo Usuario
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

    # ❌ NO USAR create_superuser - lo haremos manualmente
    def create_superuser(self, correo_electronico_usuario, password=None, **extra_fields):
        raise NotImplementedError("Usar create_user con rol Administrador en lugar de create_superuser")

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre_rol
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

class Turnos(models.Model):
    id_turno = models.AutoField(primary_key=True)
    nombre_turno = models.CharField(max_length=50, unique=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    def __str__(self):
        return f"{self.nombre_turno} ({self.hora_inicio} - {self.hora_fin})"
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'

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
    correo_electronico_usuario = models.EmailField(unique=True)
    telefono_movil_usuario = models.CharField(
        max_length=20, 
        validators=[telefono_validator]
    )
    
    # Relaciones
    id_rol = models.ForeignKey(Roles, on_delete=models.PROTECT)
    id_turno = models.ForeignKey(Turnos, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Campos de control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    # ❌ ELIMINADO: is_staff = models.BooleanField(default=False)
    
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
        return self.id_rol.nombre_rol == 'Administrador'
    
    def has_module_perms(self, app_label):
        """
        ¿El usuario tiene permisos para ver la app en el admin?
        Solo los administradores pueden acceder al admin
        """
        return self.id_rol.nombre_rol == 'Administrador'
    
    # ✅ PROPERTY PARA COMPATIBILIDAD CON DJANGO ADMIN
    @property
    def is_staff(self):
        """
        Django admin usa esta propiedad para determinar si puede acceder al admin
        Solo los administradores son considerados "staff"
        """
        return self.id_rol.nombre_rol == 'Administrador'
    
    def __str__(self):
        return f"{self.nombre_usuario} {self.apellido_pat_usuario} - {self.rut_usuario}"
    
    def get_full_name(self):
        return f"{self.nombre_usuario} {self.apellido_pat_usuario} {self.apellido_mat_usuario}"
    
    def get_short_name(self):
        return self.nombre_usuario
    
    @property
    def es_conductor(self):
        return self.id_rol.nombre_rol in ['Conductor', 'Inspector']
    
    @property
    def es_administrador(self):
        return self.id_rol.nombre_rol == 'Administrador'
    
    @property
    def es_operador(self):
        return self.id_rol.nombre_rol == 'Operador'
    
    @property
    def es_ciudadano(self):
        return self.id_rol.nombre_rol == 'Ciudadano'
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class TiposVehiculos(models.Model):
    id_tipo_vehiculo = models.AutoField(primary_key=True)
    nombre_tipo_vehiculo = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre_tipo_vehiculo
    
    class Meta:
        verbose_name = 'Tipo de Vehículo'
        verbose_name_plural = 'Tipos de Vehículos'

class Vehiculos(models.Model):
    ESTADOS_VEHICULO = [
        ('Disponible', 'Disponible'),
        ('En mantención', 'En mantención'),
        ('Asignado', 'Asignado'),
        ('Inactivo', 'Inactivo'),
    ]
    
    id_vehiculo = models.AutoField(primary_key=True)
    patente_vehiculo = models.CharField(max_length=10, unique=True)
    marca_vehiculo = models.CharField(max_length=50)
    modelo_vehiculo = models.CharField(max_length=50)
    codigo_vehiculo = models.CharField(max_length=10)
    id_tipo_vehiculo = models.ForeignKey(TiposVehiculos, on_delete=models.PROTECT)
    estado_vehiculo = models.CharField(max_length=20, choices=ESTADOS_VEHICULO, default='Disponible')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patente_vehiculo} - {self.marca_vehiculo} {self.modelo_vehiculo}"
    
    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

class AsignacionesVehiculos(models.Model):
    id_asignacion_vehiculo = models.AutoField(primary_key=True)
    id_conductor = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT,
        limit_choices_to={'id_rol__nombre_rol__in': ['Conductor', 'Inspector']}
    )
    id_vehiculo = models.ForeignKey(Vehiculos, on_delete=models.PROTECT)
    id_turno = models.ForeignKey(Turnos, on_delete=models.PROTECT)
    fecha_asignacion = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.id_conductor} - {self.id_vehiculo} - {self.fecha_asignacion}"
    
    class Meta:
        verbose_name = 'Asignación de Vehículo'
        verbose_name_plural = 'Asignaciones de Vehículos'
        unique_together = ['id_conductor', 'id_vehiculo', 'fecha_asignacion']

class FamiliaDenuncia(models.Model):
    id_familia_denuncia = models.AutoField(primary_key=True)
    nombre_familia_denuncia = models.CharField(max_length=100, unique=True)
    codigo_familia = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.codigo_familia} - {self.nombre_familia_denuncia}"
    
    class Meta:
        verbose_name = 'Familia de Denuncia'
        verbose_name_plural = 'Familias de Denuncia'

class GrupoDenuncia(models.Model):
    id_grupo_denuncia = models.AutoField(primary_key=True)
    nombre_grupo_denuncia = models.CharField(max_length=100)
    codigo_grupo = models.CharField(max_length=10)
    id_familia_denuncia = models.ForeignKey(FamiliaDenuncia, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.codigo_grupo} - {self.nombre_grupo_denuncia}"
    
    class Meta:
        verbose_name = 'Grupo de Denuncia'
        verbose_name_plural = 'Grupos de Denuncia'
        unique_together = ['id_familia_denuncia', 'codigo_grupo']

class SubgrupoDenuncia(models.Model):
    id_subgrupo_denuncia = models.AutoField(primary_key=True)
    nombre_subgrupo_denuncia = models.CharField(max_length=100)
    codigo_subgrupo = models.CharField(max_length=10)
    id_grupo_denuncia = models.ForeignKey(GrupoDenuncia, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.codigo_subgrupo} - {self.nombre_subgrupo_denuncia}"
    
    class Meta:
        verbose_name = 'Subgrupo de Denuncia'
        verbose_name_plural = 'Subgrupos de Denuncia'
        unique_together = ['id_grupo_denuncia', 'codigo_subgrupo']

class Requerimiento(models.Model):
    CLASIFICACION_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    
    id_requerimiento = models.AutoField(primary_key=True)
    nombre_requerimiento = models.CharField(max_length=200)
    codigo_requerimiento = models.CharField(max_length=10)
    id_subgrupo_denuncia = models.ForeignKey(SubgrupoDenuncia, on_delete=models.PROTECT)
    clasificacion_requerimiento = models.CharField(max_length=10, choices=CLASIFICACION_CHOICES)
    descripcion_requerimiento = models.TextField()
    
    def __str__(self):
        return f"{self.codigo_requerimiento} - {self.nombre_requerimiento} ({self.clasificacion_requerimiento})"
    
    class Meta:
        verbose_name = 'Requerimiento'
        verbose_name_plural = 'Requerimientos'
        unique_together = ['id_subgrupo_denuncia', 'codigo_requerimiento']

class ServiciosEmergencia(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_servicio = models.CharField(max_length=100, unique=True)
    codigo_servicio = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.codigo_servicio} - {self.nombre_servicio}"
    
    class Meta:
        verbose_name = 'Servicio de Emergencia'
        verbose_name_plural = 'Servicios de Emergencia'

class VillasCuadrantes(models.Model):
    id_villa_cuadrante = models.AutoField(primary_key=True)
    nombre_villa = models.CharField(max_length=100)
    cuadrante = models.CharField(max_length=10)
    direccion_referencia = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre_villa} - Cuadrante {self.cuadrante}"
    
    class Meta:
        verbose_name = 'Villa y Cuadrante'
        verbose_name_plural = 'Villas y Cuadrantes'
        unique_together = ['nombre_villa', 'cuadrante']

class Denuncia(models.Model):
    ESTADO_DENUNCIA_CHOICES = [
        ('Recibido', 'Recibido'),
        ('En proceso', 'En proceso'),
        ('Completado', 'Completado'),
    ]
    
    id_denuncia = models.AutoField(primary_key=True)
    
    # Operadores
    id_operador1 = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT,
        related_name='denuncias_operador1',
        limit_choices_to={'id_rol__nombre_rol': 'Operador'}
    )
    id_operador2 = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT,
        related_name='denuncias_operador2',
        limit_choices_to={'id_rol__nombre_rol': 'Operador'},
        null=True,
        blank=True
    )
    
    # Tiempos
    hora_denuncia = models.DateTimeField()
    fecha_denuncia = models.DateField()
    
    # Solicitante
    id_solicitante = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT,
        related_name='denuncias_solicitante'
    )
    
    # Ubicación
    direccion = models.CharField(max_length=200)
    id_villa_cuadrante = models.ForeignKey(VillasCuadrantes, on_delete=models.PROTECT)
    
    # Detalles de denuncia
    id_requerimiento = models.ForeignKey(Requerimiento, on_delete=models.PROTECT)
    detalle_denuncia = models.TextField()
    
    # Información adicional
    visibilidad_camaras_denuncia = models.BooleanField(default=False)
    id_turno = models.ForeignKey(Turnos, on_delete=models.PROTECT)
    
    # Tiempos del procedimiento
    hora_llegada_movil = models.DateTimeField(null=True, blank=True)
    labor_realizada_denuncia = models.TextField()
    termino_evento = models.DateTimeField(null=True, blank=True)
    
    # Cálculos automáticos
    tiempo_total_procedimiento_minutos = models.IntegerField(null=True, blank=True)
    estado_denuncia = models.CharField(
        max_length=20, 
        choices=ESTADO_DENUNCIA_CHOICES, 
        default='Recibido'
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calcular tiempo total si hay hora de llegada y término
        if self.hora_llegada_movil and self.termino_evento:
            diferencia = self.termino_evento - self.hora_llegada_movil
            self.tiempo_total_procedimiento_minutos = int(diferencia.total_seconds() / 60)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Denuncia #{self.id_denuncia} - {self.id_solicitante} - {self.fecha_denuncia}"
    
    @property
    def familia_denuncia(self):
        return self.id_requerimiento.id_subgrupo_denuncia.id_grupo_denuncia.id_familia_denuncia.nombre_familia_denuncia
    
    class Meta:
        verbose_name = 'Denuncia'
        verbose_name_plural = 'Denuncias'

class DerivacionesDenuncia(models.Model):
    TIPO_DERIVACION_CHOICES = [
        ('Primaria', 'Derivación Primaria'),
        ('Adicional', 'Derivación Adicional'),
    ]
    
    id_derivacion = models.AutoField(primary_key=True)
    id_denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE)
    id_servicio = models.ForeignKey(
        ServiciosEmergencia, 
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    id_conductor = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        limit_choices_to={'id_rol__nombre_rol__in': ['Conductor', 'Inspector']},
        null=True,
        blank=True
    )
    tipo_derivacion = models.CharField(
        max_length=20, 
        choices=TIPO_DERIVACION_CHOICES, 
        default='Primaria'
    )
    hora_derivacion = models.DateTimeField()
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        servicio = self.id_servicio.nombre_servicio if self.id_servicio else self.id_conductor
        return f"Derivación {self.tipo_derivacion} - {servicio} - Denuncia #{self.id_denuncia.id_denuncia}"
    
    class Meta:
        verbose_name = 'Derivación de Denuncia'
        verbose_name_plural = 'Derivaciones de Denuncias'

class MovilesDenuncia(models.Model):
    id_movil_denuncia = models.AutoField(primary_key=True)
    id_denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE)
    id_conductor = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT,
        limit_choices_to={'id_rol__nombre_rol__in': ['Conductor', 'Inspector']}
    )
    id_vehiculo = models.ForeignKey(Vehiculos, on_delete=models.PROTECT)
    orden_asignacion = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3')])
    hora_asignacion = models.DateTimeField()
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"Móvil {self.orden_asignacion} - {self.id_conductor} - Denuncia #{self.id_denuncia.id_denuncia}"
    
    class Meta:
        verbose_name = 'Móvil en Denuncia'
        verbose_name_plural = 'Móviles en Denuncias'
        unique_together = ['id_denuncia', 'orden_asignacion']