// ✏️ SISTEMA PARA ACTUALIZAR USUARIOS (CORREGIDO)

// Variables globales para actualizar usuario
let todosLosUsuariosActualizar = [];
let usuarioSeleccionadoActualizar = null;

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Módulo de actualizar usuarios inicializado');
    inicializarEventListenersActualizar();
});

// ✅ INICIALIZAR EVENT LISTENERS PARA ACTUALIZAR
function inicializarEventListenersActualizar() {
    // Formatear teléfono en edición
    const telefonoInput = document.getElementById('editar-telefono');
    if (telefonoInput) {
        telefonoInput.addEventListener('input', formatearTelefonoChilenoActualizar);
        telefonoInput.addEventListener('blur', validarTelefonoEnTiempoRealActualizar);
    }

    // Filtrar turnos cuando cambie el rol en edición
    const rolSelect = document.getElementById('editar-rol');
    if (rolSelect) {
        rolSelect.addEventListener('change', filtrarTurnosPorRolEdicion);
    }

    // Validación de contraseñas en edición
    const nuevaPasswordInput = document.getElementById('nueva-password');
    const confirmarPasswordInput = document.getElementById('confirmar-nueva-password');
    
    if (nuevaPasswordInput && confirmarPasswordInput) {
        nuevaPasswordInput.addEventListener('input', actualizarIndicadorPasswordEdicion);
        confirmarPasswordInput.addEventListener('input', actualizarIndicadorPasswordEdicion);
    }
}

// ✅ ABRIR MODAL ACTUALIZAR USUARIO
async function abrirModalActualizarUsuario() {
    console.log('✏️ Abriendo modal para actualizar usuario...');
    
    try {
        document.getElementById('modal-actualizar-usuario').style.display = 'block';
        resetearModalActualizarUsuario();
        await cargarUsuariosParaActualizar();
        console.log('✅ Modal de actualizar usuario listo');
        
    } catch (error) {
        console.error('❌ Error al abrir modal de actualizar usuario:', error);
        mostrarError('Error al cargar los usuarios: ' + error.message);
    }
}

// ✅ CERRAR MODAL ACTUALIZAR
function cerrarModalActualizarUsuario() {
    console.log('❌ Cerrando modal de actualizar usuario...');
    document.getElementById('modal-actualizar-usuario').style.display = 'none';
}

// ✅ RESETEAR MODAL ACTUALIZAR
function resetearModalActualizarUsuario() {
    console.log('🔄 Reseteando modal de actualizar usuario...');
    
    usuarioSeleccionadoActualizar = null;
    document.getElementById('form-actualizar-usuario').reset();
    document.getElementById('buscar-usuario-actualizar').value = '';
    document.getElementById('info-usuario-seleccionado').style.display = 'none';
    document.getElementById('form-edicion-usuario').style.display = 'none';
    document.getElementById('btn-actualizar-usuario').disabled = true;
    document.getElementById('lista-usuarios-actualizar').innerHTML = '';
    
    // Resetear indicadores de contraseña
    const strengthBars = document.querySelectorAll('#form-edicion-usuario .strength-bar');
    const strengthTexts = document.querySelectorAll('#form-edicion-usuario .password-strength small');
    const matchTexts = document.querySelectorAll('#form-edicion-usuario .password-match small');
    
    if (strengthBars.length > 0) {
        strengthBars.forEach(bar => {
            bar.style.width = '0%';
            bar.style.backgroundColor = '#6c757d';
        });
        
        strengthTexts.forEach(text => {
            text.textContent = 'La contraseña debe tener al menos 8 caracteres';
            text.style.color = '#6c757d';
        });
        
        matchTexts.forEach(text => {
            text.textContent = 'Las contraseñas deben coincidir';
            text.style.color = '#6c757d';
        });
    }
}

