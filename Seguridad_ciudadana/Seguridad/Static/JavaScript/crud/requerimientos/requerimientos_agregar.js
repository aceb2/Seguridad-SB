// Variables globales
let familias = [];
let grupos = [];
let subgrupos = [];
let requerimientos = [];

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Inicializando sistema de requerimientos...');
    cargarDatosIniciales();
    inicializarEventListeners();
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

// Cargar familias desde la API
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

// Cargar grupos basados en familia seleccionada
async function cargarGrupos() {
    try {
        const familiaId = document.getElementById('select-familia').value;
        const selectGrupo = document.getElementById('select-grupo');
        const btnNuevoGrupo = document.querySelector('button[onclick="mostrarInput(\'grupo\')"]');
        
        if (!familiaId) {
            selectGrupo.innerHTML = '<option value="">Primero seleccione una familia</option>';
            selectGrupo.disabled = true;
            btnNuevoGrupo.disabled = true;
            habilitarBotonGuardar();
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
        
        habilitarBotonGuardar();
        
    } catch (error) {
        console.error('❌ Error cargando grupos:', error);
        mostrarError('Error cargando grupos: ' + error.message);
    }
}

// Cargar subgrupos basados en grupo seleccionado
async function cargarSubgrupos() {
    try {
        const grupoId = document.getElementById('select-grupo').value;
        const selectSubgrupo = document.getElementById('select-subgrupo');
        const btnNuevoSubgrupo = document.querySelector('button[onclick="mostrarInput(\'subgrupo\')"]');
        
        console.log(`🔧 Cargando subgrupos para grupo: ${grupoId}`);
        
        if (!grupoId) {
            selectSubgrupo.innerHTML = '<option value="">Primero seleccione un grupo</option>';
            selectSubgrupo.disabled = true;
            btnNuevoSubgrupo.disabled = true;
            habilitarBotonGuardar();
            return;
        }
        
        const response = await fetch(`/api/subgrupos/?grupo_id=${grupoId}`);
        
        console.log('🔧 Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const subgruposData = await response.json();
        console.log('🔧 Subgrupos recibidos:', subgruposData);
        
        selectSubgrupo.innerHTML = '<option value="">Seleccionar Subgrupo</option>';
        
        if (subgruposData.length === 0) {
            selectSubgrupo.innerHTML += '<option value="" disabled>No hay subgrupos para este grupo</option>';
        } else {
            subgruposData.forEach(subgrupo => {
                const option = document.createElement('option');
                option.value = subgrupo.id_subgrupo_denuncia || subgrupo.id;
                option.textContent = subgrupo.nombre_subgrupo_denuncia || subgrupo.nombre;
                selectSubgrupo.appendChild(option);
            });
        }
        
        selectSubgrupo.disabled = false;
        btnNuevoSubgrupo.disabled = false;
        
        // Limpiar requerimiento
        document.getElementById('select-requerimiento').innerHTML = '<option value="">Primero seleccione un subgrupo</option>';
        document.getElementById('select-requerimiento').disabled = true;
        
        habilitarBotonGuardar();
        
    } catch (error) {
        console.error('❌ Error cargando subgrupos:', error);
        mostrarError('Error cargando subgrupos: ' + error.message);
    }
}

// Habilitar requerimiento cuando se selecciona subgrupo
async function habilitarRequerimiento() {
    try {
        const subgrupoId = document.getElementById('select-subgrupo').value;
        const selectRequerimiento = document.getElementById('select-requerimiento');
        const btnNuevoRequerimiento = document.querySelector('button[onclick="mostrarInput(\'requerimiento\')"]');
        
        if (!subgrupoId) {
            selectRequerimiento.innerHTML = '<option value="">Primero seleccione un subgrupo</option>';
            selectRequerimiento.disabled = true;
            btnNuevoRequerimiento.disabled = true;
            habilitarBotonGuardar();
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
        
        habilitarBotonGuardar();
        
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
    
    // Si es requerimiento, actualizar el estado del botón guardar
    if (tipo === 'requerimiento') {
        setTimeout(() => {
            habilitarBotonGuardar();
        }, 100);
    }
}

// Agregar nueva familia
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
            body: JSON.stringify({ 
                nombre: nombre 
            })
        });
        
        console.log('🔧 DEBUG Familia - Respuesta:', {
            status: response.status,
            ok: response.ok
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error response:', errorText);
            throw new Error(`Error HTTP: ${response.status} - ${errorText}`);
        }
        
        const nuevaFamilia = await response.json();
        console.log('✅ Familia agregada:', nuevaFamilia);
        
        // Validar respuesta
        if (!nuevaFamilia.id_familia_denuncia && !nuevaFamilia.id) {
            throw new Error('El servidor no devolvió un ID válido');
        }
        
        // Limpiar formulario
        document.getElementById('nueva-familia').value = '';
        document.getElementById('input-familia').style.display = 'none';
        
        // Recargar familias
        await cargarFamilias();
        
        // Seleccionar la nueva familia
        const familiaId = nuevaFamilia.id_familia_denuncia || nuevaFamilia.id;
        document.getElementById('select-familia').value = familiaId;
        
        // Cargar grupos para la nueva familia
        await cargarGrupos();
        
        mostrarExito('Familia agregada correctamente');
        
    } catch (error) {
        console.error('❌ Error agregando familia:', error);
        mostrarError('Error al agregar familia: ' + error.message);
    }
}

// Agregar nuevo grupo
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
        
        console.log('🔧 DEBUG Grupo - Respuesta:', {
            status: response.status,
            ok: response.ok
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error response:', errorText);
            throw new Error(`Error HTTP: ${response.status} - ${errorText}`);
        }
        
        const nuevoGrupo = await response.json();
        console.log('✅ Grupo agregado:', nuevoGrupo);
        
        // Validar respuesta
        if (!nuevoGrupo.id_grupo_denuncia && !nuevoGrupo.id) {
            throw new Error('El servidor no devolvió un ID válido');
        }
        
        // Limpiar formulario
        document.getElementById('nuevo-grupo').value = '';
        document.getElementById('input-grupo').style.display = 'none';
        
        // Recargar grupos
        await cargarGrupos();
        
        // Seleccionar el nuevo grupo
        const grupoId = nuevoGrupo.id_grupo_denuncia || nuevoGrupo.id;
        document.getElementById('select-grupo').value = grupoId;
        
        // Cargar subgrupos para el nuevo grupo
        await cargarSubgrupos();
        
        mostrarExito('Grupo agregado correctamente');
        
    } catch (error) {
        console.error('❌ Error agregando grupo:', error);
        mostrarError('Error al agregar grupo: ' + error.message);
    }
}

