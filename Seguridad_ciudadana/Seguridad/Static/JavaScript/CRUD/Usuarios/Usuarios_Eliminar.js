// 🗑️ SISTEMA PARA ELIMINAR USUARIOS

// Variables globales para eliminar usuario
let usuarioSeleccionadoEliminar = null;

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Módulo de eliminar usuarios inicializado');
    inicializarEventListenersEliminar();
});

// ✅ INICIALIZAR EVENT LISTENERS
function inicializarEventListenersEliminar() {
    // Event listener para el input de búsqueda
    const buscarInput = document.getElementById('buscar-usuario-eliminar');
    if (buscarInput) {
        buscarInput.addEventListener('input', buscarUsuariosEliminar);
    }
}

// ✅ ABRIR MODAL DE ELIMINAR USUARIO
function abrirModalEliminarUsuario() {
    console.log('🗑️ Abriendo modal para eliminar usuario...');
    
    try {
        document.getElementById('modal-eliminar-usuario').style.display = 'block';
        resetearModalEliminar();
        console.log('✅ Modal de eliminar usuario listo');
        
    } catch (error) {
        console.error('❌ Error al abrir modal de eliminar usuario:', error);
        mostrarError('Error al abrir el modal: ' + error.message);
    }
}

// ✅ CERRAR MODAL ELIMINAR
function cerrarModalEliminarUsuario() {
    console.log('❌ Cerrando modal de eliminar usuario...');
    document.getElementById('modal-eliminar-usuario').style.display = 'none';
    resetearModalEliminar();
}

// ✅ RESETEAR MODAL ELIMINAR
function resetearModalEliminar() {
    console.log('🔄 Reseteando modal de eliminar...');
    
    // Limpiar búsqueda
    document.getElementById('buscar-usuario-eliminar').value = '';
    
    // Limpiar lista de resultados
    const listaUsuarios = document.getElementById('lista-usuarios-eliminar');
    if (listaUsuarios) {
        listaUsuarios.innerHTML = '';
    }
    
    // Ocultar información del usuario
    const infoUsuario = document.getElementById('info-usuario-eliminar');
    if (infoUsuario) {
        infoUsuario.style.display = 'none';
    }
    
    // Deshabilitar botón de eliminar
    const btnEliminar = document.getElementById('btn-confirmar-eliminar-usuario');
    if (btnEliminar) {
        btnEliminar.disabled = true;
    }
    
    // Resetear usuario seleccionado
    usuarioSeleccionadoEliminar = null;
}

