// Variables globales para actualización
let todosRequerimientosActualizar = [];
let requerimientoSeleccionadoActualizar = null;
let familiasActualizar = [];
let gruposActualizar = [];
let subgruposActualizar = [];

// ✅ INICIALIZACIÓN MEJORADA
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Sistema de actualización listo');
    // No cargar datos aquí, se cargarán cuando se abra el modal
});

// ✅ FUNCIÓN COMPLETAMENTE REESCRITA PARA ABRIR MODAL
async function abrirModalActualizarRequerimiento() {
    console.log('📖 Abriendo modal de actualización...');
    
    try {
        // Mostrar modal inmediatamente
        document.getElementById('modal-actualizar-requerimiento').style.display = 'block';
        
        // ✅ RESETEAR COMPLETAMENTE EL MODAL
        resetearModalActualizar();
        
        // ✅ CARGAR DATOS FRESCOS CADA VEZ
        await cargarDatosInicialesActualizar();
        
        console.log('✅ Modal listo para usar');
        
    } catch (error) {
        console.error('❌ Error al abrir modal:', error);
        mostrarError('Error al cargar los datos: ' + error.message);
    }
}

// ✅ FUNCIÓN PARA RESETEAR COMPLETAMENTE EL MODAL
function resetearModalActualizar() {
    console.log('🔄 Reseteando modal...');
    
    // Limpiar selección
    requerimientoSeleccionadoActualizar = null;
    
    // Limpiar búsqueda
    document.getElementById('buscar-requerimiento').value = '';
    document.getElementById('lista-requerimientos-actualizar').innerHTML = 
        '<div class="requerimiento-item-actualizar">Ingrese un término de búsqueda</div>';
    
    // Ocultar secciones
    document.getElementById('info-requerimiento-actualizar').style.display = 'none';
    document.getElementById('form-edicion-actualizar').style.display = 'none';
    
    // Deshabilitar botón
    document.getElementById('btn-actualizar-requerimiento').disabled = true;
    
    // ✅ RESETEAR FORMULARIO COMPLETAMENTE
    document.getElementById('form-actualizar-requerimiento').reset();
    
    // ✅ RESETEAR SELECTS CON OPCIONES BÁSICAS
    resetearSelectsActualizar();
}

// ✅ FUNCIÓN PARA RESETEAR SELECTS
function resetearSelectsActualizar() {
    // Select de clasificación (siempre disponible)
    const selectClasificacion = document.getElementById('nueva-clasificacion-requerimiento');
    selectClasificacion.innerHTML = `
        <option value="">Seleccionar Clasificación</option>
        <option value="Baja">Baja</option>
        <option value="Media">Media</option>
        <option value="Alta">Alta</option>
    `;
    selectClasificacion.disabled = false;
    
    // Select de familia (se cargará con datos)
    const selectFamilia = document.getElementById('select-familia-actualizar');
    selectFamilia.innerHTML = '<option value="">Seleccionar Familia</option>';
    selectFamilia.disabled = false; // Habilitar desde el inicio
    
    // Select de grupo (vacío hasta seleccionar familia)
    const selectGrupo = document.getElementById('select-grupo-actualizar');
    selectGrupo.innerHTML = '<option value="">Seleccionar Grupo</option>';
    selectGrupo.disabled = true;
    
    // Select de subgrupo (vacío hasta seleccionar grupo)
    const selectSubgrupo = document.getElementById('select-subgrupo-actualizar');
    selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
    selectSubgrupo.disabled = true;
}

// ✅ CARGAR DATOS INICIALES MEJORADO
async function cargarDatosInicialesActualizar() {
    try {
        console.log('📥 Cargando datos iniciales...');
        
        // Cargar en paralelo para mayor velocidad
        await Promise.all([
            cargarTodosRequerimientosActualizar(),
            cargarFamiliasActualizar()
        ]);
        
        console.log('✅ Datos cargados correctamente');
        
    } catch (error) {
        console.error('❌ Error cargando datos iniciales:', error);
        throw error;
    }
}

