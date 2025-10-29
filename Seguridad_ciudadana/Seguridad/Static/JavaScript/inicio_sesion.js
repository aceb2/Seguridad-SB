// Funcionalidad de tabs
function showTab(tabName) {
    // Ocultar todos los forms
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
    
    // Mostrar el form seleccionado
    document.getElementById(tabName + '-form').classList.add('active');
    
    // Actualizar tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
    
    // Limpiar mensajes
    hideMessages();
}

// Validación y envío de formularios
document.addEventListener('DOMContentLoaded', function() {
    // Formulario de registro
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmit(this);
    });
    
    // Formulario de login
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmit(this);
    });
});

async function handleFormSubmit(form) {
    const formData = new FormData(form);
    const formType = formData.get('form_type');
    
    // Validaciones específicas
    if (formType === 'register') {
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        
        if (password !== confirmPassword) {
            showError('Las contraseñas no coinciden');
            return;
        }
        
        if (password.length < 6) {
            showError('La contraseña debe tener al menos 6 caracteres');
            return;
        }
    }
    
    // Enviar datos al servidor
    try {
        const response = await fetch(`/auth/${formType}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccess(data.message);
            if (formType === 'login') {
                // Redirigir después de login exitoso
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                // Cambiar a pestaña de login después de registro
                setTimeout(() => {
                    showTab('login');
                    form.reset();
                }, 1500);
            }
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Error de conexión. Intente nuevamente.');
    }
}

// Funciones para mostrar mensajes
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('success-message').style.display = 'none';
    
    setTimeout(hideMessages, 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    document.getElementById('error-message').style.display = 'none';
    
    setTimeout(hideMessages, 5000);
}

function hideMessages() {
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('success-message').style.display = 'none';
}

// Cambio entre formularios con la tecla Tab
document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab' && e.ctrlKey) {
        e.preventDefault();
        const activeTab = document.querySelector('.tab-btn.active');
        const tabs = document.querySelectorAll('.tab-btn');
        const currentIndex = Array.from(tabs).indexOf(activeTab);
        const nextIndex = (currentIndex + 1) % tabs.length;
        
        tabs[nextIndex].click();
    }
});

// Limpiar formularios al cambiar de pestaña
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('form').forEach(form => form.reset());
        hideMessages();
    });
});