// Variables globales
let familias = [];
let grupos = [];
let subgrupos = [];
let requerimientos = [];

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Inicializando sistema de requerimientos...');
    cargarDatosIniciales();
});

// Cargar todos los datos iniciales
async function cargarDatosIniciales() {
    try {
        console.log('📥 Cargando datos iniciales...');
        await cargarFamilias();
        await cargarTodosLosRequerimientos();
        console.log('✅ Datos iniciales cargados correctamente');
    } catch (error) {
        console.error('❌ Error cargando datos iniciales:', error);
        mostrarError('No se pudieron cargar los datos iniciales: ' + error.message);
    }
}

// Función mejorada para mostrar errores
function mostrarError(mensaje) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: mensaje,
        confirmButtonText: 'Entendido'
    });
}

// Función mejorada para mostrar éxito
function mostrarExito(mensaje) {
    Swal.fire({
        icon: 'success',
        title: 'Éxito',
        text: mensaje,
        confirmButtonText: 'Continuar',
        timer: 3000
    });
}

// Cargar familias desde la API (MEJORADA)
async function cargarFamilias() {
    try {
        console.log('📥 Cargando familias...');
        const response = await fetch('/api/familias/');
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        familias = await response.json();
        console.log('✅ Familias cargadas:', familias);
        
        const selectFamilia = document.getElementById('select-familia');
        selectFamilia.innerHTML = '<option value="">Seleccionar Familia</option>';
        
        familias.forEach(familia => {
            const option = document.createElement('option');
            option.value = familia.id_familia_denuncia || familia.id;
            option.textContent = familia.nombre_familia_denuncia;
            selectFamilia.appendChild(option);
        });
    } catch (error) {
        console.error('❌ Error cargando familias:', error);
        throw error;
    }
}

// Cargar grupos basados en familia seleccionada (MEJORADA)
async function cargarGrupos() {
    try {
        const familiaId = document.getElementById('select-familia').value;
        const selectGrupo = document.getElementById('select-grupo');
        const btnNuevoGrupo = document.querySelector('button[onclick="mostrarInput(\'grupo\')"]');
        
        if (!familiaId) {
            selectGrupo.innerHTML = '<option value="">Primero seleccione una familia</option>';
            selectGrupo.disabled = true;
            btnNuevoGrupo.disabled = true;
            return;
        }
        
        console.log(`📥 Cargando grupos para familia ${familiaId}...`);
        const response = await fetch(`/api/grupos/?familia_id=${familiaId}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        grupos = await response.json();
        console.log('✅ Grupos cargados:', grupos);
        
        selectGrupo.innerHTML = '<option value="">Seleccionar Grupo</option>';
        grupos.forEach(grupo => {
            const option = document.createElement('option');
            option.value = grupo.id_grupo_denuncia || grupo.id;
            option.textContent = grupo.nombre_grupo_denuncia;
            selectGrupo.appendChild(option);
        });
        
        selectGrupo.disabled = false;
        btnNuevoGrupo.disabled = false;
        
        // Limpiar niveles inferiores
        document.getElementById('select-subgrupo').innerHTML = '<option value="">Primero seleccione un grupo</option>';
        document.getElementById('select-subgrupo').disabled = true;
        document.getElementById('select-requerimiento').innerHTML = '<option value="">Primero seleccione un subgrupo</option>';
        document.getElementById('select-requerimiento').disabled = true;
        
    } catch (error) {
        console.error('❌ Error cargando grupos:', error);
        mostrarError('Error cargando grupos: ' + error.message);
    }
}

// Cargar subgrupos basados en grupo seleccionado (MEJORADA)
async function cargarSubgrupos() {
    try {
        const grupoId = document.getElementById('select-grupo').value;
        const selectSubgrupo = document.getElementById('select-subgrupo');
        const btnNuevoSubgrupo = document.querySelector('button[onclick="mostrarInput(\'subgrupo\')"]');
        
        if (!grupoId) {
            selectSubgrupo.innerHTML = '<option value="">Primero seleccione un grupo</option>';
            selectSubgrupo.disabled = true;
            btnNuevoSubgrupo.disabled = true;
            return;
        }
        
        console.log(`📥 Cargando subgrupos para grupo ${grupoId}...`);
        const response = await fetch(`/api/subgrupos/?grupo_id=${grupoId}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        subgrupos = await response.json();
        console.log('✅ Subgrupos cargados:', subgrupos);
        
        selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        subgrupos.forEach(subgrupo => {
            const option = document.createElement('option');
            option.value = subgrupo.id_subgrupo_denuncia || subgrupo.id;
            option.textContent = subgrupo.nombre_subgrupo_denuncia;
            selectSubgrupo.appendChild(option);
        });
        
        selectSubgrupo.disabled = false;
        btnNuevoSubgrupo.disabled = false;
        
        // Limpiar requerimiento
        document.getElementById('select-requerimiento').innerHTML = '<option value="">Primero seleccione un subgrupo</option>';
        document.getElementById('select-requerimiento').disabled = true;
        
    } catch (error) {
        console.error('❌ Error cargando subgrupos:', error);
        mostrarError('Error cargando subgrupos: ' + error.message);
    }
}


// Habilitar requerimiento cuando se selecciona subgrupo (MEJORADA)
async function habilitarRequerimiento() {
    try {
        const subgrupoId = document.getElementById('select-subgrupo').value;
        const selectRequerimiento = document.getElementById('select-requerimiento');
        const btnNuevoRequerimiento = document.querySelector('button[onclick="mostrarInput(\'requerimiento\')"]');
        
        if (!subgrupoId) {
            selectRequerimiento.innerHTML = '<option value="">Primero seleccione un subgrupo</option>';
            selectRequerimiento.disabled = true;
            btnNuevoRequerimiento.disabled = true;
            return;
        }
        
        console.log(`📥 Cargando requerimientos para subgrupo ${subgrupoId}...`);
        const response = await fetch(`/api/requerimientos/?subgrupo_id=${subgrupoId}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        requerimientos = await response.json();
        console.log('✅ Requerimientos cargados:', requerimientos);
        
        selectRequerimiento.innerHTML = '<option value="">Seleccionar Requerimiento</option>';
        requerimientos.forEach(req => {
            const option = document.createElement('option');
            option.value = req.id_requerimiento || req.id;
            option.textContent = `${req.nombre_requerimiento} (${req.clasificacion_requerimiento})`;
            selectRequerimiento.appendChild(option);
        });
        
        selectRequerimiento.disabled = false;
        btnNuevoRequerimiento.disabled = false;
        
    } catch (error) {
        console.error('❌ Error cargando requerimientos:', error);
        mostrarError('Error cargando requerimientos: ' + error.message);
    }
}

// Mostrar/ocultar inputs para nuevos elementos
function mostrarInput(tipo) {
    const inputDiv = document.getElementById(`input-${tipo}`);
    const todosInputs = document.querySelectorAll('.input-nuevo');
    
    // Ocultar todos los inputs primero
    todosInputs.forEach(input => {
        input.style.display = 'none';
    });
    
    // Mostrar el input seleccionado
    inputDiv.style.display = 'block';
}

// Agregar nueva familia (MEJORADA)
async function agregarFamilia() {
    const nombre = document.getElementById('nueva-familia').value.trim();
    
    if (!nombre) {
        mostrarError('Ingrese un nombre para la familia');
        return;
    }
    
    try {
        console.log(`➕ Agregando nueva familia: ${nombre}`);
        
        const response = await fetch('/api/familias/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ nombre: nombre })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP: ${response.status}`);
        }
        
        const nuevaFamilia = await response.json();
        console.log('✅ Familia agregada:', nuevaFamilia);
        
        document.getElementById('nueva-familia').value = '';
        document.getElementById('input-familia').style.display = 'none';
        
        await cargarFamilias();
        
        // Seleccionar la nueva familia
        document.getElementById('select-familia').value = nuevaFamilia.id_familia_denuncia || nuevaFamilia.id;
        await cargarGrupos();
        
        mostrarExito('Familia agregada correctamente');
        
    } catch (error) {
        console.error('❌ Error agregando familia:', error);
        mostrarError('Error al agregar familia: ' + error.message);
    }
}