// ✅ CARGAR REQUERIMIENTOS CON INFORMACIÓN COMPLETA
async function cargarTodosRequerimientosActualizar() {
    try {
        console.log('📋 Cargando requerimientos con información completa...');
        const response = await fetch('/api/requerimientos/');
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        
        todosRequerimientosActualizar = await response.json();
        console.log(`✅ ${todosRequerimientosActualizar.length} requerimientos cargados`);
        
        // ✅ DEBUG: Verificar la estructura de los datos
        if (todosRequerimientosActualizar.length > 0) {
            console.log('🔍 Estructura del primer requerimiento:', todosRequerimientosActualizar[0]);
        }
        
    } catch (error) {
        console.error('❌ Error cargando requerimientos:', error);
        throw error;
    }
}

// ✅ CARGAR FAMILIAS MEJORADO CON DEBUG
async function cargarFamiliasActualizar() {
    try {
        console.log('🏠 Cargando familias...');
        const response = await fetch('/api/familias/');
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        
        familiasActualizar = await response.json();
        const select = document.getElementById('select-familia-actualizar');
        
        // Limpiar y cargar opciones
        select.innerHTML = '<option value="">Seleccionar Familia</option>';
        
        familiasActualizar.forEach(familia => {
            const option = document.createElement('option');
            option.value = familia.id_familia_denuncia || familia.id;
            option.textContent = `${familia.codigo_familia || ''} ${familia.nombre_familia_denuncia}`.trim();
            select.appendChild(option);
        });
        
        // ✅ ASEGURAR QUE ESTÉ HABILITADO
        select.disabled = false;
        console.log(`✅ ${familiasActualizar.length} familias cargadas:`, familiasActualizar);
        
    } catch (error) {
        console.error('❌ Error cargando familias:', error);
        throw error;
    }
}

// ✅ CARGAR GRUPOS MEJORADO
async function cargarGruposActualizar() {
    const familiaId = document.getElementById('select-familia-actualizar').value;
    const selectGrupo = document.getElementById('select-grupo-actualizar');
    
    if (!familiaId) {
        selectGrupo.innerHTML = '<option value="">Seleccionar Grupo</option>';
        selectGrupo.disabled = true;
        
        // También limpiar subgrupo
        document.getElementById('select-subgrupo-actualizar').innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        document.getElementById('select-subgrupo-actualizar').disabled = true;
        return;
    }
    
    try {
        console.log(`📊 Cargando grupos para familia ${familiaId}...`);
        const response = await fetch(`/api/grupos/?familia_id=${familiaId}`);
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        
        gruposActualizar = await response.json();
        selectGrupo.innerHTML = '<option value="">Seleccionar Grupo</option>';
        
        gruposActualizar.forEach(grupo => {
            const option = document.createElement('option');
            option.value = grupo.id_grupo_denuncia;
            option.textContent = `${grupo.codigo_grupo || ''} ${grupo.nombre_grupo_denuncia}`.trim();
            selectGrupo.appendChild(option);
        });
        
        selectGrupo.disabled = false;
        
        // Limpiar subgrupo
        document.getElementById('select-subgrupo-actualizar').innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        document.getElementById('select-subgrupo-actualizar').disabled = true;
        
        console.log(`✅ ${gruposActualizar.length} grupos cargados`);
        
    } catch (error) {
        console.error('❌ Error cargando grupos:', error);
        mostrarError('Error cargando grupos: ' + error.message);
    }
}

