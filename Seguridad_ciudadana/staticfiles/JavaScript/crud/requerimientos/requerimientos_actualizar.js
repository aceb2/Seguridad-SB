// Variables globales
let requerimientoSeleccionado = null;
let timeoutBusqueda = null;

// Función para abrir el modal de actualizar requerimiento
function abrirModalActualizarRequerimiento() {
    const modal = document.getElementById('modal-actualizar-requerimiento');
    modal.style.display = 'block';
    
    // Limpiar formulario
    limpiarFormularioActualizar();
    
    // Cargar familias para el selector de cambio
    cargarFamiliasActualizar();
    
    // Enfocar el campo de búsqueda
    setTimeout(() => {
        document.getElementById('buscar-requerimiento').focus();
    }, 100);
}

// Función para cerrar el modal de actualizar requerimiento
function cerrarModalActualizarRequerimiento() {
    const modal = document.getElementById('modal-actualizar-requerimiento');
    modal.style.display = 'none';
    requerimientoSeleccionado = null;
}

// Función para limpiar el formulario de actualizar
function limpiarFormularioActualizar() {
    document.getElementById('buscar-requerimiento').value = '';
    document.getElementById('lista-requerimientos-actualizar').innerHTML = '';
    document.getElementById('info-requerimiento-actualizar').style.display = 'none';
    document.getElementById('form-edicion-actualizar').style.display = 'none';
    document.getElementById('btn-actualizar-requerimiento').disabled = true;
    
    // Limpiar campos de edición
    document.getElementById('nuevo-nombre-requerimiento').value = '';
    document.getElementById('nueva-clasificacion-requerimiento').value = 'Media';
    document.getElementById('nueva-descripcion-requerimiento').value = '';
    
    // Limpiar selectores de cambio de subgrupo
    document.getElementById('select-familia-actualizar').innerHTML = '<option value="">Seleccionar Familia</option>';
    document.getElementById('select-grupo-actualizar').innerHTML = '<option value="">Seleccionar Grupo</option>';
    document.getElementById('select-grupo-actualizar').disabled = true;
    document.getElementById('select-subgrupo-actualizar').innerHTML = '<option value="">Seleccionar Subgrupo</option>';
    document.getElementById('select-subgrupo-actualizar').disabled = true;
}

// Función para buscar requerimientos
function buscarRequerimientos() {
    clearTimeout(timeoutBusqueda);
    
    timeoutBusqueda = setTimeout(() => {
        const query = document.getElementById('buscar-requerimiento').value.trim();
        const lista = document.getElementById('lista-requerimientos-actualizar');
        
        if (query.length < 2) {
            lista.innerHTML = '<div class="sin-resultados">Escriba al menos 2 caracteres para buscar</div>';
            return;
        }
        
        // Mostrar loading
        lista.innerHTML = '<div class="loading">Buscando requerimientos...</div>';
        
        // Realizar búsqueda en los requerimientos ya cargados
        const requerimientos = Array.from(document.querySelectorAll('.requerimiento-item'));
        const resultados = requerimientos.filter(req => {
            const nombre = req.querySelector('.requerimiento-nombre').textContent.toLowerCase();
            const codigo = req.querySelector('.requerimiento-codigo').textContent.toLowerCase();
            const busqueda = query.toLowerCase();
            
            return nombre.includes(busqueda) || codigo.includes(busqueda);
        });
        
        mostrarResultadosBusqueda(resultados, query);
        
    }, 500);
}