// Agregar nuevo grupo (MEJORADA)
async function agregarGrupo() {
    const nombre = document.getElementById('nuevo-grupo').value.trim();
    const familiaId = document.getElementById('select-familia').value;
    
    if (!nombre || !familiaId) {
        mostrarError('Ingrese un nombre y seleccione una familia');
        return;
    }
    
    try {
        console.log(`➕ Agregando nuevo grupo: ${nombre} para familia ${familiaId}`);
        
        const response = await fetch('/api/grupos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ 
                nombre: nombre,
                familia_id: familiaId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP: ${response.status}`);
        }
        
        const nuevoGrupo = await response.json();
        console.log('✅ Grupo agregado:', nuevoGrupo);
        
        document.getElementById('nuevo-grupo').value = '';
        document.getElementById('input-grupo').style.display = 'none';
        
        await cargarGrupos();
        
        // Seleccionar el nuevo grupo
        document.getElementById('select-grupo').value = nuevoGrupo.id_grupo_denuncia || nuevoGrupo.id;
        await cargarSubgrupos();
        
        mostrarExito('Grupo agregado correctamente');
        
    } catch (error) {
        console.error('❌ Error agregando grupo:', error);
        mostrarError('Error al agregar grupo: ' + error.message);
    }
}

// Agregar nuevo subgrupo (MEJORADA)
async function agregarSubgrupo() {
    const nombre = document.getElementById('nuevo-subgrupo').value.trim();
    const grupoId = document.getElementById('select-grupo').value;
    
    if (!nombre || !grupoId) {
        mostrarError('Ingrese un nombre y seleccione un grupo');
        return;
    }
    
    try {
        console.log(`➕ Agregando nuevo subgrupo: ${nombre} para grupo ${grupoId}`);
        
        const response = await fetch('/api/subgrupos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ 
                nombre: nombre,
                grupo_id: grupoId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP: ${response.status}`);
        }
        
        const nuevoSubgrupo = await response.json();
        console.log('✅ Subgrupo agregado:', nuevoSubgrupo);
        
        document.getElementById('nuevo-subgrupo').value = '';
        document.getElementById('input-subgrupo').style.display = 'none';
        
        await cargarSubgrupos();
        
        // Seleccionar el nuevo subgrupo
        document.getElementById('select-subgrupo').value = nuevoSubgrupo.id_subgrupo_denuncia || nuevoSubgrupo.id;
        await habilitarRequerimiento();
        
        mostrarExito('Subgrupo agregado correctamente');
        
    } catch (error) {
        console.error('❌ Error agregando subgrupo:', error);
        mostrarError('Error al agregar subgrupo: ' + error.message);
    }
}