// ✅ CARGAR SUBGRUPOS MEJORADO
async function cargarSubgruposActualizar() {
    const grupoId = document.getElementById('select-grupo-actualizar').value;
    const selectSubgrupo = document.getElementById('select-subgrupo-actualizar');
    
    if (!grupoId) {
        selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        selectSubgrupo.disabled = true;
        return;
    }
    
    try {
        console.log(`📑 Cargando subgrupos para grupo ${grupoId}...`);
        const response = await fetch(`/api/subgrupos/?grupo_id=${grupoId}`);
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        
        subgruposActualizar = await response.json();
        selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        
        subgruposActualizar.forEach(subgrupo => {
            const option = document.createElement('option');
            option.value = subgrupo.id_subgrupo_denuncia;
            option.textContent = `${subgrupo.codigo_subgrupo || ''} ${subgrupo.nombre_subgrupo_denuncia}`.trim();
            selectSubgrupo.appendChild(option);
        });
        
        selectSubgrupo.disabled = false;
        console.log(`✅ ${subgruposActualizar.length} subgrupos cargados`);
        
    } catch (error) {
        console.error('❌ Error cargando subgrupos:', error);
        mostrarError('Error cargando subgrupos: ' + error.message);
    }
}

// ✅ BÚSQUEDA MEJORADA CON DEBOUNCE
let timeoutBusqueda;
function buscarRequerimientos() {
    clearTimeout(timeoutBusqueda);
    timeoutBusqueda = setTimeout(() => {
        ejecutarBusqueda();
    }, 300);
}

function ejecutarBusqueda() {
    const searchTerm = document.getElementById('buscar-requerimiento').value.toLowerCase().trim();
    const lista = document.getElementById('lista-requerimientos-actualizar');
    
    lista.innerHTML = '';
    
    if (!searchTerm) {
        lista.innerHTML = '<div class="requerimiento-item-actualizar">Ingrese un término de búsqueda</div>';
        return;
    }
    
    const resultados = todosRequerimientosActualizar.filter(req => 
        req.nombre_requerimiento.toLowerCase().includes(searchTerm) ||
        (req.descripcion_requerimiento && req.descripcion_requerimiento.toLowerCase().includes(searchTerm)) ||
        (req.codigo_requerimiento && req.codigo_requerimiento.toLowerCase().includes(searchTerm)) ||
        (req.familia_nombre && req.familia_nombre.toLowerCase().includes(searchTerm)) ||
        (req.grupo_nombre && req.grupo_nombre.toLowerCase().includes(searchTerm)) ||
        (req.subgrupo_nombre && req.subgrupo_nombre.toLowerCase().includes(searchTerm))
    );
    
    if (resultados.length === 0) {
        lista.innerHTML = '<div class="requerimiento-item-actualizar">No se encontraron requerimientos</div>';
        return;
    }
    
    resultados.forEach(requerimiento => {
        const item = document.createElement('div');
        item.className = 'requerimiento-item-actualizar';
        
        const infoJerarquia = requerimiento.familia_nombre && requerimiento.grupo_nombre && requerimiento.subgrupo_nombre 
            ? `${requerimiento.familia_nombre} → ${requerimiento.grupo_nombre} → ${requerimiento.subgrupo_nombre}`
            : 'Jerarquía no disponible';
            
        item.innerHTML = `
            <div style="flex: 1;">
                <strong>${requerimiento.nombre_requerimiento}</strong>
                <div style="font-size: 12px; color: #666; margin-top: 4px;">
                    <div><strong>Código:</strong> ${requerimiento.codigo_requerimiento || 'Sin código'}</div>
                    <div><strong>Ubicación:</strong> ${infoJerarquia}</div>
                </div>
            </div>
            <span class="clasificacion-badge-actualizar ${requerimiento.clasificacion_requerimiento.toLowerCase()}">
                ${requerimiento.clasificacion_requerimiento}
            </span>
        `;
        
        item.onclick = () => seleccionarRequerimientoActualizar(requerimiento, item);
        lista.appendChild(item);
    });
}