// Agregar nuevo subgrupo
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
            const errorText = await response.text();
            console.error('❌ Error response text:', errorText);
            throw new Error(`Error HTTP: ${response.status} - ${errorText}`);
        }
        
        const nuevoSubgrupo = await response.json();
        console.log('✅ Subgrupo agregado:', nuevoSubgrupo);
        
        // Validar que el subgrupo tenga los campos esperados
        if (!nuevoSubgrupo.id_subgrupo_denuncia && !nuevoSubgrupo.id) {
            console.error('❌ El servidor no devolvió un ID válido:', nuevoSubgrupo);
            throw new Error('El servidor no devolvió un ID válido para el subgrupo');
        }
        
        // Limpiar formulario
        document.getElementById('nuevo-subgrupo').value = '';
        document.getElementById('input-subgrupo').style.display = 'none';
        
        // Recargar los subgrupos
        await cargarSubgrupos();
        
        // Seleccionar el nuevo subgrupo
        const subgrupoId = nuevoSubgrupo.id_subgrupo_denuncia || nuevoSubgrupo.id;
        document.getElementById('select-subgrupo').value = subgrupoId;
        
        // Habilitar requerimientos
        await habilitarRequerimiento();
        
        mostrarExito('Subgrupo agregado correctamente');
        
    } catch (error) {
        console.error('❌ Error agregando subgrupo:', error);
        mostrarError('Error al agregar subgrupo: ' + error.message);
    }
}