// Función para mostrar resultados de búsqueda
function mostrarResultadosBusqueda(resultados, query) {
    const lista = document.getElementById('lista-requerimientos-actualizar');
    
    if (resultados.length === 0) {
        lista.innerHTML = `
            <div class="sin-resultados">
                <i class="fa-solid fa-search"></i>
                <p>No se encontraron requerimientos para "${query}"</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="resultados-titulo">Resultados de búsqueda:</div>';
    
    resultados.slice(0, 10).forEach(reqElement => {
        const id = reqElement.dataset.id;
        const nombre = reqElement.querySelector('.requerimiento-nombre').textContent;
        const codigo = reqElement.querySelector('.requerimiento-codigo').textContent;
        const clasificacion = reqElement.querySelector('.clasificacion-badge').textContent;
        const ruta = reqElement.querySelector('.requerimiento-ruta').textContent;
        
        html += `
            <div class="requerimiento-resultado-item" onclick="seleccionarRequerimientoActualizar('${id}')">
                <div class="resultado-header">
                    <span class="resultado-nombre">${nombre}</span>
                    <span class="resultado-codigo">${codigo}</span>
                </div>
                <div class="resultado-clasificacion">
                    <span class="clasificacion-badge ${clasificacion.toLowerCase()}">${clasificacion}</span>
                </div>
                <div class="resultado-ruta">${ruta}</div>
                <div class="resultado-accion">
                    <i class="fa-solid fa-chevron-right"></i>
                </div>
            </div>
        `;
    });
    
    if (resultados.length > 10) {
        html += `<div class="mas-resultados">+${resultados.length - 10} resultados más...</div>`;
    }
    
    lista.innerHTML = html;
}

// Función para seleccionar un requerimiento
async function seleccionarRequerimientoActualizar(requerimientoId) {
    try {
        // Mostrar loading
        document.getElementById('info-requerimiento-actualizar').style.display = 'none';
        document.getElementById('form-edicion-actualizar').style.display = 'none';
        document.getElementById('btn-actualizar-requerimiento').disabled = true;
        
        const response = await fetch(`/api/requerimientos/${requerimientoId}/`);
        
        if (!response.ok) {
            throw new Error('Error al cargar el requerimiento');
        }
        
        const requerimiento = await response.json();
        requerimientoSeleccionado = requerimiento;
        
        // Mostrar información del requerimiento
        mostrarInformacionRequerimiento(requerimiento);
        
        // Cargar datos en el formulario de edición
        cargarDatosFormularioEdicion(requerimiento);
        
        // Mostrar secciones
        document.getElementById('info-requerimiento-actualizar').style.display = 'block';
        document.getElementById('form-edicion-actualizar').style.display = 'block';
        document.getElementById('btn-actualizar-requerimiento').disabled = false;
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo cargar la información del requerimiento'
        });
    }
}

// Función para mostrar información del requerimiento seleccionado
function mostrarInformacionRequerimiento(requerimiento) {
    document.getElementById('nombre-requerimiento-actualizar').textContent = requerimiento.nombre_requerimiento;
    document.getElementById('clasificacion-requerimiento-actualizar').textContent = requerimiento.clasificacion_requerimiento;
    document.getElementById('clasificacion-requerimiento-actualizar').className = `clasificacion-badge ${requerimiento.clasificacion_requerimiento.toLowerCase()}`;
    
    // Construir ruta completa
    const ruta = `${requerimiento.familia_nombre} → ${requerimiento.grupo_nombre} → ${requerimiento.subgrupo_nombre}`;
    document.getElementById('ruta-completa-actualizar').textContent = ruta;
}

// Función para cargar datos en el formulario de edición
function cargarDatosFormularioEdicion(requerimiento) {
    document.getElementById('nuevo-nombre-requerimiento').value = requerimiento.nombre_requerimiento;
    document.getElementById('nueva-clasificacion-requerimiento').value = requerimiento.clasificacion_requerimiento;
    document.getElementById('nueva-descripcion-requerimiento').value = requerimiento.descripcion_requerimiento || '';
    
    // Seleccionar la familia actual en el selector de cambio
    if (requerimiento.id_familia_denuncia) {
        setTimeout(() => {
            document.getElementById('select-familia-actualizar').value = requerimiento.id_familia_denuncia;
            cargarGruposActualizar(requerimiento.id_grupo_denuncia);
        }, 100);
    }
}

// Función para cargar familias en el selector de actualizar
async function cargarFamiliasActualizar() {
    try {
        const response = await fetch('/api/familias/');
        const familias = await response.json();
        
        const select = document.getElementById('select-familia-actualizar');
        select.innerHTML = '<option value="">Seleccionar Familia</option>';
        
        familias.forEach(familia => {
            const option = document.createElement('option');
            option.value = familia.id;
            option.textContent = `${familia.codigo_familia} - ${familia.nombre_familia_denuncia}`;
            select.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error cargando familias:', error);
    }
}

// Función para cargar grupos en el selector de actualizar
async function cargarGruposActualizar(grupoSeleccionado = null) {
    const familiaId = document.getElementById('select-familia-actualizar').value;
    const selectGrupo = document.getElementById('select-grupo-actualizar');
    const selectSubgrupo = document.getElementById('select-subgrupo-actualizar');
    
    if (!familiaId) {
        selectGrupo.disabled = true;
        selectGrupo.innerHTML = '<option value="">Seleccionar Grupo</option>';
        selectSubgrupo.disabled = true;
        selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        return;
    }
    
    try {
        selectGrupo.disabled = true;
        selectGrupo.innerHTML = '<option value="">Cargando grupos...</option>';
        
        const response = await fetch(`/api/grupos/?familia_id=${familiaId}`);
        const grupos = await response.json();
        
        selectGrupo.innerHTML = '<option value="">Seleccionar Grupo</option>';
        grupos.forEach(grupo => {
            const option = document.createElement('option');
            option.value = grupo.id_grupo_denuncia;
            option.textContent = `${grupo.codigo_grupo} - ${grupo.nombre_grupo_denuncia}`;
            if (grupoSeleccionado && grupo.id_grupo_denuncia == grupoSeleccionado) {
                option.selected = true;
            }
            selectGrupo.appendChild(option);
        });
        
        selectGrupo.disabled = false;
        
        // Si se seleccionó un grupo, cargar sus subgrupos
        if (grupoSeleccionado) {
            cargarSubgruposActualizar(requerimientoSeleccionado.id_subgrupo_denuncia);
        }
        
    } catch (error) {
        console.error('Error cargando grupos:', error);
        selectGrupo.innerHTML = '<option value="">Error al cargar grupos</option>';
    }
}

// Función para cargar subgrupos en el selector de actualizar
async function cargarSubgruposActualizar(subgrupoSeleccionado = null) {
    const grupoId = document.getElementById('select-grupo-actualizar').value;
    const selectSubgrupo = document.getElementById('select-subgrupo-actualizar');
    
    if (!grupoId) {
        selectSubgrupo.disabled = true;
        selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        return;
    }
    
    try {
        selectSubgrupo.disabled = true;
        selectSubgrupo.innerHTML = '<option value="">Cargando subgrupos...</option>';
        
        const response = await fetch(`/api/subgrupos/?grupo_id=${grupoId}`);
        const subgrupos = await response.json();
        
        selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        subgrupos.forEach(subgrupo => {
            const option = document.createElement('option');
            option.value = subgrupo.id;
            option.textContent = `${subgrupo.codigo_subgrupo} - ${subgrupo.nombre_subgrupo_denuncia}`;
            if (subgrupoSeleccionado && subgrupo.id == subgrupoSeleccionado) {
                option.selected = true;
            }
            selectSubgrupo.appendChild(option);
        });
        
        selectSubgrupo.disabled = false;
        
    } catch (error) {
        console.error('Error cargando subgrupos:', error);
        selectSubgrupo.innerHTML = '<option value="">Error al cargar subgrupos</option>';
    }
}

// Función principal para actualizar el requerimiento
async function actualizarRequerimiento() {
    if (!requerimientoSeleccionado) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No hay ningún requerimiento seleccionado'
        });
        return;
    }
    
    // Obtener datos del formulario
    const nuevoNombre = document.getElementById('nuevo-nombre-requerimiento').value.trim();
    const nuevaClasificacion = document.getElementById('nueva-clasificacion-requerimiento').value;
    const nuevaDescripcion = document.getElementById('nueva-descripcion-requerimiento').value.trim();
    const nuevoSubgrupoId = document.getElementById('select-subgrupo-actualizar').value;
    
    // Validaciones básicas
    if (!nuevoNombre) {
        Swal.fire({
            icon: 'warning',
            title: 'Campo requerido',
            text: 'El nombre del requerimiento es obligatorio'
        });
        return;
    }
    
    // Preparar datos para enviar
    const datosActualizacion = {
        nombre_requerimiento: nuevoNombre,
        clasificacion_requerimiento: nuevaClasificacion,
        descripcion_requerimiento: nuevaDescripcion
    };
    
    // Solo agregar subgrupo si se seleccionó uno diferente
    if (nuevoSubgrupoId && nuevoSubgrupoId != requerimientoSeleccionado.id_subgrupo_denuncia) {
        datosActualizacion.id_subgrupo_denuncia_id = nuevoSubgrupoId;
    }
    
    try {
        // Mostrar loading
        document.getElementById('btn-actualizar-requerimiento').disabled = true;
        document.getElementById('btn-actualizar-requerimiento').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Actualizando...';
        
        const response = await fetch(`/api/requerimientos/${requerimientoSeleccionado.id_requerimiento}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(datosActualizacion)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al actualizar el requerimiento');
        }
        
        const resultado = await response.json();
        
        // Mostrar mensaje de éxito
        Swal.fire({
            icon: 'success',
            title: '¡Actualizado!',
            text: resultado.mensaje || 'Requerimiento actualizado correctamente',
            timer: 2000,
            showConfirmButton: false
        });
        
        // Cerrar modal después de éxito
        setTimeout(() => {
            cerrarModalActualizarRequerimiento();
            
            // Recargar la lista de requerimientos
            if (typeof cargarRequerimientos === 'function') {
                cargarRequerimientos();
            }
            
            // Recargar estadísticas
            if (typeof cargarEstadisticas === 'function') {
                cargarEstadisticas();
            }
        }, 2000);
        
    } catch (error) {
        console.error('Error actualizando requerimiento:', error);
        
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'No se pudo actualizar el requerimiento'
        });
        
        // Rehabilitar botón
        document.getElementById('btn-actualizar-requerimiento').disabled = false;
        document.getElementById('btn-actualizar-requerimiento').innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Actualizar Requerimiento';
    }
}