// Agregar nuevo requerimiento (MEJORADA)
async function agregarRequerimiento() {
    const nombre = document.getElementById('nuevo-requerimiento').value.trim();
    const subgrupoId = document.getElementById('select-subgrupo').value;
    const clasificacion = document.getElementById('clasificacion-requerimiento').value;
    const descripcion = document.getElementById('descripcion-requerimiento').value.trim();
    
    if (!nombre || !subgrupoId) {
        mostrarError('Ingrese un nombre y seleccione un subgrupo');
        return;
    }
    
    try {
        console.log(`➕ Agregando nuevo requerimiento: ${nombre} para subgrupo ${subgrupoId}`);
        
        const response = await fetch('/api/requerimientos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ 
                nombre: nombre,
                subgrupo_id: subgrupoId,
                clasificacion: clasificacion,
                descripcion: descripcion
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error HTTP: ${response.status}`);
        }
        
        const nuevoRequerimiento = await response.json();
        console.log('✅ Requerimiento agregado:', nuevoRequerimiento);
        
        // Limpiar formulario
        document.getElementById('nuevo-requerimiento').value = '';
        document.getElementById('descripcion-requerimiento').value = '';
        document.getElementById('input-requerimiento').style.display = 'none';
        
        await habilitarRequerimiento();
        await cargarTodosLosRequerimientos();
        
        // Seleccionar el nuevo requerimiento
        document.getElementById('select-requerimiento').value = nuevoRequerimiento.id_requerimiento || nuevoRequerimiento.id;
        
        mostrarExito('Requerimiento agregado correctamente');
        
    } catch (error) {
        console.error('❌ Error agregando requerimiento:', error);
        mostrarError('Error al agregar requerimiento: ' + error.message);
    }
}

// Función para guardar el requerimiento completo
async function guardarRequerimientoCompleto(event) {
    event.preventDefault();
    
    const requerimientoId = document.getElementById('select-requerimiento').value;
    
    if (!requerimientoId) {
        Swal.fire('Error', 'Debe seleccionar o crear un requerimiento', 'warning');
        return;
    }
    
    Swal.fire('Éxito', 'Requerimiento configurado correctamente', 'success');
    cerrarModalRequerimiento();
    await cargarTodosLosRequerimientos();
}

// Después de recibir la respuesta
console.log('🔧 DEBUG - Respuesta del servidor:', {
    status: response.status,
    result: result
});

// Cargar todos los requerimientos para la lista (MEJORADA)
async function cargarTodosLosRequerimientos() {
    try {
        console.log('📥 Cargando todos los requerimientos...');
        const response = await fetch('/api/requerimientos/');
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const todosRequerimientos = await response.json();
        console.log('✅ Todos los requerimientos cargados:', todosRequerimientos);
        
        const lista = document.getElementById('lista-requerimientos');
        lista.innerHTML = '';
        
        if (todosRequerimientos.length === 0) {
            lista.innerHTML = '<p class="sin-datos">No hay requerimientos registrados</p>';
            return;
        }
        
        todosRequerimientos.forEach(req => {
            const item = document.createElement('div');
            item.className = 'requerimiento-item';
            item.innerHTML = `
                <strong>${req.nombre_requerimiento}</strong>
                <span class="clasificacion ${req.clasificacion_requerimiento.toLowerCase()}">
                    ${req.clasificacion_requerimiento}
                </span>
            `;
            lista.appendChild(item);
        });
        
    } catch (error) {
        console.error('❌ Error cargando requerimientos:', error);
        mostrarError('Error cargando la lista de requerimientos: ' + error.message);
    }
}

// Funciones del modal
function abrirModalRequerimiento() {
    document.getElementById('modal-requerimiento').style.display = 'block';
}

function cerrarModalRequerimiento() {
    document.getElementById('modal-requerimiento').style.display = 'none';
    // Limpiar formulario
    document.getElementById('form-requerimiento').reset();
    // Ocultar todos los inputs nuevos
    document.querySelectorAll('.input-nuevo').forEach(input => {
        input.style.display = 'none';
    });
}

// Obtener token CSRF
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('modal-requerimiento');
    if (event.target === modal) {
        cerrarModalRequerimiento();
    }
}