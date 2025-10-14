// ===========================
// MAIN.JS - Sistema CESFAM
// JavaScript Principal
// ===========================

(function() {
    'use strict';

    // ===========================
    // INICIALIZACIÓN
    // ===========================
    document.addEventListener('DOMContentLoaded', function() {
        initAlerts();
        initTooltips();
        initNavbarMobile();
        initFormSpinner();
        initScrollTop();
        console.log('Sistema CESFAM inicializado correctamente');
    });

    // ===========================
    // AUTO-CERRAR ALERTAS
    // ===========================
    function initAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        
        alerts.forEach(alert => {
            // Auto-cerrar después de 5 segundos
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }, 5000);
            
            // Agregar animación de salida
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    alert.style.animation = 'fadeOut 0.3s ease';
                });
            }
        });
    }

    // ===========================
    // ACTIVAR TOOLTIPS
    // ===========================
    function initTooltips() {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover',
                animation: true
            });
        });
        
        console.log(`${tooltipList.length} tooltips activados`);
    }

    // ===========================
    // NAVBAR MÓVIL
    // ===========================
    function initNavbarMobile() {
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarCollapse) {
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    // Cerrar navbar en móvil después de hacer clic
                    if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                        const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                        if (bsCollapse) {
                            bsCollapse.hide();
                        }
                    }
                });
            });
        }
        
        // Cerrar navbar al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const navbar = document.querySelector('.navbar');
                if (navbar && !navbar.contains(event.target)) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                }
            }
        });
    }

    // ===========================
    // SPINNER EN FORMULARIOS
    // ===========================
    function initFormSpinner() {
        const forms = document.querySelectorAll('form:not(.no-spinner)');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                // Validar que el formulario sea válido antes de mostrar spinner
                if (form.checkValidity()) {
                    toggleSpinner(true);
                    
                    // Deshabilitar botón de submit
                    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitBtn) {
                        submitBtn.disabled = true;
                        submitBtn.classList.add('btn-loading');
                    }
                }
            });
        });
    }

    // ===========================
    // SCROLL TO TOP
    // ===========================
    function initScrollTop() {
        // Crear botón si no existe
        let scrollBtn = document.getElementById('scrollTopBtn');
        
        if (!scrollBtn) {
            scrollBtn = document.createElement('button');
            scrollBtn.id = 'scrollTopBtn';
            scrollBtn.className = 'btn btn-primary rounded-circle position-fixed';
            scrollBtn.style.cssText = 'bottom: 20px; right: 20px; width: 45px; height: 45px; display: none; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.3);';
            scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
            scrollBtn.setAttribute('aria-label', 'Volver arriba');
            document.body.appendChild(scrollBtn);
        }
        
        // Mostrar/ocultar botón según scroll
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollBtn.style.display = 'block';
                scrollBtn.style.animation = 'fadeIn 0.3s ease';
            } else {
                scrollBtn.style.display = 'none';
            }
        });
        
        // Acción al hacer clic
        scrollBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ===========================
    // FUNCIONES AUXILIARES
    // ===========================

    /**
     * Muestra u oculta el spinner de carga
     */
    function toggleSpinner(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.classList.toggle('active', show);
        }
    }

    /**
     * Valida RUT chileno
     */
    function validarRUT(rut) {
        // Limpia el RUT
        rut = rut.replace(/[^0-9kK]/g, '');
        
        if (rut.length < 2) return false;
        
        const cuerpo = rut.slice(0, -1);
        const dv = rut.slice(-1).toUpperCase();
        
        // Calcula el dígito verificador
        let suma = 0;
        let multiplo = 2;
        
        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += parseInt(cuerpo.charAt(i)) * multiplo;
            multiplo = multiplo === 7 ? 2 : multiplo + 1;
        }
        
        const dvEsperado = 11 - (suma % 11);
        let dvCalculado;
        
        if (dvEsperado === 11) dvCalculado = '0';
        else if (dvEsperado === 10) dvCalculado = 'K';
        else dvCalculado = dvEsperado.toString();
        
        return dv === dvCalculado;
    }

    /**
     * Formatea RUT chileno con puntos y guión
     */
    function formatearRUT(rut) {
        // Limpia el RUT
        rut = rut.replace(/[^0-9kK]/g, '');
        
        if (rut.length > 1) {
            const cuerpo = rut.slice(0, -1);
            const dv = rut.slice(-1).toUpperCase();
            
            // Formatea con puntos
            const cuerpoFormateado = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            return `${cuerpoFormateado}-${dv}`;
        }
        
        return rut;
    }

    /**
     * Debounce function para optimizar eventos
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Muestra mensaje de error en input
     */
    function mostrarError(input, mensaje) {
        input.classList.add('is-invalid');
        let feedbackDiv = input.nextElementSibling;
        
        if (!feedbackDiv || !feedbackDiv.classList.contains('invalid-feedback')) {
            feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'invalid-feedback';
            input.parentNode.insertBefore(feedbackDiv, input.nextSibling);
        }
        
        feedbackDiv.textContent = mensaje;
        feedbackDiv.style.display = 'block';
    }

    /**
     * Oculta mensaje de error en input
     */
    function ocultarError(input) {
        input.classList.remove('is-invalid');
        const feedbackDiv = input.nextElementSibling;
        
        if (feedbackDiv && feedbackDiv.classList.contains('invalid-feedback')) {
            feedbackDiv.style.display = 'none';
        }
    }

    /**
     * Valida email
     */
    function validarEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    /**
     * Formatea fecha a formato chileno (DD/MM/YYYY)
     */
    function formatearFecha(fecha) {
        if (!fecha) return '';
        
        const date = new Date(fecha);
        const dia = String(date.getDate()).padStart(2, '0');
        const mes = String(date.getMonth() + 1).padStart(2, '0');
        const anio = date.getFullYear();
        
        return `${dia}/${mes}/${anio}`;
    }

    /**
     * Muestra notificación toast
     */
    function mostrarToast(mensaje, tipo = 'info') {
        // Si existe Bootstrap Toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toastContainer = document.getElementById('toastContainer') || crearToastContainer();
            
            const toastHTML = `
                <div class="toast align-items-center text-white bg-${tipo} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body">
                            ${mensaje}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            `;
            
            toastContainer.insertAdjacentHTML('beforeend', toastHTML);
            const toastElement = toastContainer.lastElementChild;
            const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
            toast.show();
            
            // Eliminar el toast del DOM después de ocultarlo
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        } else {
            // Fallback: usar alert
            alert(mensaje);
        }
    }

    /**
     * Crea contenedor para toasts si no existe
     */
    function crearToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Confirma acción con modal
     */
    function confirmarAccion(mensaje, callback) {
        if (confirm(mensaje)) {
            callback();
        }
    }

    // ===========================
    // EXPORTAR FUNCIONES GLOBALES
    // ===========================
    window.CESFAMUtils = {
        toggleSpinner: toggleSpinner,
        validarRUT: validarRUT,
        formatearRUT: formatearRUT,
        validarEmail: validarEmail,
        formatearFecha: formatearFecha,
        mostrarError: mostrarError,
        ocultarError: ocultarError,
        mostrarToast: mostrarToast,
        confirmarAccion: confirmarAccion,
        debounce: debounce
    };

    // ===========================
    // MANEJO DE VALIDACIÓN RUT
    // ===========================
    document.addEventListener('DOMContentLoaded', function() {
        const rutInputs = document.querySelectorAll('input[name*="rut"], input[data-validate="rut"]');
        
        rutInputs.forEach(input => {
            // Formatear mientras escribe
            input.addEventListener('input', function() {
                this.value = formatearRUT(this.value);
            });
            
            // Validar al salir del campo
            input.addEventListener('blur', function() {
                if (this.value && !validarRUT(this.value)) {
                    mostrarError(this, 'RUT inválido');
                } else {
                    ocultarError(this);
                }
            });
        });
    });

    // ===========================
    // MANEJO DE CONFIRMACIONES
    // ===========================
    document.addEventListener('DOMContentLoaded', function() {
        const confirmButtons = document.querySelectorAll('[data-confirm]');
        
        confirmButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                const mensaje = this.getAttribute('data-confirm') || '¿Estás seguro de realizar esta acción?';
                
                if (!confirm(mensaje)) {
                    event.preventDefault();
                    event.stopPropagation();
                }
            });
        });
    });

    // ===========================
    // LOG DE INICIALIZACIÓN
    // ===========================
    console.log('%c Sistema CESFAM ', 'background: #003366; color: white; font-size: 14px; padding: 5px 10px; border-radius: 3px;');
    console.log('Versión: 1.0.0');
    console.log('Ambiente: Desarrollo');

})();