// Función auxiliar para obtener el token CSRF
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Event listeners para los selectores de cambio
document.getElementById('select-familia-actualizar').addEventListener('change', function() {
    const grupoSelect = document.getElementById('select-grupo-actualizar');
    const subgrupoSelect = document.getElementById('select-subgrupo-actualizar');
    
    grupoSelect.disabled = true;
    grupoSelect.innerHTML = '<option value="">Seleccionar Grupo</option>';
    subgrupoSelect.disabled = true;
    subgrupoSelect.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
    
    if (this.value) {
        cargarGruposActualizar();
    }
});

document.getElementById('select-grupo-actualizar').addEventListener('change', function() {
    const subgrupoSelect = document.getElementById('select-subgrupo-actualizar');
    
    subgrupoSelect.disabled = true;
    subgrupoSelect.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
    
    if (this.value) {
        cargarSubgruposActualizar();
    }
});

// Permitir cerrar modal con ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cerrarModalActualizarRequerimiento();
    }
});

// Cerrar modal al hacer clic fuera del contenido
document.getElementById('modal-actualizar-requerimiento').addEventListener('click', function(event) {
    if (event.target === this) {
        cerrarModalActualizarRequerimiento();
    }
});


// Función para manejar el cambio en el selector de familia (actualizar)
function cargarfamiliaActualizar() {
    const familiaId = document.getElementById('select-familia-actualizar').value;
    const grupoSelect = document.getElementById('select-grupo-actualizar');
    const subgrupoSelect = document.getElementById('select-subgrupo-actualizar');
    
    // Resetear selects dependientes
    grupoSelect.innerHTML = '<option value="">Seleccionar Grupo</option>';
    grupoSelect.disabled = true;
    subgrupoSelect.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
    subgrupoSelect.disabled = true;
    
    if (familiaId) {
        cargarGruposActualizar();
    }
}

// Función para manejar el cambio en el selector de grupo (actualizar)
function cargargruposActualizar() {
    const grupoId = document.getElementById('select-grupo-actualizar').value;
    const subgrupoSelect = document.getElementById('select-subgrupo-actualizar');
    
    // Resetear select de subgrupo
    subgrupoSelect.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
    subgrupoSelect.disabled = true;
    
    if (grupoId) {
        cargarSubgruposActualizar();
    }
}

// Función para manejar el cambio en el selector de subgrupo (actualizar)
function cargarSubgruposActualizar() {
    // Esta función se llama automáticamente cuando se carga el select
    // Puedes agregar lógica adicional aquí si es necesario
    console.log('Subgrupo seleccionado para cambio:', document.getElementById('select-subgrupo-actualizar').value);
}