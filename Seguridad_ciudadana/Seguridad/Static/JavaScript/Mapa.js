document.addEventListener("DOMContentLoaded", function () {
    // Inicializar mapa centrado en San Bernardo
    var map = L.map('map').setView([-33.593, -70.698], 11);

    // Cargar tiles de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    // Función para cargar y mostrar rutas
    function cargarRutas() {
        fetch('/rutas/json/')  // Necesitarás crear esta vista
            .then(response => response.json())
            .then(rutas => {
                // Limpiar rutas existentes
                map.eachLayer(layer => {
                    if (layer instanceof L.Routing.Control) {
                        map.removeLayer(layer);
                    }
                });

                // Dibujar cada ruta
                rutas.forEach(ruta => {
                    if (ruta.coordenadas && ruta.coordenadas.length >= 2) {
                        const waypoints = ruta.coordenadas.map(coord => 
                            L.latLng(coord.lat, coord.lng)
                        );

                        L.Routing.control({
                            waypoints: waypoints,
                            routeWhileDragging: false,
                            language: 'es',
                            showAlternatives: false,
                            lineOptions: {
                                styles: [
                                    {color: 'blue', opacity: 0.6, weight: 5}
                                ]
                            },
                            createMarker: function(i, waypoint, n) {
                                if (i === 0) {
                                    return L.marker(waypoint.latLng, {
                                        icon: L.icon({
                                            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                                            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                                            iconSize: [25, 41],
                                            iconAnchor: [12, 41],
                                            popupAnchor: [1, -34],
                                            shadowSize: [41, 41]
                                        })
                                    }).bindPopup(`Inicio: ${ruta.nombre}`);
                                } else if (i === n - 1) {
                                    return L.marker(waypoint.latLng, {
                                        icon: L.icon({
                                            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                                            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                                            iconSize: [25, 41],
                                            iconAnchor: [12, 41],
                                            popupAnchor: [1, -34],
                                            shadowSize: [41, 41]
                                        })
                                    }).bindPopup(`Fin: ${ruta.nombre}`);
                                }
                            }
                        }).addTo(map);
                    }
                });
            })
            .catch(error => console.error('Error cargando rutas:', error));
    }

    // Cargar rutas al iniciar
    cargarRutas();

    // Opcional: Botón para agregar nueva ruta
    document.getElementById('agregar-ruta-btn').addEventListener('click', function() {
        // Aquí puedes abrir un modal o formulario para agregar rutas
        agregarNuevaRuta();
    });
});

// Función para agregar nueva ruta (ejemplo)
function agregarNuevaRuta() {
    const nombre = prompt('Nombre de la ruta:');
    const vehiculo = prompt('Vehículo:');
    const latInicio = parseFloat(prompt('Latitud inicio:'));
    const lngInicio = parseFloat(prompt('Longitud inicio:'));
    const latFin = parseFloat(prompt('Latitud fin:'));
    const lngFin = parseFloat(prompt('Longitud fin:'));

    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('vehiculo', vehiculo);
    formData.append('lat_inicio', latInicio);
    formData.append('lng_inicio', lngInicio);
    formData.append('lat_fin', latFin);
    formData.append('lng_fin', lngFin);

    fetch('/agregar-ruta/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Ruta agregada correctamente');
            location.reload(); // Recargar para ver la nueva ruta
        } else {
            alert('Error: ' + data.message);
        }
    });
}