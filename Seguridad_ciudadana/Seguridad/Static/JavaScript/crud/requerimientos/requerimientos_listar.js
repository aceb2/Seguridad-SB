// Variables globales para listar
let todosRequerimientos = [];
let estadisticasGlobales = {
    familias: 0,
    grupos: 0,
    subgrupos: 0,
    requerimientos: 0
};

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Sistema de listado de requerimientos listo');
    cargarPaginaCompleta();
});

// ✅ CARGAR PÁGINA COMPLETA
async function cargarPaginaCompleta() {
    try {
        console.log('📥 Cargando página completa...');
        
        // Cargar en paralelo para mejor rendimiento
        await Promise.all([
            cargarEstadisticas(),
            cargarRequerimientosExistentes()
        ]);
        
        console.log('✅ Página cargada completamente');
        
    } catch (error) {
        console.error('❌ Error cargando página:', error);
        mostrarError('Error al cargar los datos: ' + error.message);
    }
}

// ✅ CARGAR ESTADÍSTICAS
async function cargarEstadisticas() {
    try {
        console.log('📊 Cargando estadísticas...');
        
        // Cargar conteos desde la API
        const [familiasRes, gruposRes, subgruposRes, requerimientosRes] = await Promise.all([
            fetch('/api/familias/'),
            fetch('/api/grupos/'),
            fetch('/api/subgrupos/'),
            fetch('/api/requerimientos/')
        ]);
        
        if (!familiasRes.ok || !gruposRes.ok || !subgruposRes.ok || !requerimientosRes.ok) {
            throw new Error('Error al cargar las estadísticas');
        }
        
        const [familiasData, gruposData, subgruposData, requerimientosData] = await Promise.all([
            familiasRes.json(),
            gruposRes.json(),
            subgruposRes.json(),
            requerimientosRes.json()
        ]);
        
        // Actualizar estadísticas globales
        estadisticasGlobales = {
            familias: familiasData.length,
            grupos: gruposData.length,
            subgrupos: subgruposData.length,
            requerimientos: requerimientosData.length
        };
        
        // Actualizar la interfaz
        actualizarEstadisticasUI();
        
        console.log('✅ Estadísticas cargadas:', estadisticasGlobales);
        
    } catch (error) {
        console.error('❌ Error cargando estadísticas:', error);
        // Usar valores por defecto
        estadisticasGlobales = { familias: 0, grupos: 0, subgrupos: 0, requerimientos: 0 };
        actualizarEstadisticasUI();
    }
}

// ✅ ACTUALIZAR INTERFAZ DE ESTADÍSTICAS
function actualizarEstadisticasUI() {
    document.getElementById('total-familias').textContent = estadisticasGlobales.familias;
    document.getElementById('total-grupos').textContent = estadisticasGlobales.grupos;
    document.getElementById('total-subgrupos').textContent = estadisticasGlobales.subgrupos;
    document.getElementById('total-requerimientos').textContent = estadisticasGlobales.requerimientos;
    
    // Agregar animación a los números
    animarContadores();
}

// ✅ ANIMAR CONTADORES
function animarContadores() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = +counter.textContent;
        const increment = target / 100;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current > target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 20);
    });
}

// ✅ CARGAR REQUERIMIENTOS EXISTENTES
async function cargarRequerimientosExistentes() {
    try {
        console.log('📋 Cargando requerimientos existentes...');
        
        const response = await fetch('/api/requerimientos/');
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        
        todosRequerimientos = await response.json();
        
        // Actualizar la interfaz
        renderizarRequerimientos();
        
        console.log(`✅ ${todosRequerimientos.length} requerimientos cargados`);
        
    } catch (error) {
        console.error('❌ Error cargando requerimientos:', error);
        mostrarListaVacia('Error al cargar los requerimientos');
    }
}

// ✅ RENDERIZAR REQUERIMIENTOS EN TARJETAS
function renderizarRequerimientos() {
    const contenedor = document.getElementById('lista-requerimientos');
    
    if (!contenedor) {
        console.error('❌ Contenedor de requerimientos no encontrado');
        return;
    }
    
    if (todosRequerimientos.length === 0) {
        mostrarListaVacia('No hay requerimientos registrados');
        return;
    }
    
    contenedor.innerHTML = '';
    
    todosRequerimientos.forEach((req, index) => {
        const card = crearTarjetaRequerimiento(req, index);
        contenedor.appendChild(card);
    });
    
    // Agregar animación de entrada
    animarEntradaTarjetas();
}

