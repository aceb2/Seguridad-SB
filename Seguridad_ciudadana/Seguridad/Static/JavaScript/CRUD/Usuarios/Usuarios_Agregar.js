// 👥 SISTEMA PARA AGREGAR NUEVOS USUARIOS

// Variables globales para agregar usuario
let rolesDisponibles = [];
let turnosDisponibles = [];

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Módulo de agregar usuarios inicializado');
    inicializarEventListenersAgregar();
});

// ✅ INICIALIZAR EVENT LISTENERS
function inicializarEventListenersAgregar() {
    // Validación en tiempo real de contraseñas
    const passwordInput = document.getElementById('password-usuario');
    const confirmPasswordInput = document.getElementById('confirmar-password');
    
    if (passwordInput && confirmPasswordInput) {
        passwordInput.addEventListener('input', actualizarIndicadorPassword);
        confirmPasswordInput.addEventListener('input', actualizarIndicadorPassword);
    }
    
    // Formatear RUT automáticamente
    const rutInput = document.getElementById('rut-usuario');
    if (rutInput) {
        rutInput.addEventListener('input', formatearRUT);
        rutInput.addEventListener('blur', validarRUTEnTiempoReal);
    }
    
    // Formatear teléfono
    const telefonoInput = document.getElementById('telefono-usuario');
    if (telefonoInput) {
        telefonoInput.addEventListener('input', formatearTelefonoChileno);
        telefonoInput.addEventListener('blur', validarTelefonoEnTiempoReal);
    }

    // Filtrar turnos cuando cambie el rol
    const rolSelect = document.getElementById('rol-usuario');
    if (rolSelect) {
        rolSelect.addEventListener('change', filtrarTurnosPorRol);
    }
}

// ✅ ABRIR MODAL DE AGREGAR USUARIO
async function abrirModalAgregarUsuario() {
    console.log('👤 Abriendo modal para agregar usuario...');
    
    try {
        document.getElementById('modal-agregar-usuario').style.display = 'block';
        resetearFormularioAgregar();
        await cargarDatosInicialesAgregar();
        console.log('✅ Modal de agregar usuario listo');
        
    } catch (error) {
        console.error('❌ Error al abrir modal de agregar usuario:', error);
        mostrarError('Error al cargar los datos: ' + error.message);
    }
}

// ✅ CERRAR MODAL AGREGAR
function cerrarModalAgregarUsuario() {
    console.log('❌ Cerrando modal de agregar usuario...');
    document.getElementById('modal-agregar-usuario').style.display = 'none';
}

// ✅ RESETEAR FORMULARIO AGREGAR
function resetearFormularioAgregar() {
    console.log('🔄 Reseteando formulario de agregar usuario...');
    
    document.getElementById('form-agregar-usuario').reset();
    
    // Resetear indicadores de contraseña
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.password-strength small');
    const matchText = document.querySelector('.password-match small');
    
    if (strengthBar) strengthBar.style.width = '0%';
    if (strengthBar) strengthBar.style.backgroundColor = '#6c757d';
    if (strengthText) strengthText.textContent = 'La contraseña debe tener al menos 8 caracteres';
    if (strengthText) strengthText.style.color = '#6c757d';
    if (matchText) matchText.textContent = 'Las contraseñas deben coincidir';
    if (matchText) matchText.style.color = '#6c757d';
}

// ✅ CARGAR DATOS INICIALES PARA AGREGAR (ACTUALIZADO)
async function cargarDatosInicialesAgregar() {
    try {
        console.log('📥 Cargando datos para formulario de agregar usuario...');
        
        // ✅ ACTUALIZADO: Roles permitidos para crear (sin Ciudadano)
        rolesDisponibles = [
            { id: 1, nombre: 'Administrador' },
            { id: 2, nombre: 'Operador' },
            { id: 4, nombre: 'Conductor' },
            { id: 5, nombre: 'Inspector' }
        ];
        
        console.log('✅ Datos para agregar usuario cargados correctamente');
        
    } catch (error) {
        console.error('❌ Error cargando datos para agregar:', error);
        throw error;
    }
}

// ✅ VALIDAR RUT CHILENO (MEJORADO)
function validarRUT(rut) {
    if (!rut || typeof rut !== 'string') return false;
    
    // Limpiar RUT y convertir a mayúsculas
    rut = rut.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (rut.length < 2) return false;
    
    const cuerpo = rut.slice(0, -1);
    const dv = rut.slice(-1);
    
    // Validar que el cuerpo sean solo números
    if (!/^\d+$/.test(cuerpo)) return false;
    
    // Calcular DV
    let suma = 0;
    let multiplo = 2;
    
    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo.charAt(i)) * multiplo;
        multiplo = multiplo === 7 ? 2 : multiplo + 1;
    }
    
    const dvEsperado = 11 - (suma % 11);
    const dvCalculado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : dvEsperado.toString();
    
    return dvCalculado === dv;
}

