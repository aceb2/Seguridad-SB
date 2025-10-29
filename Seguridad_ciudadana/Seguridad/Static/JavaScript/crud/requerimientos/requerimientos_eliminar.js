// Variables globales para eliminación
let elementosParaEliminar = [];
let elementoSeleccionadoEliminar = null;
let tipoEliminacionActual = '';

// ✅ INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Sistema de eliminación listo');
});

// ✅ ABRIR MODAL DE ELIMINACIÓN
async function abrirModalEliminar() {
    console.log('🗑️ Abriendo modal de eliminación...');
    
    try {
        document.getElementById('modal-eliminar').style.display = 'block';
        resetearModalEliminar();
        console.log('✅ Modal de eliminación listo');
        
    } catch (error) {
        console.error('❌ Error al abrir modal de eliminación:', error);
        mostrarError('Error al abrir el modal: ' + error.message);
    }
}

// ✅ RESETEAR MODAL DE ELIMINACIÓN
function resetearModalEliminar() {
    console.log('🔄 Reseteando modal de eliminación...');
    
    elementoSeleccionadoEliminar = null;
    tipoEliminacionActual = '';
    elementosParaEliminar = [];
    
    // Resetear selects y contenedores
    document.getElementById('tipo-elemento-eliminar').value = '';
    document.getElementById('contenedor-eliminacion').innerHTML = `
        <div class="mensaje-inicial-eliminar">
            <i class="fa-solid fa-info-circle"></i>
            <p>Seleccione el tipo de elemento que desea eliminar</p>
        </div>
    `;
    
    // Deshabilitar botón de eliminar
    document.getElementById('btn-eliminar-confirmar').disabled = true;
}

// ✅ CAMBIAR TIPO DE ELIMINACIÓN
async function cambiarTipoEliminacion() {
    const tipoElemento = document.getElementById('tipo-elemento-eliminar').value;
    const contenedor = document.getElementById('contenedor-eliminacion');
    
    elementoSeleccionadoEliminar = null;
    document.getElementById('btn-eliminar-confirmar').disabled = true;
    
    if (!tipoElemento) {
        contenedor.innerHTML = `
            <div class="mensaje-inicial-eliminar">
                <i class="fa-solid fa-info-circle"></i>
                <p>Seleccione el tipo de elemento que desea eliminar</p>
            </div>
        `;
        return;
    }
    
    tipoEliminacionActual = tipoElemento;
    
    try {
        // Mostrar loading
        contenedor.innerHTML = `
            <div class="mensaje-cargando-eliminar">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <p>Cargando ${tipoElemento}s...</p>
            </div>
        `;
        
        // Cargar elementos según el tipo
        await cargarElementosParaEliminar(tipoElemento);
        
        // Mostrar interfaz de selección
        mostrarInterfazEliminacion(tipoElemento);
        
    } catch (error) {
        console.error('❌ Error cargando elementos:', error);
        contenedor.innerHTML = `
            <div class="mensaje-error-eliminar">
                <i class="fa-solid fa-exclamation-triangle"></i>
                <p>Error al cargar los elementos: ${error.message}</p>
            </div>
        `;
    }
}

// ✅ CARGAR ELEMENTOS PARA ELIMINAR
async function cargarElementosParaEliminar(tipo) {
    console.log(`📥 Cargando ${tipo}s para eliminación...`);
    
    let url = '';
    
    switch(tipo) {
        case 'requerimiento':
            url = '/api/requerimientos/';
            break;
        case 'subgrupo':
            url = '/api/subgrupos/';
            break;
        case 'grupo':
            url = '/api/grupos/';
            break;
        case 'familia':
            url = '/api/familias/';
            break;
        default:
            throw new Error('Tipo de elemento no válido');
    }
    
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
    
    elementosParaEliminar = await response.json();
    console.log(`✅ ${elementosParaEliminar.length} ${tipo}s cargados`);
}