// ✅ CREAR TARJETA DE REQUERIMIENTO
function crearTarjetaRequerimiento(requerimiento, index) {
    const card = document.createElement('div');
    card.className = 'requerimiento-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    // Obtener información de la jerarquía
    const familia = requerimiento.familia_nombre || 'Sin familia';
    const grupo = requerimiento.grupo_nombre || 'Sin grupo';
    const subgrupo = requerimiento.subgrupo_nombre || 'Sin subgrupo';
    
    card.innerHTML = `
        <div class="requerimiento-header">
            <h3 class="requerimiento-nombre">${requerimiento.nombre_requerimiento}</h3>
            <span class="requerimiento-clasificacion clasificacion-${requerimiento.clasificacion_requerimiento?.toLowerCase() || 'media'}">
                ${requerimiento.clasificacion_requerimiento || 'Sin clasificación'}
            </span>
        </div>
        
        <div class="requerimiento-info">
            <div class="requerimiento-dato">
                <strong><i class="fa-solid fa-hashtag"></i> Código:</strong>
                <span class="codigo-requerimiento">${requerimiento.codigo_requerimiento || 'N/A'}</span>
            </div>
            <div class="requerimiento-dato">
                <strong><i class="fa-solid fa-sitemap"></i> Familia:</strong>
                <span>${familia}</span>
            </div>
            <div class="requerimiento-dato">
                <strong><i class="fa-solid fa-layer-group"></i> Grupo:</strong>
                <span>${grupo}</span>
            </div>
            <div class="requerimiento-dato">
                <strong><i class="fa-solid fa-stream"></i> Subgrupo:</strong>
                <span>${subgrupo}</span>
            </div>
            ${requerimiento.descripcion_requerimiento ? `
            <div class="requerimiento-dato descripcion">
                <strong><i class="fa-solid fa-file-lines"></i> Descripción:</strong>
                <span class="texto-descripcion">${requerimiento.descripcion_requerimiento}</span>
            </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

// ✅ MOSTRAR LISTA VACÍA
function mostrarListaVacia(mensaje) {
    const contenedor = document.getElementById('lista-requerimientos');
    if (!contenedor) return;
    
    contenedor.innerHTML = `
        <div class="sin-requerimientos">
            <i class="fa-solid fa-inbox"></i>
            <h4>${mensaje}</h4>
            <p>Utilice el botón "Agregar Nuevo Requerimiento" para crear el primero.</p>
        </div>
    `;
}

// ✅ ANIMAR ENTRADA DE TARJETAS
function animarEntradaTarjetas() {
    const cards = document.querySelectorAll('.requerimiento-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// ✅ EDITAR REQUERIMIENTO DESDE LISTA
function editarRequerimiento(idRequerimiento) {
    console.log('✏️ Editando requerimiento:', idRequerimiento);
    
    // Abrir el modal de actualización
    abrirModalActualizarRequerimiento();
    
    // Buscar y seleccionar automáticamente el requerimiento
    setTimeout(() => {
        const requerimiento = todosRequerimientos.find(req => req.id_requerimiento === idRequerimiento);
        if (requerimiento) {
            // Simular la selección en el modal de actualización
            seleccionarRequerimientoParaEdicion(requerimiento);
        }
    }, 500);
}

// ✅ SELECCIONAR REQUERIMIENTO PARA EDICIÓN (compatible con actualizar.js)
function seleccionarRequerimientoParaEdicion(requerimiento) {
    if (typeof seleccionarRequerimientoActualizar === 'function') {
        // Usar la función del archivo de actualización si existe
        const elemento = document.querySelector(`[data-requerimiento-id="${requerimiento.id_requerimiento}"]`);
        if (elemento) {
            seleccionarRequerimientoActualizar(requerimiento, elemento);
        }
    } else {
        // Fallback: abrir modal con el ID en la búsqueda
        document.getElementById('buscar-requerimiento').value = requerimiento.nombre_requerimiento;
        if (typeof buscarRequerimientos === 'function') {
            buscarRequerimientos();
        }
    }
}

// ✅ ELIMINAR REQUERIMIENTO DESDE LISTA
async function eliminarRequerimientoDesdeLista(idRequerimiento) {
    const requerimiento = todosRequerimientos.find(req => req.id_requerimiento === idRequerimiento);
    
    if (!requerimiento) {
        mostrarError('Requerimiento no encontrado');
        return;
    }
    
    const resultado = await Swal.fire({
        title: '¿Eliminar requerimiento?',
        html: `
            <div style="text-align: left;">
                <p>Está a punto de eliminar el siguiente requerimiento:</p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <strong>Nombre:</strong> ${requerimiento.nombre_requerimiento}<br>
                    <strong>Clasificación:</strong> <span class="clasificacion-badge ${requerimiento.clasificacion_requerimiento?.toLowerCase()}">${requerimiento.clasificacion_requerimiento}</span><br>
                    <strong>Código:</strong> ${requerimiento.codigo_requerimiento || 'N/A'}
                </div>
                <p style="color: #dc3545; font-weight: bold;">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    Esta acción no se puede deshacer.
                </p>
            </div>
        `,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        width: '600px'
    });
    
    if (resultado.isConfirmed) {
        await ejecutarEliminacionRequerimiento(idRequerimiento, requerimiento);
    }
}

// ✅ EJECUTAR ELIMINACIÓN DE REQUERIMIENTO
async function ejecutarEliminacionRequerimiento(idRequerimiento, requerimiento) {
    try {
        const response = await fetch(`/api/requerimientos/${idRequerimiento}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}`);
        }
        
        // Mostrar éxito
        await Swal.fire({
            title: '¡Eliminado!',
            text: `El requerimiento "${requerimiento.nombre_requerimiento}" ha sido eliminado`,
            icon: 'success',
            confirmButtonText: 'Aceptar',
            timer: 2000
        });
        
        // Recargar la página para actualizar la lista y estadísticas
        window.location.reload();
        
    } catch (error) {
        console.error('❌ Error eliminando requerimiento:', error);
        
        let mensajeError = `Error al eliminar el requerimiento: ${error.message}`;
        
        if (error.message.includes('violates foreign key constraint')) {
            mensajeError = 'No se puede eliminar este requerimiento porque está siendo utilizado en denuncias existentes.';
        }
        
        Swal.fire({
            title: 'Error',
            text: mensajeError,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    }
}

// ✅ FILTRAR REQUERIMIENTOS EN LA LISTA
function filtrarRequerimientos() {
    const searchTerm = document.getElementById('buscar-requerimientos')?.value.toLowerCase().trim() || '';
    const cards = document.querySelectorAll('.requerimiento-card');
    
    let visibleCount = 0;
    
    cards.forEach(card => {
        const texto = card.textContent.toLowerCase();
        if (texto.includes(searchTerm)) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Mostrar mensaje si no hay resultados
    const contenedor = document.getElementById('lista-requerimientos');
    const mensajeNoResultados = contenedor.querySelector('.no-resultados');
    
    if (visibleCount === 0 && searchTerm) {
        if (!mensajeNoResultados) {
            const mensaje = document.createElement('div');
            mensaje.className = 'no-resultados sin-requerimientos';
            mensaje.innerHTML = `
                <i class="fa-solid fa-search"></i>
                <h4>No se encontraron requerimientos</h4>
                <p>No hay resultados para "${searchTerm}"</p>
            `;
            contenedor.appendChild(mensaje);
        }
    } else if (mensajeNoResultados) {
        mensajeNoResultados.remove();
    }
}

// ✅ ACTUALIZAR ESTADÍSTICAS EN TIEMPO REAL
function actualizarEstadisticasTiempoReal() {
    // Esta función puede ser llamada después de agregar/editar/eliminar
    cargarEstadisticas();
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

// ✅ EXPORTAR FUNCIONES PARA USO GLOBAL
window.cargarEstadisticas = cargarEstadisticas;
window.cargarRequerimientosExistentes = cargarRequerimientosExistentes;
window.filtrarRequerimientos = filtrarRequerimientos;
window.editarRequerimiento = editarRequerimiento;
window.eliminarRequerimientoDesdeLista = eliminarRequerimientoDesdeLista;