// 🗑️ SISTEMA PARA ELIMINAR USUARIOS

// Variables globales para eliminar usuario
let todosLosUsuariosEliminar = [];
let usuarioSeleccionadoEliminar = null;

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Módulo de eliminar usuarios inicializado');
});

// ✅ ABRIR MODAL ELIMINAR USUARIO
async function abrirModalEliminarUsuario() {
    console.log('🗑️ Abriendo modal para eliminar usuario...');
    
    try {
        document.getElementById('modal-eliminar-usuario').style.display = 'block';
        resetearModalEliminarUsuario();
        await cargarUsuariosParaEliminar();
        console.log('✅ Modal de eliminar usuario listo');
        
    } catch (error) {
        console.error('❌ Error al abrir modal de eliminar usuario:', error);
        mostrarError('Error al cargar los usuarios: ' + error.message);
    }
}

// ✅ CERRAR MODAL ELIMINAR
function cerrarModalEliminarUsuario() {
    console.log('❌ Cerrando modal de eliminar usuario...');
    document.getElementById('modal-eliminar-usuario').style.display = 'none';
}

// ✅ RESETEAR MODAL ELIMINAR
function resetearModalEliminarUsuario() {
    console.log('🔄 Reseteando modal de eliminar usuario...');
    
    usuarioSeleccionadoEliminar = null;
    document.getElementById('buscar-usuario-eliminar').value = '';
    document.getElementById('info-usuario-eliminar').style.display = 'none';
    document.getElementById('btn-confirmar-eliminar-usuario').disabled = true;
    document.getElementById('lista-usuarios-eliminar').innerHTML = '';
}

// ✅ CARGAR USUARIOS PARA ELIMINAR
async function cargarUsuariosParaEliminar() {
    try {
        console.log('📥 Cargando usuarios para eliminar...');
        
        // En un sistema real, aquí harías fetch a la API
        const response = await fetch('/api/usuarios/');
        if (!response.ok) throw new Error('Error cargando usuarios');
        
        todosLosUsuariosEliminar = await response.json();
        
        // Filtrar solo administradores y operadores
        todosLos