// ✅ SELECCIONAR REQUERIMIENTO MEJORADO CON JERARQUÍA
async function seleccionarRequerimientoActualizar(requerimiento, elemento) {
    console.log('🎯 Seleccionando requerimiento:', requerimiento);
    
    requerimientoSeleccionadoActualizar = requerimiento;
    
    // Actualizar UI
    document.querySelectorAll('.requerimiento-item-actualizar').forEach(item => {
        item.classList.remove('selected');
    });
    elemento.classList.add('selected');
    
    // Mostrar información del requerimiento
    document.getElementById('info-requerimiento-actualizar').style.display = 'block';
    document.getElementById('nombre-requerimiento-actualizar').textContent = requerimiento.nombre_requerimiento;
    document.getElementById('clasificacion-requerimiento-actualizar').textContent = requerimiento.clasificacion_requerimiento;
    document.getElementById('clasificacion-requerimiento-actualizar').className = 
        `clasificacion-badge-actualizar ${requerimiento.clasificacion_requerimiento.toLowerCase()}`;
    
    // ✅ ACTUALIZAR RUTA CON INFORMACIÓN COMPLETA
    const rutaElement = document.getElementById('ruta-completa-actualizar');
    if (requerimiento.familia_nombre && requerimiento.grupo_nombre && requerimiento.subgrupo_nombre) {
        rutaElement.textContent = `${requerimiento.familia_nombre} → ${requerimiento.grupo_nombre} → ${requerimiento.subgrupo_nombre}`;
        rutaElement.style.color = '#28a745'; // Verde para indicar que está bien
    } else {
        rutaElement.textContent = 'Información de jerarquía no disponible';
        rutaElement.style.color = '#dc3545'; // Rojo para indicar problema
    }
    
    // Rellenar formulario de edición
    document.getElementById('nuevo-nombre-requerimiento').value = requerimiento.nombre_requerimiento;
    document.getElementById('nueva-clasificacion-requerimiento').value = requerimiento.clasificacion_requerimiento;
    document.getElementById('nueva-descripcion-requerimiento').value = requerimiento.descripcion_requerimiento || '';
    
    // ✅ CARGAR LA JERARQUÍA ACTUAL EN LOS SELECTS
    await cargarJerarquiaActual(requerimiento);
    
    // Mostrar formulario de edición
    document.getElementById('form-edicion-actualizar').style.display = 'block';
    
    // Habilitar botón de actualizar
    document.getElementById('btn-actualizar-requerimiento').disabled = false;
    
    console.log('✅ Requerimiento seleccionado para actualizar');
}