// ✅ FORMATEAR RUT CHILENO (MEJORADO)
function formatearRUT(e) {
    let input = e.target;
    let value = input.value.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (value.length === 0) return;
    
    // Separar cuerpo y dígito verificador
    let cuerpo = value.slice(0, -1);
    let dv = value.slice(-1);
    
    // Formatear cuerpo con puntos
    if (cuerpo.length > 0) {
        cuerpo = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }
    
    // Unir cuerpo y DV con guión
    input.value = cuerpo + (dv ? '-' + dv : '');
}

// ✅ VALIDAR RUT EN TIEMPO REAL
function validarRUTEnTiempoReal(e) {
    const input = e.target;
    const rut = input.value;
    const errorElement = document.getElementById('rut-error') || crearElementoError(input, 'rut-error');
    
    if (!rut) {
        ocultarError(errorElement);
        return;
    }
    
    if (!validarRUT(rut)) {
        mostrarErrorInput(input, errorElement, 'El RUT ingresado no es válido');
    } else {
        ocultarError(errorElement);
        input.style.borderColor = '#28a745';
    }
}

// ✅ FORMATEAR TELÉFONO CHILENO (MEJORADO)
function formatearTelefonoChileno(e) {
    let input = e.target;
    let value = input.value.replace(/[^0-9]/g, '');
    
    // Si empieza con 9, asumimos que es chileno y agregamos +56
    if (value.startsWith('9') && value.length >= 9) {
        value = '56' + value;
    }
    
    // Limitar a 11 dígitos (9 + 56)
    value = value.substring(0, 11);
    
    // Formatear: +56 9 1234 5678
    let formatted = '';
    if (value.length > 0) {
        formatted = '+';
        if (value.length > 0) formatted += value.substring(0, 2); // 56
        if (value.length > 2) formatted += ' ' + value.substring(2, 3); // 9
        if (value.length > 3) formatted += ' ' + value.substring(3, 7); // 1234
        if (value.length > 7) formatted += ' ' + value.substring(7, 11); // 5678
    }
    
    input.value = formatted;
}

// ✅ VALIDAR TELÉFONO EN TIEMPO REAL
function validarTelefonoEnTiempoReal(e) {
    const input = e.target;
    const telefono = input.value.replace(/[^0-9]/g, '');
    const errorElement = document.getElementById('telefono-error') || crearElementoError(input, 'telefono-error');
    
    if (!telefono) {
        ocultarError(errorElement);
        return;
    }
    
    // Validar formato chileno: 9XXXXXXXX
    const regexChileno = /^9[0-9]{8}$/;
    const soloNumeros = telefono.startsWith('56') ? telefono.substring(2) : telefono;
    
    if (!regexChileno.test(soloNumeros)) {
        mostrarErrorInput(input, errorElement, 'El teléfono debe tener formato: 9 1234 5678');
    } else {
        ocultarError(errorElement);
        input.style.borderColor = '#28a745';
    }
}

// ✅ VALIDAR CONTRASEÑA
function validarPassword(password) {
    const fortaleza = {
        longitud: password.length >= 8,
        mayuscula: /[A-Z]/.test(password),
        minuscula: /[a-z]/.test(password),
        numero: /[0-9]/.test(password),
        especial: /[^A-Za-z0-9]/.test(password)
    };
    
    const criteriosCumplidos = Object.values(fortaleza).filter(Boolean).length;
    let fuerza = 0;
    let mensaje = '';
    let color = '';
    
    if (criteriosCumplidos <= 2) {
        fuerza = 33;
        mensaje = 'Débil';
        color = '#dc3545';
    } else if (criteriosCumplidos <= 4) {
        fuerza = 66;
        mensaje = 'Media';
        color = '#ffc107';
    } else {
        fuerza = 100;
        mensaje = 'Fuerte';
        color = '#28a745';
    }
    
    return { fuerza, mensaje, color, fortaleza };
}

