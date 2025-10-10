// ✏️ SISTEMA PARA ACTUALIZAR USUARIOS

// Variables globales para actualizar usuario
let todosLosUsuariosActualizar = [];
let usuarioSeleccionadoActualizar = null;

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Módulo de actualizar usuarios inicializado');
});

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
}

// ✅ CARGAR USUARIOS PARA ACTUALIZAR
async function cargarUsuariosParaActualizar() {
    try {
        console.log('📥 Cargando usuarios para actualizar...');
        
        // En un sistema real, aquí harías fetch a la API
        // const response = await fetch('/api/usuarios/');
        // todosLosUsuariosActualizar = await response.json();
        
        // Usar datos globales si existen, sino cargar
        if (typeof todosLosUsuarios !== 'undefined') {
            todosLosUsuariosActualizar = todosLosUsuarios;
        } else {
            // Simular carga
            await new Promise(resolve => setTimeout(resolve, 500));
            todosLosUsuariosActualizar = [];
        }
        
        renderizarListaBusquedaActualizar(todosLosUsuariosActualizar);
        console.log(`✅ ${todosLosUsuariosActualizar.length} usuarios cargados para actualizar`);
        
    } catch (error) {
        console.error('❌ Error cargando usuarios para actualizar:', error);
        throw error;
    }
}

// ✅ RENDERIZAR LISTA DE BÚSQUEDA PARA ACTUALIZAR
function renderizarListaBusquedaActualizar(usuarios) {
    const lista = document.getElementById('lista-usuarios-actualizar');
    
    if (!usuarios || usuarios.length === 0) {
        lista.innerHTML = '<div class="usuario-item-search">No hay usuarios disponibles</div>';
        return;
    }
    
    let html = '';
    
    usuarios.forEach(usuario => {
        html += `
            <div class="usuario-item-search" data-id="${usuario.id_usuario}" onclick="seleccionarUsuarioActualizar(${usuario.id_usuario})">
                <div class="usuario-info-search">
                    <div>
                        <div class="usuario-nombre-search">${usuario.nombre_usuario} ${usuario.apellido_pat_usuario}</div>
                        <div class="usuario-email-search">${usuario.correo_electronico_usuario}</div>
                    </div>
                    <span class="rol-badge rol-${usuario.nombre_rol.toLowerCase()}">${usuario.nombre_rol}</span>
                </div>
            </div>
        `;
    });
    
    lista.innerHTML = html;
}