// ✅ ACTUALIZAR REQUERIMIENTO CON CAMPOS CORRECTOS
async function actualizarRequerimiento() {
    if (!requerimientoSeleccionadoActualizar) {
        mostrarError('No hay ningún requerimiento seleccionado');
        return;
    }
    
    const nuevoNombre = document.getElementById('nuevo-nombre-requerimiento').value.trim();
    const nuevaClasificacion = document.getElementById('nueva-clasificacion-requerimiento').value;
    const nuevaDescripcion = document.getElementById('nueva-descripcion-requerimiento').value.trim();
    const nuevoSubgrupoId = document.getElementById('select-subgrupo-actualizar').value;
    
    if (!nuevoNombre) {
        mostrarError('El nombre del requerimiento es obligatorio');
        return;
    }
    
    if (!nuevaClasificacion) {
        mostrarError('La clasificación es obligatoria');
        return;
    }
    
    try {
        const datosActualizacion = {
            nombre_requerimiento: nuevoNombre,  // ✅ CAMPO CORRECTO
            clasificacion_requerimiento: nuevaClasificacion,  // ✅ CAMPO CORRECTO
            descripcion_requerimiento: nuevaDescripcion  // ✅ CAMPO CORRECTO
        };
        
        // Si se seleccionó un nuevo subgrupo, agregarlo a la actualización
        if (nuevoSubgrupoId) {
            datosActualizacion.id_subgrupo_denuncia = parseInt(nuevoSubgrupoId);
        }
        
        console.log('🔄 Actualizando requerimiento:', datosActualizacion);
        
        const response = await fetch(`/api/requerimientos/${requerimientoSeleccionadoActualizar.id_requerimiento}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(datosActualizacion)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
        }
        
        const requerimientoActualizado = await response.json();
        console.log('✅ Requerimiento actualizado:', requerimientoActualizado);
        
        // ✅ MOSTRAR MENSAJE Y RECARGAR INMEDIATAMENTE
        Swal.fire({
            icon: 'success',
            title: '¡Actualizado!',
            text: 'Requerimiento actualizado correctamente',
            confirmButtonText: 'Aceptar',
            timer: 1500,
            didClose: () => {
                // ✅ RECARGAR LA PÁGINA INMEDIATAMENTE
                console.log('🔄 Recargando página...');
                window.location.reload();
            }
        });
        
    } catch (error) {
        console.error('❌ Error actualizando requerimiento:', error);
        mostrarError('Error al actualizar requerimiento: ' + error.message);
    }
}

// ✅ CERRAR MODAL MEJORADO
function cerrarModalActualizarRequerimiento() {
    console.log('❌ Cerrando modal...');
    document.getElementById('modal-actualizar-requerimiento').style.display = 'none';
}

// ✅ FUNCIONES DE UTILIDAD (sin cambios)
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
    const modal = document.getElementById('modal-actualizar-requerimiento');
    if (event.target === modal) {
        cerrarModalActualizarRequerimiento();
    }
}

// ✅ CARGAR JERARQUÍA ACTUAL DEL REQUERIMIENTO SELECCIONADO - CORREGIDA
async function cargarJerarquiaActual(requerimiento) {
    try {
        console.log('🗺️ Cargando jerarquía actual del requerimiento...');
        
        // ✅ OBTENER LA JERARQUÍA COMPLETA DESDE LA API ESPECÍFICA
        const response = await fetch(`/api/requerimiento_ruta_completa/${requerimiento.id_requerimiento}/`);
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const jerarquia = await response.json();
        console.log('✅ Jerarquía obtenida:', jerarquia);
        
        // ✅ USAR LA INFORMACIÓN DE LA JERARQUÍA COMPLETA
        if (jerarquia.familia && jerarquia.grupo && jerarquia.subgrupo) {
            
            // Seleccionar familia
            const selectFamilia = document.getElementById('select-familia-actualizar');
            if (selectFamilia) {
                // Buscar la familia en las opciones disponibles
                for (let option of selectFamilia.options) {
                    if (option.value == jerarquia.familia.id) {
                        selectFamilia.value = jerarquia.familia.id;
                        console.log('✅ Familia seleccionada:', jerarquia.familia.nombre);
                        break;
                    }
                }
                
                // Si se seleccionó una familia, cargar sus grupos
                if (selectFamilia.value) {
                    await cargarGruposActualizar();
                    
                    // Seleccionar grupo
                    const selectGrupo = document.getElementById('select-grupo-actualizar');
                    if (selectGrupo) {
                        for (let option of selectGrupo.options) {
                            if (option.value == jerarquia.grupo.id) {
                                selectGrupo.value = jerarquia.grupo.id;
                                console.log('✅ Grupo seleccionado:', jerarquia.grupo.nombre);
                                break;
                            }
                        }
                        
                        // Si se seleccionó un grupo, cargar sus subgrupos
                        if (selectGrupo.value) {
                            await cargarSubgruposActualizar();
                            
                            // Seleccionar subgrupo
                            const selectSubgrupo = document.getElementById('select-subgrupo-actualizar');
                            if (selectSubgrupo) {
                                for (let option of selectSubgrupo.options) {
                                    if (option.value == jerarquia.subgrupo.id) {
                                        selectSubgrupo.value = jerarquia.subgrupo.id;
                                        console.log('✅ Subgrupo seleccionado:', jerarquia.subgrupo.nombre);
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // ✅ ACTUALIZAR LA RUTA COMPLETA EN LA INTERFAZ
            const rutaElement = document.getElementById('ruta-completa-actualizar');
            rutaElement.textContent = `${jerarquia.familia.nombre} → ${jerarquia.grupo.nombre} → ${jerarquia.subgrupo.nombre}`;
            rutaElement.style.color = '#28a745';
            
        } else {
            console.warn('⚠️ Información de jerarquía incompleta en la respuesta');
            mostrarError('No se pudo cargar la información completa de la jerarquía');
        }
        
    } catch (error) {
        console.error('❌ Error cargando jerarquía actual:', error);
        mostrarError('Error al cargar la jerarquía: ' + error.message);
    }
}