// ✅ NUEVA FUNCIÓN: Agregar Requerimiento (botón específico)
async function agregarRequerimiento() {
    const nombre = document.getElementById('nuevo-requerimiento').value.trim();
    const subgrupoId = document.getElementById('select-subgrupo').value;
    const clasificacion = document.getElementById('clasificacion-requerimiento').value;
    const descripcion = document.getElementById('descripcion-requerimiento').value.trim();
    
    console.log('🔧 Datos para nuevo requerimiento:', {
        nombre,
        subgrupoId,
        clasificacion,
        descripcion
    });
    
    if (!nombre) {
        mostrarError('Ingrese un nombre para el requerimiento');
        return;
    }
    
    if (!subgrupoId) {
        mostrarError('Debe seleccionar un subgrupo primero');
        return;
    }
    
    try {
        console.log(`➕ Agregando nuevo requerimiento: ${nombre} para subgrupo ${subgrupoId}`);
        
        // Mostrar loading
        Swal.fire({
            title: 'Creando requerimiento...',
            text: 'Por favor espere',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

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
            const errorText = await response.text();
            throw new Error(`Error HTTP: ${response.status} - ${errorText}`);
        }

        const nuevoRequerimiento = await response.json();
        console.log('✅ Nuevo requerimiento creado:', nuevoRequerimiento);

        // Cerrar loading
        Swal.close();

        // Mostrar éxito con temporizador para recargar
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: 'Requerimiento creado correctamente. La página se recargará en 2 segundos...',
            timer: 2000,
            showConfirmButton: false,
            timerProgressBar: true,
            didClose: () => {
                // Recargar la página para mostrar el nuevo requerimiento en la lista
                location.reload();
            }
        });

        // También recargar después del timer por si acaso
        setTimeout(() => {
            location.reload();
        }, 2000);

    } catch (error) {
        console.error('❌ Error creando requerimiento:', error);
        Swal.close();
        mostrarError('Error al crear el requerimiento: ' + error.message);
    }
}