// ✅ ACTUALIZAR INDICADOR DE CONTRASEÑA
function actualizarIndicadorPassword() {
    const password = document.getElementById('password-usuario').value;
    const confirmar = document.getElementById('confirmar-password').value;
    
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.password-strength small');
    const matchText = document.querySelector('.password-match small');
    
    if (!strengthBar || !strengthText || !matchText) return;
    
    // Validar fortaleza
    if (password) {
        const validacion = validarPassword(password);
        strengthBar.style.width = validacion.fuerza + '%';
        strengthBar.style.backgroundColor = validacion.color;
        strengthText.textContent = `Fortaleza: ${validacion.mensaje}`;
        strengthText.style.color = validacion.color;
    } else {
        strengthBar.style.width = '0%';
        strengthBar.style.backgroundColor = '#6c757d';
        strengthText.textContent = 'La contraseña debe tener al menos 8 caracteres';
        strengthText.style.color = '#6c757d';
    }
    
    // Validar coincidencia
    if (confirmar) {
        if (password === confirmar) {
            matchText.textContent = '✓ Las contraseñas coinciden';
            matchText.style.color = '#28a745';
        } else {
            matchText.textContent = '✗ Las contraseñas no coinciden';
            matchText.style.color = '#dc3545';
        }
    } else {
        matchText.textContent = 'Las contraseñas deben coincidir';
        matchText.style.color = '#6c757d';
    }
}

// ✅ VALIDAR FORMULARIO COMPLETO
function validarFormularioAgregarUsuario() {
    const formulario = document.getElementById('form-agregar-usuario');
    const camposRequeridos = formulario.querySelectorAll('[required]');
    let valido = true;
    
    // Validar campos requeridos
    camposRequeridos.forEach(campo => {
        if (!campo.value.trim()) {
            valido = false;
            campo.style.borderColor = '#dc3545';
        } else {
            campo.style.borderColor = '#28a745';
        }
    });
    
    // Validar RUT
    const rut = document.getElementById('rut-usuario').value;
    if (rut && !validarRUT(rut)) {
        valido = false;
        document.getElementById('rut-usuario').style.borderColor = '#dc3545';
        mostrarError('El RUT ingresado no es válido');
    }
    
    // Validar email
    const email = document.getElementById('correo-usuario').value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
        valido = false;
        document.getElementById('correo-usuario').style.borderColor = '#dc3545';
        mostrarError('El formato del correo electrónico no es válido');
    }
    
    // Validar teléfono
    const telefono = document.getElementById('telefono-usuario').value.replace(/[^0-9]/g, '');
    const soloNumerosTelefono = telefono.startsWith('56') ? telefono.substring(2) : telefono;
    const regexTelefonoChileno = /^9[0-9]{8}$/;
    
    if (telefono && !regexTelefonoChileno.test(soloNumerosTelefono)) {
        valido = false;
        document.getElementById('telefono-usuario').style.borderColor = '#dc3545';
        mostrarError('El teléfono debe tener formato chileno: 9 1234 5678');
    }
    
    // Validar contraseñas
    const password = document.getElementById('password-usuario').value;
    const confirmar = document.getElementById('confirmar-password').value;
    
    if (password !== confirmar) {
        valido = false;
        document.getElementById('confirmar-password').style.borderColor = '#dc3545';
        mostrarError('Las contraseñas no coinciden');
    }
    
    // Validar fortaleza de contraseña
    if (password) {
        const validacion = validarPassword(password);
        if (validacion.fuerza < 66) {
            valido = false;
            document.getElementById('password-usuario').style.borderColor = '#ffc107';
            mostrarError('La contraseña es demasiado débil. Use mayúsculas, números y caracteres especiales');
        }
    }
    
    if (password.length < 8) {
        valido = false;
        document.getElementById('password-usuario').style.borderColor = '#dc3545';
        mostrarError('La contraseña debe tener al menos 8 caracteres');
    }
    
    return valido;
}