// ✅ CARGAR USUARIOS PARA ACTUALIZAR (EXCLUYENDO CIUDADANOS)
async function cargarUsuariosParaActualizar() {
    try {
        console.log('📥 Cargando usuarios para actualizar...');
        
        // Mostrar loading
        document.getElementById('lista-usuarios-actualizar').innerHTML = `
            <div class="usuario-item-search" style="text-align: center; padding: 20px;">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <p>Cargando usuarios...</p>
            </div>
        `;

        const response = await fetch('/api/usuarios/');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const usuarios = await response.json();
        
        // ✅ FILTRAR: Excluir usuarios con rol "Ciudadano"
        todosLosUsuariosActualizar = usuarios.filter(usuario => 
            usuario.rol_nombre !== 'Ciudadano' && usuario.rol_nombre !== 'Ciudadano'
        );
        
        renderizarListaBusquedaActualizar(todosLosUsuariosActualizar);
        console.log(`✅ ${todosLosUsuariosActualizar.length} usuarios cargados para actualizar (excluyendo ciudadanos)`);
        
    } catch (error) {
        console.error('❌ Error cargando usuarios para actualizar:', error);
        document.getElementById('lista-usuarios-actualizar').innerHTML = `
            <div class="usuario-item-search" style="text-align: center; color: #dc3545; padding: 20px;">
                <i class="fa-solid fa-exclamation-triangle"></i>
                <p>Error al cargar usuarios</p>
                <small>${error.message}</small>
                <br>
                <button onclick="cargarUsuariosParaActualizar()" class="btn-actualizar-usuario" style="margin-top: 10px; padding: 5px 10px;">
                    <i class="fa-solid fa-refresh"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// ✅ RENDERIZAR LISTA DE BÚSQUEDA PARA ACTUALIZAR
function renderizarListaBusquedaActualizar(usuarios) {
    const lista = document.getElementById('lista-usuarios-actualizar');
    
    if (!usuarios || usuarios.length === 0) {
        lista.innerHTML = `
            <div class="usuario-item-search" style="text-align: center; padding: 20px; color: #6c757d;">
                <i class="fa-solid fa-users-slash"></i>
                <p>No hay usuarios disponibles para editar</p>
                <small>Los usuarios con rol "Ciudadano" no se pueden editar desde aquí</small>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    usuarios.forEach(usuario => {
        const rolClass = getRolClassActualizar(usuario.rol_nombre);
        const estadoClass = usuario.estado_usuario ? 'estado-activo' : 'estado-inactivo';
        const estadoTexto = usuario.estado_usuario ? 'Activo' : 'Inactivo';
        
        html += `
            <div class="usuario-item-search" data-id="${usuario.id_usuario}" onclick="seleccionarUsuarioActualizar(${usuario.id_usuario})">
                <div class="usuario-info-search">
                    <div>
                        <div class="usuario-nombre-search">${usuario.nombre_usuario} ${usuario.apellido_pat_usuario}</div>
                        <div class="usuario-email-search">${usuario.correo_electronico_usuario}</div>
                        <div style="font-size: 0.8em; color: #6c757d; margin-top: 5px;">
                            <span class="${estadoClass}" style="padding: 2px 6px; border-radius: 8px; font-size: 0.7em;">${estadoTexto}</span>
                            • ${usuario.rut_usuario}
                        </div>
                    </div>
                    <span class="rol-badge ${rolClass}">${usuario.rol_nombre}</span>
                </div>
            </div>
        `;
    });
    
    lista.innerHTML = html;
}

// ✅ BUSCAR USUARIOS PARA ACTUALIZAR (EXCLUYENDO CIUDADANOS)
function buscarUsuariosActualizar() {
    const termino = document.getElementById('buscar-usuario-actualizar').value.toLowerCase();
    
    if (!termino) {
        renderizarListaBusquedaActualizar(todosLosUsuariosActualizar);
        return;
    }
    
    const usuariosFiltrados = todosLosUsuariosActualizar.filter(usuario =>
        usuario.nombre_usuario.toLowerCase().includes(termino) ||
        usuario.apellido_pat_usuario.toLowerCase().includes(termino) ||
        usuario.apellido_mat_usuario.toLowerCase().includes(termino) ||
        usuario.correo_electronico_usuario.toLowerCase().includes(termino) ||
        (usuario.rut_usuario && usuario.rut_usuario.toLowerCase().includes(termino))
    );
    
    renderizarListaBusquedaActualizar(usuariosFiltrados);
}

// ✅ SELECCIONAR USUARIO PARA ACTUALIZAR
function seleccionarUsuarioActualizar(usuarioId) {
    usuarioSeleccionadoActualizar = todosLosUsuariosActualizar.find(u => u.id_usuario === usuarioId);
    
    if (!usuarioSeleccionadoActualizar) {
        mostrarError('Usuario no encontrado');
        return;
    }
    
    // Resaltar elemento seleccionado
    document.querySelectorAll('.usuario-item-search').forEach(item => {
        item.classList.remove('selected');
    });
    
    const elementoSeleccionado = document.querySelector(`.usuario-item-search[data-id="${usuarioId}"]`);
    if (elementoSeleccionado) {
        elementoSeleccionado.classList.add('selected');
    }
    
    mostrarInformacionUsuarioActualizar(usuarioSeleccionadoActualizar);
    document.getElementById('btn-actualizar-usuario').disabled = false;
    
    console.log('✅ Usuario seleccionado para actualizar:', usuarioSeleccionadoActualizar);
}

// ✅ MOSTRAR INFORMACIÓN USUARIO PARA ACTUALIZAR (CORREGIDO)
function mostrarInformacionUsuarioActualizar(usuario) {
    document.getElementById('info-usuario-seleccionado').style.display = 'block';
    document.getElementById('form-edicion-usuario').style.display = 'block';
    
    // Mostrar información actual
    document.getElementById('usuario-nombre-completo').textContent = 
        `${usuario.nombre_usuario} ${usuario.apellido_pat_usuario} ${usuario.apellido_mat_usuario}`;
    document.getElementById('usuario-rut').textContent = usuario.rut_usuario;
    document.getElementById('usuario-correo').textContent = usuario.correo_electronico_usuario;
    document.getElementById('usuario-rol-actual').textContent = usuario.rol_nombre;
    document.getElementById('usuario-rol-actual').className = `rol-badge ${getRolClassActualizar(usuario.rol_nombre)}`;
    
    // ✅ CORREGIDO: Mostrar estado correctamente
    const estadoTexto = usuario.estado_usuario ? 'Activo' : 'Inactivo';
    document.getElementById('usuario-estado-actual').textContent = estadoTexto;
    document.getElementById('usuario-estado-actual').className = `estado-badge ${usuario.estado_usuario ? 'estado-activo' : 'estado-inactivo'}`;
    
    // Llenar formulario de edición
    document.getElementById('editar-nombre').value = usuario.nombre_usuario || '';
    document.getElementById('editar-apellido-pat').value = usuario.apellido_pat_usuario || '';
    document.getElementById('editar-apellido-mat').value = usuario.apellido_mat_usuario || '';
    document.getElementById('editar-rut').value = usuario.rut_usuario || '';
    
    // Formatear teléfono para mostrar
    const telefonoFormateado = formatearTelefonoParaMostrarActualizar(usuario.telefono_movil_usuario);
    document.getElementById('editar-telefono').value = telefonoFormateado;
    
    document.getElementById('editar-correo').value = usuario.correo_electronico_usuario || '';
    document.getElementById('editar-rol').value = usuario.id_rol || '';
    
    // ✅ CORREGIDO: Establecer el valor del estado correctamente
    document.getElementById('editar-estado').value = usuario.estado_usuario ? '1' : '0';
    
    document.getElementById('editar-turno').value = usuario.id_turno || '';
    
    // Aplicar filtro de turnos según el rol seleccionado
    setTimeout(() => {
        filtrarTurnosPorRolEdicion();
    }, 100);
    
    // Limpiar campos de nueva contraseña
    document.getElementById('nueva-password').value = '';
    document.getElementById('confirmar-nueva-password').value = '';
    
    // Resetear indicadores de contraseña
    actualizarIndicadorPasswordEdicion();
    
    // ✅ DEBUG: Verificar valores cargados
    console.log('🔍 DEBUG - Valores cargados en el formulario:');
    console.log('Estado del usuario (original):', usuario.estado_usuario);
    console.log('Valor seleccionado en el select:', document.getElementById('editar-estado').value);
}

// ✅ FORMATEAR TELÉFONO PARA MOSTRAR
function formatearTelefonoParaMostrarActualizar(telefono) {
    if (!telefono) return '';
    
    // Si el teléfono ya tiene formato, mantenerlo
    if (telefono.includes('+')) return telefono;
    
    // Si es un número chileno (9 dígitos), formatear
    const soloNumeros = telefono.replace(/[^0-9]/g, '');
    if (soloNumeros.length === 9 && soloNumeros.startsWith('9')) {
        return `+56 ${soloNumeros.substring(0, 1)} ${soloNumeros.substring(1, 5)} ${soloNumeros.substring(5, 9)}`;
    }
    
    return telefono;
}

// ✅ FORMATEAR TELÉFONO CHILENO EN EDICIÓN
function formatearTelefonoChilenoActualizar(e) {
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

// ✅ VALIDAR TELÉFONO EN TIEMPO REAL EN EDICIÓN
function validarTelefonoEnTiempoRealActualizar(e) {
    const input = e.target;
    const telefono = input.value.replace(/[^0-9]/g, '');
    
    if (!telefono) {
        input.style.borderColor = '#e9ecef';
        return;
    }
    
    // Validar formato chileno: 9XXXXXXXX
    const regexChileno = /^9[0-9]{8}$/;
    const soloNumeros = telefono.startsWith('56') ? telefono.substring(2) : telefono;
    
    if (!regexChileno.test(soloNumeros)) {
        input.style.borderColor = '#dc3545';
    } else {
        input.style.borderColor = '#28a745';
    }
}

// ✅ FILTRAR TURNOS POR ROL EN EDICIÓN (ACTUALIZADO SIN CIUDADANO)
function filtrarTurnosPorRolEdicion() {
    const rolSelect = document.getElementById('editar-rol');
    const turnoSelect = document.getElementById('editar-turno');
    
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

// ✅ ACTUALIZAR INDICADOR DE CONTRASEÑA EN EDICIÓN
function actualizarIndicadorPasswordEdicion() {
    const password = document.getElementById('nueva-password').value;
    const confirmar = document.getElementById('confirmar-nueva-password').value;
    
    const strengthBar = document.querySelector('#form-edicion-usuario .strength-bar');
    const strengthText = document.querySelector('#form-edicion-usuario .password-strength small');
    const matchText = document.querySelector('#form-edicion-usuario .password-match small');
    
    if (!strengthBar || !strengthText || !matchText) return;
    
    // Validar fortaleza solo si hay contraseña
    if (password) {
        const validacion = validarPasswordActualizar(password);
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

// ✅ VALIDAR CONTRASEÑA (VERSIÓN PARA ACTUALIZAR)
function validarPasswordActualizar(password) {
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

// ✅ VALIDAR FORMULARIO ACTUALIZAR
function validarFormularioActualizarUsuario() {
    const nombre = document.getElementById('editar-nombre').value.trim();
    const apellidoPat = document.getElementById('editar-apellido-pat').value.trim();
    const apellidoMat = document.getElementById('editar-apellido-mat').value.trim();
    const telefono = document.getElementById('editar-telefono').value.replace(/[^0-9]/g, '');
    const correo = document.getElementById('editar-correo').value.trim();
    const nuevaPassword = document.getElementById('nueva-password').value;
    const confirmarPassword = document.getElementById('confirmar-nueva-password').value;
    
    let valido = true;
    let mensajesError = [];
    
    // Validar campos requeridos
    if (!nombre || !apellidoPat || !apellidoMat || !telefono || !correo) {
        mensajesError.push('Todos los campos obligatorios deben estar completos');
        valido = false;
    }
    
    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (correo && !emailRegex.test(correo)) {
        mensajesError.push('El formato del correo electrónico no es válido');
        valido = false;
    }
    
    // Validar teléfono
    const soloNumerosTelefono = telefono.startsWith('56') ? telefono.substring(2) : telefono;
    const regexTelefonoChileno = /^9[0-9]{8}$/;
    
    if (telefono && !regexTelefonoChileno.test(soloNumerosTelefono)) {
        mensajesError.push('El teléfono debe tener formato chileno: 9 1234 5678');
        valido = false;
    }
    
    // Validar contraseñas si se están cambiando
    if (nuevaPassword || confirmarPassword) {
        if (nuevaPassword !== confirmarPassword) {
            mensajesError.push('Las nuevas contraseñas no coinciden');
            valido = false;
        }
        
        if (nuevaPassword && nuevaPassword.length < 8) {
            mensajesError.push('La nueva contraseña debe tener al menos 8 caracteres');
            valido = false;
        }
    }
    
    if (!valido) {
        mostrarError(mensajesError.join('<br>'));
    }
    
    return valido;
}

// ✅ ACTUALIZAR USUARIO EXISTENTE (CON DEBUG MEJORADO)
async function actualizarUsuarioExistente(event) {
    event.preventDefault();
    
    if (!usuarioSeleccionadoActualizar) {
        mostrarError('No hay ningún usuario seleccionado para actualizar');
        return;
    }
    
    if (!validarFormularioActualizarUsuario()) {
        return;
    }
    
    try {
        // Mostrar loading
        Swal.fire({
            title: 'Actualizando usuario...',
            text: 'Por favor espere',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Obtener datos del formulario
        const telefonoLimpio = document.getElementById('editar-telefono').value.replace(/[^0-9]/g, '');
        const soloNumerosTelefono = telefonoLimpio.startsWith('56') ? telefonoLimpio.substring(2) : telefonoLimpio;
        
        const estadoSeleccionado = document.getElementById('editar-estado').value;
        
        const datosActualizacion = {
            nombre_usuario: document.getElementById('editar-nombre').value.trim(),
            apellido_pat_usuario: document.getElementById('editar-apellido-pat').value.trim(),
            apellido_mat_usuario: document.getElementById('editar-apellido-mat').value.trim(),
            telefono_movil_usuario: soloNumerosTelefono,
            correo_electronico_usuario: document.getElementById('editar-correo').value.trim(),
            id_rol: parseInt(document.getElementById('editar-rol').value),
            id_turno: document.getElementById('editar-turno').value ? parseInt(document.getElementById('editar-turno').value) : null,
            estado_usuario: estadoSeleccionado === '1'  // ✅ Convertir a boolean
        };
        
        // ✅ DEBUG DETALLADO
        console.log('🔍 DEBUG - Estado del formulario:');
        console.log('Valor del select estado:', estadoSeleccionado);
        console.log('Tipo del valor:', typeof estadoSeleccionado);
        console.log('Estado convertido a boolean:', datosActualizacion.estado_usuario);
        console.log('Tipo del estado convertido:', typeof datosActualizacion.estado_usuario);
        
        console.log('📤 Datos completos que se enviarán:');
        console.log('URL:', `/api/usuarios/${usuarioSeleccionadoActualizar.id_usuario}/`);
        console.log('Datos:', datosActualizacion);
        
        // Agregar nueva contraseña si se proporcionó
        const nuevaPassword = document.getElementById('nueva-password').value;
        if (nuevaPassword) {
            datosActualizacion.password_usuario = nuevaPassword;
            console.log('🔐 Contraseña incluida en la actualización');
        }
        
        // Hacer la petición PUT a la API
        const response = await fetch(`/api/usuarios/${usuarioSeleccionadoActualizar.id_usuario}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(datosActualizacion)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('❌ Error response from API:', errorData);
            throw new Error(errorData.error || `Error ${response.status}`);
        }
        
        const usuarioActualizado = await response.json();
        console.log('✅ Respuesta del servidor:', usuarioActualizado);
        
        // Cerrar loading
        Swal.close();
        
        // Mostrar éxito
        mostrarExito('Usuario actualizado correctamente');
        
        // Cerrar modal
        cerrarModalActualizarUsuario();
        
        // Recargar la lista de usuarios
        if (typeof recargarListaUsuarios === 'function') {
            recargarListaUsuarios();
        }
        
    } catch (error) {
        console.error('❌ Error actualizando usuario:', error);
        Swal.close();
        mostrarError('Error al actualizar el usuario: ' + error.message);
    }
}

// ✅ EDITAR USUARIO DESDE LISTA
function editarUsuarioDesdeLista(usuarioId) {
    abrirModalActualizarUsuario();
    
    // Esperar a que se cargue el modal y luego seleccionar el usuario
    setTimeout(() => {
        const usuario = todosLosUsuariosActualizar.find(u => u.id_usuario === usuarioId);
        if (usuario) {
            seleccionarUsuarioActualizar(usuarioId);
        }
    }, 500);
}

// ✅ FUNCIONES AUXILIARES
function getRolClassActualizar(rolNombre) {
    const roles = {
        'Administrador': 'rol-administrador',
        'Operador': 'rol-operador',
        'Conductor': 'rol-conductor',
        'Inspector': 'rol-inspector',
        'Ciudadano': 'rol-ciudadano'
    };
    return roles[rolNombre] || 'rol-usuario';
}

// ✅ FUNCIONES DE UTILIDAD (compartidas)
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
        html: mensaje,
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