// ✅ BUSCAR USUARIOS PARA ACTUALIZAR
function buscarUsuariosActualizar() {
    const termino = document.getElementById('buscar-usuario-actualizar').value.toLowerCase();
    const usuariosFiltrados = todosLosUsuariosActualizar.filter(usuario =>
        usuario.nombre_usuario.toLowerCase().includes(termino) ||
        usuario.apellido_pat_usuario.toLowerCase().includes(termino) ||
        usuario.correo_electronico_usuario.toLowerCase().includes(termino) ||
        usuario.rut_usuario.toLowerCase().includes(termino)
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
    document.querySelector(`.usuario-item-search[data-id="${usuarioId}"]`).classList.add('selected');
    
    mostrarInformacionUsuarioActualizar(usuarioSeleccionadoActualizar);
    document.getElementById('btn-actualizar-usuario').disabled = false;
    
    console.log('✅ Usuario seleccionado para actualizar:', usuarioSeleccionadoActualizar);
}

// ✅ MOSTRAR INFORMACIÓN USUARIO PARA ACTUALIZAR
function mostrarInformacionUsuarioActualizar(usuario) {
    document.getElementById('info-usuario-seleccionado').style.display = 'block';
    document.getElementById('form-edicion-usuario').style.display = 'block';
    
    // Mostrar información actual
    document.getElementById('usuario-nombre-completo').textContent = 
        `${usuario.nombre_usuario} ${usuario.apellido_pat_usuario} ${usuario.apellido_mat_usuario}`;
    document.getElementById('usuario-rut').textContent = usuario.rut_usuario;
    document.getElementById('usuario-rol-actual').textContent = usuario.nombre_rol;
    document.getElementById('usuario-rol-actual').className = `rol-badge rol-${usuario.nombre_rol.toLowerCase()}`;
    document.getElementById('usuario-estado-actual').textContent = usuario.estado_usuario ? 'Activo' : 'Inactivo';
    document.getElementById('usuario-estado-actual').className = `estado-badge ${usuario.estado_usuario ? 'estado-activo' : 'estado-inactivo'}`;
    
    // Llenar formulario de edición
    document.getElementById('editar-nombre').value = usuario.nombre_usuario;
    document.getElementById('editar-apellido-pat').value = usuario.apellido_pat_usuario;
    document.getElementById('editar-apellido-mat').value = usuario.apellido_mat_usuario;
    document.getElementById('editar-telefono').value = usuario.telefono_usuario;
    document.getElementById('editar-correo').value = usuario.correo_electronico_usuario;
    document.getElementById('editar-rol').value = usuario.id_rol;
    document.getElementById('editar-estado').value = usuario.estado_usuario ? '1' : '0';
    document.getElementById('editar-direccion').value = usuario.direccion_usuario || '';
    document.getElementById('editar-observaciones').value = usuario.observaciones_usuario || '';
    
    // Limpiar campos de nueva contraseña
    document.getElementById('nueva-password').value = '';
    document.getElementById('confirmar-nueva-password').value = '';
}

// ✅ VALIDAR FORMULARIO ACTUALIZAR
function validarFormularioActualizarUsuario() {
    const nombre = document.getElementById('editar-nombre').value.trim();
    const apellidoPat = document.getElementById('editar-apellido-pat').value.trim();
    const apellidoMat = document.getElementById('editar-apellido-mat').value.trim();
    const telefono = document.getElementById('editar-telefono').value.trim();
    const correo = document.getElementById('editar-correo').value.trim();
    const nuevaPassword = document.getElementById('nueva-password').value;
    const confirmarPassword = document.getElementById('confirmar-nueva-password').value;
    
    let valido = true;
    
    // Validar campos requeridos
    if (!nombre || !apellidoPat || !apellidoMat || !telefono || !correo) {
        valido = false;
        mostrarError('Todos los campos obligatorios deben estar completos');
    }
    
    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (correo && !emailRegex.test(correo)) {
        valido = false;
        mostrarError('El formato del correo electrónico no es válido');
    }
    
    // Validar contraseñas si se están cambiando
    if (nuevaPassword || confirmarPassword) {
        if (nuevaPassword !== confirmarPassword) {
            valido = false;
            mostrarError('Las nuevas contraseñas no coinciden');
        }
        
        if (nuevaPassword.length < 8) {
            valido = false;
            mostrarError('La nueva contraseña debe tener al menos 8 caracteres');
        }
    }
    
    return valido;
}

// ✅ ACTUALIZAR USUARIO EXISTENTE
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
        const datosActualizacion = {
            nombre_usuario: document.getElementById('editar-nombre').value.trim(),
            apellido_pat_usuario: document.getElementById('editar-apellido-pat').value.trim(),
            apellido_mat_usuario: document.getElementById('editar-apellido-mat').value.trim(),
            telefono_usuario: document.getElementById('editar-telefono').value.trim(),
            correo_electronico_usuario: document.getElementById('editar-correo').value.trim(),
            id_rol: parseInt(document.getElementById('editar-rol').value),
            direccion_usuario: document.getElementById('editar-direccion').value.trim(),
            estado_usuario: document.getElementById('editar-estado').value === '1',
            observaciones_usuario: document.getElementById('editar-observaciones').value.trim()
        };
        
        // Agregar nueva contraseña si se proporcionó
        const nuevaPassword = document.getElementById('nueva-password').value;
        if (nuevaPassword) {
            datosActualizacion.password_usuario = nuevaPassword;
        }
        
        console.log('📤 Datos para actualizar usuario:', datosActualizacion);
        
        // En un sistema real, aquí harías la petición PUT a tu API
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
            throw new Error(errorData.error || `Error ${response.status}`);
        }
        
        const usuarioActualizado = await response.json();
        console.log('✅ Usuario actualizado:', usuarioActualizado);
        
        // Cerrar loading
        Swal.close();
        
        // Mostrar éxito
        mostrarExito('Usuario actualizado correctamente');
        
        // Cerrar modal
        cerrarModalActualizarUsuario();
        
        // Recargar la lista de usuarios si existe la función
        if (typeof cargarUsuarios === 'function') {
            await cargarUsuarios();
        }
        
        // Recargar página después de 2 segundos
        setTimeout(() => {
            window.location.reload();
        }, 2000);
        
    } catch (error) {
        console.error('❌ Error actualizando usuario:', error);
        Swal.close();
        mostrarError('Error al actualizar el usuario: ' + error.message);
    }
}

// ✅ EDITAR USUARIO DESDE LISTA
function editarUsuarioDesdeLista(usuarioId) {
    abrirModalActualizarUsuario();
    
    // Simular delay para que se abra el modal
    setTimeout(() => {
        const usuario = todosLosUsuariosActualizar.find(u => u.id_usuario === usuarioId);
        if (usuario) {
            seleccionarUsuarioActualizar(usuarioId);
        }
    }, 300);
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