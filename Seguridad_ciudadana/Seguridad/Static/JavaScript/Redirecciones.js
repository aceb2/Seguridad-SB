// Función para alternar el dropdown
function toggleDropdown() {
  const dropdownMenu = document.getElementById('dropdownMenu');
  dropdownMenu.classList.toggle('show');
}

// Cerrar el dropdown si se hace click fuera de él
document.addEventListener('click', function(event) {
  const dropdown = document.querySelector('.dropdown');
  const dropdownMenu = document.getElementById('dropdownMenu');
  const botonOpciones = document.getElementById('boton-opciones');
  
  // Si el click fue fuera del dropdown y el menú está abierto
  if (!dropdown.contains(event.target) && dropdownMenu.classList.contains('show')) {
    dropdownMenu.classList.remove('show');
  }
  
});

// Cerrar dropdown con la tecla Escape
document.addEventListener('keydown', function(event) {
  if (event.key === 'Escape') {
    const dropdownMenu = document.getElementById('dropdownMenu');
    if (dropdownMenu.classList.contains('show')) {
      dropdownMenu.classList.remove('show');
    }
  }
});