// ✅ BUSCAR USUARIOS PARA ELIMINAR
async function buscarUsuariosEliminar() {
    const query = document.getElementById('buscar-usuario-eliminar').value.trim();
    const listaUsuarios = document.getElementById('lista-usuarios-eliminar');
    
    if (!listaUsuarios) return;
    
    // Limpiar lista si la búsqueda está vacía
    if (!query) {
        listaUsuarios.innerHTML = '';
        return;
    }
    
    try {
        // Mostrar loading
        listaUsuarios.innerHTML = `
            <div class="loading-usuarios">
                <i class="fa-solid fa-spinner"></i>
                <p>Buscando usuarios...</p>
            </div>
        `;

        const response = await fetch(`/api/usuarios/buscar/?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const usuarios = await response.json();
        
        // Mostrar resultados
        if (usuarios.length === 0) {
            listaUsuarios.innerHTML = `
                <div class="sin-resultados">
                    <i class="fa-solid fa-search"></i>
                    <p>No se encontraron usuarios</p>
                </div>
            `;
            return;
        }
        
        const usuariosHTML = usuarios.map(usuario => {
            const estadoClass = usuario.estado_usuario ? 'estado-activo' : 'estado-inactivo';
            const estadoTexto = usuario.estado_usuario ? 'Activo' : 'Inactivo';
            
            return `
                <div class="usuario-item-search" onclick="seleccionarUsuarioEliminar(${usuario.id_usuario}, this)">
                    <div class="usuario-info-search">
                        <div>
                            <div class="usuario-nombre-search">${usuario.nombre_completo}</div>
                            <div class="usuario-email-search">${usuario.correo_electronico_usuario}</div>
                            <div class="usuario-rut-search">RUT: ${usuario.rut_usuario}</div>
                        </div>
                        <div>
                            <span class="usuario-rol ${getRolClassEliminar(usuario.rol_nombre)}">${usuario.rol_nombre}</span>
                            <div class="usuario-estado ${estadoClass}">${estadoTexto}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        listaUsuarios.innerHTML = usuariosHTML;
        
    } catch (error) {
        console.error('❌ Error buscando usuarios:', error);
        listaUsuarios.innerHTML = `
            <div class="error-busqueda">
                <i class="fa-solid fa-exclamation-triangle"></i>
                <p>Error al buscar usuarios: ${error.message}</p>
            </div>
        `;
    }
}

// ✅ SELECCIONAR USUARIO PARA ELIMINAR
async function seleccionarUsuarioEliminar(usuarioId, elemento) {
    try {
        console.log(`👤 Seleccionando usuario para eliminar: ${usuarioId}`);
        
        // Remover selección anterior
        const itemsAnteriores = document.querySelectorAll('#lista-usuarios-eliminar .usuario-item-search.selected');
        itemsAnteriores.forEach(item => item.classList.remove('selected'));
        
        // Agregar selección actual
        elemento.classList.add('selected');
        
        // Obtener información completa del usuario
        const response = await fetch(`/api/usuarios/${usuarioId}/`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const usuario = await response.json();
        
        // Guardar usuario seleccionado
        usuarioSeleccionadoEliminar = usuario;
        
        // Mostrar información del usuario
        mostrarInformacionUsuarioEliminar(usuario);
        
        // Habilitar botón de eliminar
        document.getElementById('btn-confirmar-eliminar-usuario').disabled = false;
        
    } catch (error) {
        console.error('❌ Error seleccionando usuario:', error);
        mostrarError('Error al cargar la información del usuario: ' + error.message);
    }
}

// ✅ MOSTRAR INFORMACIÓN DEL USUARIO A ELIMINAR
function mostrarInformacionUsuarioEliminar(usuario) {
    const infoUsuario = document.getElementById('info-usuario-eliminar');
    if (!infoUsuario) return;
    
    // Actualizar información
    document.getElementById('usuario-eliminar-nombre').textContent = 
        `${usuario.nombre_usuario} ${usuario.apellido_pat_usuario} ${usuario.apellido_mat_usuario}`;
    document.getElementById('usuario-eliminar-rut').textContent = usuario.rut_usuario;
    document.getElementById('usuario-eliminar-correo').textContent = usuario.correo_electronico_usuario;
    
    // Actualizar rol
    const rolElement = document.getElementById('usuario-eliminar-rol');
    rolElement.textContent = getNombreRol(usuario.id_rol);
    rolElement.className = 'rol-badge ' + getRolClassEliminar(getNombreRol(usuario.id_rol));
    
    // Actualizar estado
    const estadoElement = document.getElementById('usuario-eliminar-estado');
    const estadoTexto = usuario.estado_usuario ? 'Activo' : 'Inactivo';
    const estadoClass = usuario.estado_usuario ? 'estado-activo' : 'estado-inactivo';
    estadoElement.textContent = estadoTexto;
    estadoElement.className = 'estado-badge ' + estadoClass;
    
    // Mostrar sección
    infoUsuario.style.display = 'block';
}

// ✅ CONFIRMAR ELIMINACIÓN DE USUARIO
async function confirmarEliminarUsuario() {
    if (!usuarioSeleccionadoEliminar) {
        mostrarError('No hay ningún usuario seleccionado para eliminar');
        return;
    }
    
    const usuarioId = usuarioSeleccionadoEliminar.id_usuario;
    const nombreUsuario = `${usuarioSeleccionadoEliminar.nombre_usuario} ${usuarioSeleccionadoEliminar.apellido_pat_usuario}`;
    
    // Confirmación con SweetAlert2
    Swal.fire({
        title: '¿Estás seguro?',
        html: `
            <p>Vas a eliminar permanentemente al usuario:</p>
            <p><strong>${nombreUsuario}</strong></p>
            <p class="text-danger">Esta acción no se puede deshacer.</p>
        `,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar usuario',
        cancelButtonText: 'Cancelar',
        reverseButtons: true,
        focusCancel: true,
        customClass: {
            popup: 'swal2-popup-eliminar'
        }
    }).then(async (result) => {
        if (result.isConfirmed) {
            await ejecutarEliminacionUsuario(usuarioId, nombreUsuario);
        }
    });
}

// ✅ EJECUTAR ELIMINACIÓN DE USUARIO
async function ejecutarEliminacionUsuario(usuarioId, nombreUsuario) {
    try {
        console.log(`🗑️ Ejecutando eliminación del usuario: ${usuarioId}`);
        
        // Mostrar loading
        Swal.fire({
            title: 'Eliminando usuario...',
            text: 'Por favor espere',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/usuarios/${usuarioId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}`);
        }
        
        const resultado = await response.json();
        console.log('✅ Usuario eliminado:', resultado);
        
        // Cerrar loading
        Swal.close();
        
        // Mostrar éxito
        Swal.fire({
            icon: 'success',
            title: '¡Usuario eliminado!',
            html: `
                <p>El usuario <strong>${nombreUsuario}</strong> ha sido eliminado correctamente del sistema.</p>
            `,
            confirmButtonText: 'Aceptar',
            timer: 3000
        });
        
        // Cerrar modal
        cerrarModalEliminarUsuario();
        
        // Recargar la lista de usuarios
        if (typeof recargarListaUsuarios === 'function') {
            recargarListaUsuarios();
        }
        
        // Recargar estadísticas
        if (typeof cargarEstadisticas === 'function') {
            cargarEstadisticas();
        }
        
    } catch (error) {
        console.error('❌ Error eliminando usuario:', error);
        Swal.close();
        
        // Mostrar error específico
        let mensajeError = 'Error al eliminar el usuario: ' + error.message;
        
        if (error.message.includes('denuncias asociadas')) {
            mensajeError = `
                <p>No se puede eliminar el usuario <strong>${nombreUsuario}</strong> porque tiene denuncias asociadas en el sistema.</p>
                <p class="text-muted">Para eliminar este usuario, primero debe reasignar o eliminar sus denuncias asociadas.</p>
            `;
        }
        
        Swal.fire({
            icon: 'error',
            title: 'Error al eliminar',
            html: mensajeError,
            confirmButtonText: 'Aceptar'
        });
    }
}

// ✅ FUNCIONES AUXILIARES PARA ELIMINAR
function getRolClassEliminar(rolNombre) {
    const roles = {
        'Administrador': 'rol-administrador',
        'Operador': 'rol-operador',
        'Conductor': 'rol-conductor',
        'Inspector': 'rol-inspector'
    };
    return roles[rolNombre] || 'rol-usuario';
}

function getNombreRol(idRol) {
    const roles = {
        1: 'Administrador',
        2: 'Operador',
        3: 'Conductor',
        4: 'Inspector'
    };
    return roles[idRol] || 'Usuario';
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
        text: mensaje,
        confirmButtonText: 'Aceptar'
    });
}

// ✅ ELIMINAR USUARIO DESDE LA LISTA
function eliminarUsuarioDesdeLista(usuarioId) {
    console.log('🗑️ Eliminando usuario desde lista:', usuarioId);
    
    // Abrir modal de eliminación
    abrirModalEliminarUsuario();
    
    // Buscar y seleccionar automáticamente el usuario
    setTimeout(async () => {
        try {
            // Obtener información del usuario
            const response = await fetch(`/api/usuarios/${usuarioId}/`);
            if (response.ok) {
                const usuario = await response.json();
                
                // Buscar en la lista
                const buscarInput = document.getElementById('buscar-usuario-eliminar');
                buscarInput.value = usuario.rut_usuario;
                
                // Esperar a que se realice la búsqueda y seleccionar
                setTimeout(() => {
                    const items = document.querySelectorAll('#lista-usuarios-eliminar .usuario-item-search');
                    for (let item of items) {
                        if (item.textContent.includes(usuario.rut_usuario)) {
                            seleccionarUsuarioEliminar(usuarioId, item);
                            break;
                        }
                    }
                }, 500);
            }
        } catch (error) {
            console.error('❌ Error preseleccionando usuario:', error);
        }
    }, 300);
}