// ✅ MOSTRAR INTERFAZ DE ELIMINACIÓN
function mostrarInterfazEliminacion(tipo) {
    const contenedor = document.getElementById('contenedor-eliminacion');
    const tipoNombre = obtenerNombreTipo(tipo);
    
    if (elementosParaEliminar.length === 0) {
        contenedor.innerHTML = `
            <div class="mensaje-vacio-eliminar">
                <i class="fa-solid fa-inbox"></i>
                <p>No hay ${tipoNombre}s registrados</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="header-eliminacion">
            <h4>Seleccione el ${tipoNombre} a eliminar:</h4>
            <div class="search-container-eliminar">
                <input type="text" id="buscar-${tipo}" placeholder="Buscar ${tipoNombre}..." 
                       class="search-input-eliminar" onkeyup="filtrarElementos('${tipo}')">
                <i class="fa-solid fa-magnifying-glass search-icon-eliminar"></i>
            </div>
        </div>
        <div id="lista-${tipo}s-eliminar" class="lista-elementos-eliminar">
    `;
    
    elementosParaEliminar.forEach(elemento => {
        const infoAdicional = obtenerInfoAdicional(elemento, tipo);
        
        html += `
            <div class="elemento-item-eliminar" data-id="${elemento.id || elemento.id_requerimiento || elemento.id_subgrupo_denuncia || elemento.id_grupo_denuncia || elemento.id_familia_denuncia}">
                <div class="elemento-info-eliminar">
                    <strong>${elemento.nombre || elemento.nombre_requerimiento || elemento.nombre_subgrupo_denuncia || elemento.nombre_grupo_denuncia || elemento.nombre_familia_denuncia}</strong>
                    ${infoAdicional}
                </div>
                <div class="elemento-acciones-eliminar">
                    <button type="button" class="btn-seleccionar-eliminar" onclick="seleccionarElementoEliminar('${tipo}', ${elemento.id || elemento.id_requerimiento || elemento.id_subgrupo_denuncia || elemento.id_grupo_denuncia || elemento.id_familia_denuncia})">
                        <i class="fa-solid fa-check"></i> Seleccionar
                    </button>
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    // Información de advertencia
    html += `
        <div class="advertencia-eliminacion">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <div>
                <strong>¡ADVERTENCIA!</strong>
                <p>Al eliminar un ${tipoNombre}, también se eliminarán todos los elementos que dependan de él.</p>
                ${tipo === 'familia' ? '<p>Se eliminarán grupos, subgrupos y requerimientos asociados.</p>' : ''}
                ${tipo === 'grupo' ? '<p>Se eliminarán subgrupos y requerimientos asociados.</p>' : ''}
                ${tipo === 'subgrupo' ? '<p>Se eliminarán requerimientos asociados.</p>' : ''}
                <p class="texto-peligro">Esta acción no se puede deshacer.</p>
            </div>
        </div>
    `;
    
    contenedor.innerHTML = html;
}

// ✅ OBTENER INFORMACIÓN ADICIONAL PARA CADA ELEMENTO
function obtenerInfoAdicional(elemento, tipo) {
    switch(tipo) {
        case 'requerimiento':
            return `
                <div class="info-adicional-eliminar">
                    <span class="clasificacion-badge ${elemento.clasificacion_requerimiento?.toLowerCase() || 'media'}">
                        ${elemento.clasificacion_requerimiento || 'Sin clasificación'}
                    </span>
                    <span class="codigo-elemento">${elemento.codigo_requerimiento || 'Sin código'}</span>
                </div>
                ${elemento.familia_nombre ? `
                <div class="jerarquia-eliminar">
                    ${elemento.familia_nombre} → ${elemento.grupo_nombre} → ${elemento.subgrupo_nombre}
                </div>
                ` : ''}
            `;
            
        case 'subgrupo':
            return `
                <div class="info-adicional-eliminar">
                    <span class="codigo-elemento">${elemento.codigo_subgrupo || 'Sin código'}</span>
                </div>
            `;
            
        case 'grupo':
            return `
                <div class="info-adicional-eliminar">
                    <span class="codigo-elemento">${elemento.codigo_grupo || 'Sin código'}</span>
                </div>
            `;
            
        case 'familia':
            return `
                <div class="info-adicional-eliminar">
                    <span class="codigo-elemento">${elemento.codigo_familia || 'Sin código'}</span>
                </div>
            `;
            
        default:
            return '';
    }
}

// ✅ OBTENER NOMBRE LEGIBLE DEL TIPO
function obtenerNombreTipo(tipo) {
    const nombres = {
        'requerimiento': 'Requerimiento',
        'subgrupo': 'Subgrupo',
        'grupo': 'Grupo',
        'familia': 'Familia'
    };
    return nombres[tipo] || tipo;
}

// ✅ FILTRAR ELEMENTOS EN LA LISTA
function filtrarElementos(tipo) {
    const searchTerm = document.getElementById(`buscar-${tipo}`).value.toLowerCase().trim();
    const items = document.querySelectorAll(`#lista-${tipo}s-eliminar .elemento-item-eliminar`);
    
    items.forEach(item => {
        const texto = item.textContent.toLowerCase();
        if (texto.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// ✅ SELECCIONAR ELEMENTO PARA ELIMINAR
function seleccionarElementoEliminar(tipo, id) {
    console.log(`🎯 Seleccionando ${tipo} con ID: ${id} para eliminar`);
    
    // Quitar selección anterior
    document.querySelectorAll('.elemento-item-eliminar').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Marcar como seleccionado
    const elementoItem = document.querySelector(`.elemento-item-eliminar[data-id="${id}"]`);
    if (elementoItem) {
        elementoItem.classList.add('selected');
    }
    
    // Encontrar el elemento en la lista
    elementoSeleccionadoEliminar = elementosParaEliminar.find(elemento => 
        elemento.id === id || 
        elemento.id_requerimiento === id ||
        elemento.id_subgrupo_denuncia === id ||
        elemento.id_grupo_denuncia === id ||
        elemento.id_familia_denuncia === id
    );
    
    if (elementoSeleccionadoEliminar) {
        // Habilitar botón de eliminar
        document.getElementById('btn-eliminar-confirmar').disabled = false;
        
        console.log(`✅ ${obtenerNombreTipo(tipo)} seleccionado:`, elementoSeleccionadoEliminar);
    }
}

// ✅ CONFIRMAR ELIMINACIÓN
async function confirmarEliminacion() {
    if (!elementoSeleccionadoEliminar || !tipoEliminacionActual) {
        mostrarError('No hay ningún elemento seleccionado para eliminar');
        return;
    }
    
    const tipoNombre = obtenerNombreTipo(tipoEliminacionActual);
    const nombreElemento = elementoSeleccionadoEliminar.nombre || 
                          elementoSeleccionadoEliminar.nombre_requerimiento ||
                          elementoSeleccionadoEliminar.nombre_subgrupo_denuncia ||
                          elementoSeleccionadoEliminar.nombre_grupo_denuncia ||
                          elementoSeleccionadoEliminar.nombre_familia_denuncia;
    
    // Mostrar confirmación
    const resultado = await Swal.fire({
        title: '¿Está seguro?',
        html: `
            <div style="text-align: left;">
                <p>Está a punto de eliminar el siguiente elemento:</p>
                <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <strong>${tipoNombre}:</strong> ${nombreElemento}<br>
                    <strong>ID:</strong> ${elementoSeleccionadoEliminar.id || elementoSeleccionadoEliminar.id_requerimiento || elementoSeleccionadoEliminar.id_subgrupo_denuncia || elementoSeleccionadoEliminar.id_grupo_denuncia || elementoSeleccionadoEliminar.id_familia_denuncia}
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
        cancelButtonText: 'Cancelar'
    });
    
    if (resultado.isConfirmed) {
        await ejecutarEliminacion();
    }
}

// ✅ EJECUTAR ELIMINACIÓN
async function ejecutarEliminacion() {
    if (!elementoSeleccionadoEliminar || !tipoEliminacionActual) return;
    
    const id = elementoSeleccionadoEliminar.id || 
               elementoSeleccionadoEliminar.id_requerimiento ||
               elementoSeleccionadoEliminar.id_subgrupo_denuncia ||
               elementoSeleccionadoEliminar.id_grupo_denuncia ||
               elementoSeleccionadoEliminar.id_familia_denuncia;
    
    const tipoNombre = obtenerNombreTipo(tipoEliminacionActual);
    const nombreElemento = elementoSeleccionadoEliminar.nombre || 
                          elementoSeleccionadoEliminar.nombre_requerimiento ||
                          elementoSeleccionadoEliminar.nombre_subgrupo_denuncia ||
                          elementoSeleccionadoEliminar.nombre_grupo_denuncia ||
                          elementoSeleccionadoEliminar.nombre_familia_denuncia;
    
    try {
        // Determinar la URL según el tipo
        let url = '';
        switch(tipoEliminacionActual) {
            case 'requerimiento':
                url = `/api/requerimientos/${id}/`;
                break;
            case 'subgrupo':
                url = `/api/subgrupos/${id}/`;
                break;
            case 'grupo':
                url = `/api/grupos/${id}/`;
                break;
            case 'familia':
                url = `/api/familias/${id}/`;
                break;
        }
        
        console.log(`🗑️ Eliminando ${tipoEliminacionActual} en: ${url}`);
        
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}`);
        }
        
        // Mostrar éxito y recargar
        Swal.fire({
            title: '¡Eliminado!',
            html: `
                <p>El ${tipoNombre} <strong>"${nombreElemento}"</strong> ha sido eliminado correctamente.</p>
            `,
            icon: 'success',
            confirmButtonText: 'Aceptar',
            timer: 2000,
            didClose: () => {
                // Recargar la página
                window.location.reload();
            }
        });
        
    } catch (error) {
        console.error('❌ Error eliminando elemento:', error);
        
        let mensajeError = `Error al eliminar el ${tipoNombre}: ${error.message}`;
        
        // Mensajes más específicos para errores comunes
        if (error.message.includes('violates foreign key constraint')) {
            mensajeError = `No se puede eliminar este ${tipoNombre} porque tiene elementos dependientes. Elimine primero los elementos asociados.`;
        }
        
        Swal.fire({
            title: 'Error',
            text: mensajeError,
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    }
}

// ✅ CERRAR MODAL DE ELIMINACIÓN
function cerrarModalEliminar() {
    console.log('❌ Cerrando modal de eliminación...');
    document.getElementById('modal-eliminar').style.display = 'none';
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

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('modal-eliminar');
    if (event.target === modal) {
        cerrarModalEliminar();
    }
}