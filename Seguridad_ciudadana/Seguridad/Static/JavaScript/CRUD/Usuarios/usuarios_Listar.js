// 📋 SISTEMA PARA LISTAR Y CARGAR USUARIOS (ACTUALIZADO)

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Módulo de listar usuarios inicializado');
    cargarUsuarios();
    cargarEstadisticas();
});

// ✅ CARGAR USUARIOS DESDE LA API (EXCLUYENDO CIUDADANOS)
async function cargarUsuarios() {
    try {
        console.log('📥 Cargando lista de usuarios...');
        
        // Mostrar loading
        document.getElementById('lista-usuarios').innerHTML = `
            <div class="loading-usuarios">
                <i class="fa-solid fa-spinner"></i>
                <p>Cargando usuarios...</p>
            </div>
        `;

        const response = await fetch('/api/usuarios/');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const usuarios = await response.json();
        console.log('✅ Usuarios cargados:', usuarios);
        
        // ✅ FILTRAR: Excluir usuarios con rol "Ciudadano"
        const usuariosFiltrados = usuarios.filter(usuario => 
            usuario.rol_nombre !== 'Ciudadano' && usuario.rol_nombre !== 'Ciudadano'
        );
        
        mostrarUsuarios(usuariosFiltrados);
        
    } catch (error) {
        console.error('❌ Error cargando usuarios:', error);
        document.getElementById('lista-usuarios').innerHTML = `
            <div class="sin-usuarios">
                <i class="fa-solid fa-exclamation-triangle"></i>
                <p>Error al cargar los usuarios: ${error.message}</p>
                <button onclick="cargarUsuarios()" class="btn-actualizar-usuario">
                    <i class="fa-solid fa-refresh"></i> Reintentar
                </button>
            </div>
        `;
    }
}

// ✅ MOSTRAR USUARIOS EN LA LISTA (EXCLUYENDO CIUDADANOS)
function mostrarUsuarios(usuarios) {
    const listaUsuarios = document.getElementById('lista-usuarios');
    
    if (!usuarios || usuarios.length === 0) {
        listaUsuarios.innerHTML = `
            <div class="sin-usuarios">
                <i class="fa-solid fa-users-slash"></i>
                <h3>No hay usuarios registrados</h3>
                <p>Comienza agregando el primer usuario al sistema.</p>
            </div>
        `;
        return;
    }
    
    const usuariosHTML = usuarios.map(usuario => {
        const rolClass = getRolClass(usuario.rol_nombre);
        const estadoClass = usuario.estado_usuario ? 'estado-activo' : 'estado-inactivo';
        const estadoTexto = usuario.estado_usuario ? 'Activo' : 'Inactivo';
        
        return `
            <div class="usuario-card" data-usuario-id="${usuario.id_usuario}">
                <div class="usuario-header">
                    <h3 class="usuario-nombre">${usuario.nombre_usuario} ${usuario.apellido_pat_usuario}</h3>
                    <span class="usuario-rol ${rolClass}">${usuario.rol_nombre}</span>
                </div>
                
                <div class="usuario-info">
                    <div class="usuario-dato">
                        <strong>RUT:</strong>
                        <span>${usuario.rut_usuario}</span>
                    </div>
                    <div class="usuario-dato">
                        <strong>Email:</strong>
                        <span>${usuario.correo_electronico_usuario}</span>
                    </div>
                    <div class="usuario-dato">
                        <strong>Teléfono:</strong>
                        <span>${usuario.telefono_movil_usuario || 'No asignado'}</span>
                    </div>
                    <div class="usuario-dato">
                        <strong>Turno:</strong>
                        <span>${usuario.turno_nombre || 'No asignado'}</span>
                    </div>
                    <div class="usuario-dato">
                        <strong>Estado:</strong>
                        <span class="usuario-estado ${estadoClass}">${estadoTexto}</span>
                    </div>
                    <div class="usuario-dato">
                        <strong>Registro:</strong>
                        <span>${usuario.fecha_creacion || 'No disponible'}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    listaUsuarios.innerHTML = usuariosHTML;
}

// ✅ CARGAR ESTADÍSTICAS (ACTUALIZADO)
async function cargarEstadisticas() {
    try {
        const response = await fetch('/api/usuarios/');
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}`);
        }
        
        const usuarios = await response.json();
        
        // ✅ CALCULAR NUEVAS ESTADÍSTICAS
        const totalUsuarios = usuarios.length;
        const totalCiudadanos = usuarios.filter(u => u.rol_nombre === 'Ciudadano').length;
        const totalTrabajadores = usuarios.filter(u => 
            u.rol_nombre !== 'Ciudadano' && u.rol_nombre !== 'Ciudadano'
        ).length;
        const totalAdministradores = usuarios.filter(u => u.rol_nombre === 'Administrador').length;
        const totalActivos = usuarios.filter(u => u.estado_usuario).length;
        
        // Actualizar estadísticas
        document.getElementById('total-ciudadanos').textContent = totalCiudadanos;
        document.getElementById('total-trabajadores').textContent = totalTrabajadores;
        document.getElementById('total-administradores').textContent = totalAdministradores;
        document.getElementById('total-activos').textContent = totalActivos;
        
    } catch (error) {
        console.error('❌ Error cargando estadísticas:', error);
        // Mostrar ceros en caso de error
        document.getElementById('total-ciudadanos').textContent = '0';
        document.getElementById('total-trabajadores').textContent = '0';
        document.getElementById('total-administradores').textContent = '0';
        document.getElementById('total-activos').textContent = '0';
    }
}

// ✅ OBTENER CLASE CSS PARA ROL
function getRolClass(rolNombre) {
    const roles = {
        'Administrador': 'rol-administrador',
        'Operador': 'rol-operador',
        'Conductor': 'rol-conductor',
        'Inspector': 'rol-inspector',
        'Ciudadano': 'rol-ciudadano'
    };
    return roles[rolNombre] || 'rol-usuario';
}

// ✅ FUNCIONES PARA BOTONES DE ACCIÓN
function editarUsuarioDesdeLista(usuarioId) {
    console.log('✏️ Editando usuario desde lista:', usuarioId);
    abrirModalActualizarUsuario();
}

function eliminarUsuarioDesdeLista(usuarioId) {
    console.log('🗑️ Eliminando usuario desde lista:', usuarioId);
    abrirModalEliminarUsuario();
}

// ✅ RECARGAR LISTA DESDE OTROS MÓDULOS
function recargarListaUsuarios() {
    cargarUsuarios();
    cargarEstadisticas();
}