// ✅ FILTRAR TURNOS SEGÚN ROL (ACTUALIZADO SIN CIUDADANO)
function filtrarTurnosPorRol() {
    const rolSelect = document.getElementById('rol-usuario');
    const turnoSelect = document.getElementById('turno-usuario');
    
    if (!rolSelect || !turnoSelect) return;
    
    const rolSeleccionado = parseInt(rolSelect.value);
    const turnoActual = turnoSelect.value;
    
    // Mostrar todos los turnos temporalmente
    for (let i = 0; i < turnoSelect.options.length; i++) {
        turnoSelect.options[i].style.display = '';
        turnoSelect.options[i].disabled = false;
    }
    
    // ✅ ACTUALIZADO: Si es Inspector (rol 5), mostrar solo turnos de inspectores
    if (rolSeleccionado === 5) {
        for (let i = 0; i < turnoSelect.options.length; i++) {
            const option = turnoSelect.options[i];
            const value = parseInt(option.value);
            // Mostrar solo turnos 4 y 5 (inspectores)
            if (value !== 4 && value !== 5 && value !== '') {
                option.style.display = 'none';
                option.disabled = true;
            }
        }
        // Si el turno actual no es válido para inspector, resetear
        if (turnoActual && turnoActual !== '4' && turnoActual !== '5') {
            turnoSelect.value = '';
        }
    }
    // ✅ ACTUALIZADO: Para Conductores (rol 4) y otros roles (1, 2), mostrar solo turnos generales
    else if (rolSeleccionado) {
        for (let i = 0; i < turnoSelect.options.length; i++) {
            const option = turnoSelect.options[i];
            const value = parseInt(option.value);
            // Mostrar solo turnos 1, 2, 3 (generales)
            if (value !== 1 && value !== 2 && value !== 3 && value !== '') {
                option.style.display = 'none';
                option.disabled = true;
            }
        }
        // Si el turno actual no es válido, resetear
        if (turnoActual && turnoActual !== '1' && turnoActual !== '2' && turnoActual !== '3') {
            turnoSelect.value = '';
        }
    }
}

// ✅ FUNCIONES AUXILIARES PARA MANEJO DE ERRORES
function crearElementoError(input, id) {
    const errorElement = document.createElement('div');
    errorElement.id = id;
    errorElement.className = 'error-message';
    errorElement.style.color = '#dc3545';
    errorElement.style.fontSize = '0.8em';
    errorElement.style.marginTop = '5px';
    errorElement.style.display = 'none';
    
    input.parentNode.appendChild(errorElement);
    return errorElement;
}

function mostrarErrorInput(input, errorElement, mensaje) {
    input.style.borderColor = '#dc3545';
    errorElement.textContent = mensaje;
    errorElement.style.display = 'block';
}

function ocultarError(errorElement) {
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

// ✅ GUARDAR NUEVO USUARIO
async function guardarUsuario(event) {
    event.preventDefault();
    console.log('💾 Intentando guardar nuevo usuario...');
    
    if (!validarFormularioAgregarUsuario()) {
        console.error('❌ Validación de formulario falló');
        return;
    }
    
    try {
        // Mostrar loading
        Swal.fire({
            title: 'Creando usuario...',
            text: 'Por favor espere',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Obtener datos del formulario
        const telefonoLimpio = document.getElementById('telefono-usuario').value.replace(/[^0-9]/g, '');
        const soloNumerosTelefono = telefonoLimpio.startsWith('56') ? telefonoLimpio.substring(2) : telefonoLimpio;
        
        const datosUsuario = {
            nombre_usuario: document.getElementById('nombre-usuario').value.trim(),
            apellido_pat_usuario: document.getElementById('apellido-pat-usuario').value.trim(),
            apellido_mat_usuario: document.getElementById('apellido-mat-usuario').value.trim(),
            rut_usuario: document.getElementById('rut-usuario').value.replace(/[^0-9kK]/g, '').toUpperCase(),
            telefono_movil_usuario: soloNumerosTelefono,
            correo_electronico_usuario: document.getElementById('correo-usuario').value.trim(),
            password_usuario: document.getElementById('password-usuario').value,
            id_rol: parseInt(document.getElementById('rol-usuario').value),
            id_turno: document.getElementById('turno-usuario').value ? parseInt(document.getElementById('turno-usuario').value) : null,
            estado_usuario: document.getElementById('estado-usuario').value === '1'
        };
        
        console.log('📤 Datos del usuario a guardar:', datosUsuario);
        
        // Hacer la petición POST a la API
        const response = await fetch('/api/usuarios/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(datosUsuario)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}`);
        }
        
        const usuarioCreado = await response.json();
        console.log('✅ Usuario creado:', usuarioCreado);
        
        // Cerrar loading
        Swal.close();
        
        // Mostrar éxito
        mostrarExito('Usuario creado correctamente');
        
        // Cerrar modal
        cerrarModalAgregarUsuario();
        
        // Recargar la lista de usuarios
        if (typeof recargarListaUsuarios === 'function') {
            recargarListaUsuarios();
        }
        
    } catch (error) {
        console.error('❌ Error creando usuario:', error);
        Swal.close();
        mostrarError('Error al crear el usuario: ' + error.message);
    }
}

// ✅ FUNCIONES DE UTILIDAD
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function mostrarError(mensaje) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: mensaje,
        confirmButtonText: 'Aceptar'
    });
}

function mostrarExito(mensaje) {
    Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: mensaje,
        confirmButtonText: 'Aceptar',
        timer: 3000
    });
}