// Función para guardar el requerimiento completo (ACTUALIZADA CON RECARGA)
async function guardarRequerimientoCompleto(event) {
    event.preventDefault();
    
    const inputRequerimientoVisible = document.getElementById('input-requerimiento').style.display !== 'none';
    const nuevoRequerimientoNombre = document.getElementById('nuevo-requerimiento').value.trim();
    const requerimientoSeleccionado = document.getElementById('select-requerimiento').value;
    
    console.log('🔧 Debug guardarRequerimientoCompleto:', {
        inputRequerimientoVisible,
        nuevoRequerimientoNombre,
        requerimientoSeleccionado
    });

    // Caso 1: Hay un nuevo requerimiento escrito
    if (inputRequerimientoVisible && nuevoRequerimientoNombre) {
        console.log('📝 Creando nuevo requerimiento...');
        
        try {
            // Mostrar loading
            Swal.fire({
                title: 'Creando requerimiento...',
                text: 'Por favor espere',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            // Crear el nuevo requerimiento
            const subgrupoId = document.getElementById('select-subgrupo').value;
            const clasificacion = document.getElementById('clasificacion-requerimiento').value;
            const descripcion = document.getElementById('descripcion-requerimiento').value.trim();

            const response = await fetch('/api/requerimientos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ 
                    nombre: nuevoRequerimientoNombre,
                    subgrupo_id: subgrupoId,
                    clasificacion: clasificacion,
                    descripcion: descripcion
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error HTTP: ${response.status} - ${errorText}`);
            }

            const nuevoRequerimiento = await response.json();
            console.log('✅ Nuevo requerimiento creado:', nuevoRequerimiento);

            // Cerrar loading
            Swal.close();

            // Mostrar éxito con temporizador para recargar
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: 'Requerimiento creado y guardado correctamente. La página se recargará en 2 segundos...',
                timer: 2000,
                showConfirmButton: false,
                timerProgressBar: true,
                didClose: () => {
                    // Recargar la página para mostrar el nuevo requerimiento en la lista
                    location.reload();
                }
            });

            // También recargar después del timer por si acaso
            setTimeout(() => {
                location.reload();
            }, 2000);

        } catch (error) {
            console.error('❌ Error creando requerimiento:', error);
            Swal.close();
            mostrarError('Error al crear el requerimiento: ' + error.message);
        }
    }
    // Caso 2: Hay un requerimiento seleccionado del dropdown
    else if (requerimientoSeleccionado) {
        console.log('💾 Guardando requerimiento existente...');
        
        try {
            // Mostrar loading
            Swal.fire({
                title: 'Guardando...',
                text: 'Por favor espere',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            // Simular un pequeño delay para que se vea el loading
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Cerrar loading
            Swal.close();

            // Cerrar modal
            cerrarModalRequerimiento();

            // Mostrar éxito con temporizador para recargar
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: 'Requerimiento guardado correctamente. La página se recargará en 2 segundos...',
                timer: 2000,
                showConfirmButton: false,
                timerProgressBar: true,
                didClose: () => {
                    // Recargar la página para actualizar la lista
                    location.reload();
                }
            });

            // También recargar después del timer por si acaso
            setTimeout(() => {
                location.reload();
            }, 2000);

        } catch (error) {
            console.error('❌ Error guardando requerimiento:', error);
            Swal.close();
            mostrarError('Error al guardar el requerimiento: ' + error.message);
        }
    }
    // Caso 3: No hay nada seleccionado ni escrito
    else {
        Swal.fire({
            icon: 'warning',
            title: 'Requerimiento no configurado',
            text: 'Debe seleccionar un requerimiento existente o crear uno nuevo',
            confirmButtonText: 'Entendido'
        });
        return;
    }
}

// ✅ CARGAR TODOS LOS REQUERIMIENTOS ACTUALIZADO - NUEVO FORMATO TARJETAS
async function cargarTodosLosRequerimientos() {
    try {
        console.log('📥 Cargando todos los requerimientos para lista...');
        const response = await fetch('/api/requerimientos/');
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const todosRequerimientos = await response.json();
        console.log('✅ Todos los requerimientos cargados:', todosRequerimientos);
        
        const lista = document.getElementById('lista-requerimientos');
        if (!lista) {
            console.error('❌ Contenedor lista-requerimientos no encontrado');
            return;
        }
        
        lista.innerHTML = '';
        
        if (todosRequerimientos.length === 0) {
            lista.innerHTML = `
                <div class="sin-requerimientos">
                    <i class="fa-solid fa-inbox"></i>
                    <h4>No hay requerimientos registrados</h4>
                    <p>Utilice el botón "Agregar Nuevo Requerimiento" para crear el primero.</p>
                </div>
            `;
            return;
        }
        
        // Crear contenedor grid para las tarjetas
        const gridContainer = document.createElement('div');
        gridContainer.className = 'lista-requerimientos-grid';
        
        todosRequerimientos.forEach((req, index) => {
            const card = crearTarjetaRequerimiento(req, index);
            gridContainer.appendChild(card);
        });
        
        lista.appendChild(gridContainer);
        
        console.log('✅ Lista de requerimientos renderizada en formato tarjetas');
        
    } catch (error) {
        console.error('❌ Error cargando requerimientos:', error);
        mostrarError('Error cargando la lista de requerimientos: ' + error.message);
    }
}

// Funciones del modal
function abrirModalRequerimiento() {
    document.getElementById('modal-requerimiento').style.display = 'block';
    // Inicializar el estado del botón cuando se abre el modal
    setTimeout(() => {
        habilitarBotonGuardar();
    }, 100);
}

function cerrarModalRequerimiento() {
    document.getElementById('modal-requerimiento').style.display = 'none';
    // Limpiar formulario
    document.getElementById('form-requerimiento').reset();
    // Ocultar todos los inputs nuevos
    document.querySelectorAll('.input-nuevo').forEach(input => {
        input.style.display = 'none';
    });
    // Resetear el botón guardar
    habilitarBotonGuardar();
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

// Función para habilitar el botón de guardar (ACTUALIZADA)
function habilitarBotonGuardar() {
    const requerimientoId = document.getElementById('select-requerimiento').value;
    const inputRequerimientoVisible = document.getElementById('input-requerimiento').style.display !== 'none';
    const nuevoRequerimientoNombre = document.getElementById('nuevo-requerimiento').value.trim();
    const btnGuardar = document.querySelector('.btn-guardar');
    
    if (!btnGuardar) {
        console.error('❌ Botón guardar no encontrado');
        return;
    }
    
    // Habilitar si:
    // - Hay un requerimiento seleccionado O
    // - El input de nuevo requerimiento está visible Y tiene texto
    const puedeGuardar = requerimientoId || (inputRequerimientoVisible && nuevoRequerimientoNombre);
    
    console.log('🔧 Estado botón guardar:', {
        puedeGuardar,
        requerimientoId,
        inputRequerimientoVisible,
        nuevoRequerimientoNombre
    });
    
    if (puedeGuardar) {
        btnGuardar.disabled = false;
        btnGuardar.style.backgroundColor = '#28a745';
        btnGuardar.style.cursor = 'pointer';
    } else {
        btnGuardar.disabled = true;
        btnGuardar.style.backgroundColor = '#6c757d';
        btnGuardar.style.cursor = 'not-allowed';
    }
}

// Función para inicializar event listeners
function inicializarEventListeners() {
    console.log('🔧 Inicializando event listeners...');
    
    // Escuchar cambios en el input de nuevo requerimiento
    const nuevoRequerimientoInput = document.getElementById('nuevo-requerimiento');
    if (nuevoRequerimientoInput) {
        nuevoRequerimientoInput.addEventListener('input', habilitarBotonGuardar);
        console.log('✅ Event listener agregado a nuevo-requerimiento');
    } else {
        console.error('❌ Input nuevo-requerimiento no encontrado');
    }
    
    // Escuchar cambios en el select de requerimiento
    const selectRequerimiento = document.getElementById('select-requerimiento');
    if (selectRequerimiento) {
        selectRequerimiento.addEventListener('change', habilitarBotonGuardar);
        console.log('✅ Event listener agregado a select-requerimiento');
    } else {
        console.error('❌ Select select-requerimiento no encontrado');
    }
    
    // Escuchar cambios en otros selects que afectan el estado
    const selectFamilia = document.getElementById('select-familia');
    if (selectFamilia) {
        selectFamilia.addEventListener('change', habilitarBotonGuardar);
    }
    
    const selectGrupo = document.getElementById('select-grupo');
    if (selectGrupo) {
        selectGrupo.addEventListener('change', habilitarBotonGuardar);
    }
    
    const selectSubgrupo = document.getElementById('select-subgrupo');
    if (selectSubgrupo) {
        selectSubgrupo.addEventListener('change', habilitarBotonGuardar);
    }
    
    // Inicializar el botón guardar
    const btnGuardar = document.querySelector('.btn-guardar');
    if (btnGuardar) {
        btnGuardar.disabled = true;
        btnGuardar.style.backgroundColor = '#6c757d';
        btnGuardar.style.cursor = 'not-allowed';
        console.log('✅ Botón guardar inicializado');
    } else {
        console.error('❌ Botón guardar no encontrado');
    }
}

// ✅ FUNCIÓN PARA CREAR TARJETA DE REQUERIMIENTO - VERSIÓN ACTUALIZADA
function crearTarjetaRequerimiento(requerimiento, index) {
    const card = document.createElement('div');
    card.className = 'requerimiento-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    // ✅ USAR LOS NUEVOS CAMPOS DE JERARQUÍA
    const familia = requerimiento.familia_nombre || 'Sin familia';
    const grupo = requerimiento.grupo_nombre || 'Sin grupo';
    const subgrupo = requerimiento.subgrupo_nombre || 'Sin subgrupo';
    const codigo = requerimiento.codigo_requerimiento || 'N/A';
    const clasificacion = requerimiento.clasificacion_requerimiento || 'Sin clasificación';
    const descripcion = requerimiento.descripcion_requerimiento || '';
    
    card.innerHTML = `
        <div class="requerimiento-header">
            <h3 class="requerimiento-nombre">${requerimiento.nombre_requerimiento}</h3>
            <span class="requerimiento-clasificacion clasificacion-${clasificacion.toLowerCase()}">
                ${clasificacion}
            </span>
        </div>
        <div class="requerimiento-info">
            <div class="requerimiento-dato">
                <strong><i class="fa-solid fa-hashtag"></i> Código:</strong>
                <span class="codigo-requerimiento">${codigo}</span>
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
            ${descripcion ? `
            <div class="requerimiento-dato descripcion">
                <strong><i class="fa-solid fa-file-lines"></i> Descripción:</strong>
                <span class="texto-descripcion">${descripcion}</span>
            </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

// ✅ FUNCIÓN PARA EDITAR DESDE LISTA (compatibilidad)
function editarRequerimientoDesdeLista(idRequerimiento) {
    console.log('✏️ Editando requerimiento desde lista:', idRequerimiento);
    
    // Abrir el modal de actualización si existe la función
    if (typeof abrirModalActualizarRequerimiento === 'function') {
        abrirModalActualizarRequerimiento();
        
        // Buscar y seleccionar automáticamente el requerimiento
        setTimeout(() => {
            const requerimiento = todosRequerimientos.find(req => req.id_requerimiento === idRequerimiento);
            if (requerimiento && typeof seleccionarRequerimientoActualizar === 'function') {
                // Simular la selección en el modal de actualización
                const elemento = document.querySelector(`[data-requerimiento-id="${requerimiento.id_requerimiento}"]`);
                if (elemento) {
                    seleccionarRequerimientoActualizar(requerimiento, elemento);
                }
            }
        }, 500);
    } else {
        console.warn('⚠️ Función abrirModalActualizarRequerimiento no disponible');
    }
}