// ===========================
// HOME.JS - Página de Inicio
// JavaScript específico para el dashboard principal
// ===========================

(function() {
    'use strict';

    // ===========================
    // INICIALIZACIÓN
    // ===========================
    document.addEventListener('DOMContentLoaded', function() {
        initActionCards();
        initQuickActions();
        initHeroAnimations();
        initInteractiveElements();
        console.log('Home page inicializada correctamente');
    });

    // ===========================
    // ANIMACIÓN DE CARDS AL SCROLL
    // ===========================
    function initActionCards() {
        const cards = document.querySelectorAll('.action-card');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in-up');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            cards.forEach(card => {
                observer.observe(card);
            });
        }

        // Agregar efecto de click con feedback visual
        cards.forEach(card => {
            card.addEventListener('click', function(e) {
                // Crear efecto ripple
                createRippleEffect(e, this);
            });
        });
    }

    // ===========================
    // EFECTO RIPPLE EN CARDS
    // ===========================
    function createRippleEffect(event, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple-effect');

        // Agregar estilos del ripple si no existen
        if (!document.getElementById('ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                .ripple-effect {
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.6);
                    transform: scale(0);
                    animation: ripple-animation 0.6s ease-out;
                    pointer-events: none;
                    z-index: 10;
                }
                @keyframes ripple-animation {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // ===========================
    // ACCESOS RÁPIDOS
    // ===========================
    function initQuickActions() {
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        
        quickActionBtns.forEach(btn => {
            // Agregar contador de clics (opcional)
            btn.addEventListener('click', function(e) {
                // Efecto de click
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });

            // Tooltip personalizado al hover
            btn.addEventListener('mouseenter', function() {
                const text = this.querySelector('span').textContent;
                showCustomTooltip(this, text);
            });

            btn.addEventListener('mouseleave', function() {
                hideCustomTooltip();
            });
        });
    }

    // ===========================
    // TOOLTIP PERSONALIZADO
    // ===========================
    let tooltipElement = null;

    function showCustomTooltip(element, text) {
        // Crear tooltip si no existe
        if (!tooltipElement) {
            tooltipElement = document.createElement('div');
            tooltipElement.className = 'custom-tooltip';
            tooltipElement.style.cssText = `
                position: fixed;
                background: rgba(0, 51, 102, 0.95);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-size: 0.875rem;
                pointer-events: none;
                z-index: 10000;
                opacity: 0;
                transition: opacity 0.2s ease;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(tooltipElement);
        }

        tooltipElement.textContent = text;
        
        // Posicionar tooltip
        const rect = element.getBoundingClientRect();
        tooltipElement.style.left = rect.left + (rect.width / 2) - (tooltipElement.offsetWidth / 2) + 'px';
        tooltipElement.style.top = rect.top - tooltipElement.offsetHeight - 10 + 'px';
        
        setTimeout(() => {
            tooltipElement.style.opacity = '1';
        }, 10);
    }

    function hideCustomTooltip() {
        if (tooltipElement) {
            tooltipElement.style.opacity = '0';
        }
    }

    // ===========================
    // ANIMACIONES DEL HERO
    // ===========================
    function initHeroAnimations() {
        const heroIcon = document.querySelector('.hero-icon');
        const roleBadge = document.querySelector('.role-badge');

        // Animación de entrada del icono
        if (heroIcon) {
            setTimeout(() => {
                heroIcon.style.animation = 'bounceIn 0.6s ease-out';
            }, 300);
        }

        // Animación de entrada del badge
        if (roleBadge) {
            setTimeout(() => {
                roleBadge.style.animation = 'slideInRight 0.5s ease-out';
            }, 500);
        }

        // Agregar estilos de animación si no existen
        if (!document.getElementById('hero-animations')) {
            const style = document.createElement('style');
            style.id = 'hero-animations';
            style.textContent = `
                @keyframes bounceIn {
                    0% {
                        opacity: 0;
                        transform: scale(0.3) rotate(-10deg);
                    }
                    50% {
                        transform: scale(1.05) rotate(5deg);
                    }
                    70% {
                        transform: scale(0.9) rotate(-2deg);
                    }
                    100% {
                        opacity: 1;
                        transform: scale(1) rotate(0deg);
                    }
                }
                @keyframes slideInRight {
                    from {
                        opacity: 0;
                        transform: translateX(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // ===========================
    // ELEMENTOS INTERACTIVOS
    // ===========================
    function initInteractiveElements() {
        // Agregar efecto parallax suave al hero
        const heroWelcome = document.querySelector('.hero-welcome');
        
        if (heroWelcome && window.innerWidth > 768) {
            window.addEventListener('scroll', function() {
                const scrolled = window.pageYOffset;
                const rate = scrolled * 0.3;
                heroWelcome.style.transform = `translateY(${rate}px)`;
            });
        }

        // Contador animado para estadísticas (si existen)
        initCounters();

        // Info box interactiva
        const infoBox = document.querySelector('.info-box');
        if (infoBox) {
            infoBox.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.02)';
                this.style.transition = 'transform 0.3s ease';
            });
            
            infoBox.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        }

        // Efecto shimmer en badge destacado
        const featuredBadges = document.querySelectorAll('.badge-featured');
        featuredBadges.forEach(badge => {
            badge.classList.add('shimmer');
        });
    }

    // ===========================
    // CONTADOR ANIMADO
    // ===========================
    function initCounters() {
        const counters = document.querySelectorAll('[data-counter]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-counter'));
            const duration = 2000; // 2 segundos
            const increment = target / (duration / 16); // 60fps
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.textContent = Math.ceil(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };

            // Iniciar contador cuando sea visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        updateCounter();
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(counter);
        });
    }

    // ===========================
    // SHORTCUTS DE TECLADO
    // ===========================
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K para buscar (ejemplo)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchBtn = document.querySelector('a[href*="listar_ninos"]');
            if (searchBtn) {
                searchBtn.click();
            }
        }

        // Números 1-6 para accesos rápidos
        if (e.key >= '1' && e.key <= '6' && !e.ctrlKey && !e.altKey) {
            const quickActions = document.querySelectorAll('.quick-action-btn');
            const index = parseInt(e.key) - 1;
            if (quickActions[index]) {
                e.preventDefault();
                quickActions[index].click();
            }
        }
    });

    // ===========================
    // MODO OSCURO (OPCIONAL)
    // ===========================
    function initDarkMode() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        
        if (darkModeToggle) {
            // Verificar preferencia guardada
            const isDarkMode = localStorage.getItem('darkMode') === 'true';
            
            if (isDarkMode) {
                document.body.classList.add('dark-mode');
            }

            darkModeToggle.addEventListener('click', function() {
                document.body.classList.toggle('dark-mode');
                const isNowDark = document.body.classList.contains('dark-mode');
                localStorage.setItem('darkMode', isNowDark);
                
                // Feedback visual
                CESFAMUtils.mostrarToast(
                    isNowDark ? 'Modo oscuro activado' : 'Modo claro activado',
                    'info'
                );
            });
        }
    }

    // ===========================
    // ESTADÍSTICAS EN TIEMPO REAL
    // ===========================
    function updateLiveStats() {
        // Esta función puede conectarse a un endpoint para obtener estadísticas
        // Por ahora es un placeholder para futura implementación
        
        const statsElements = document.querySelectorAll('[data-stat-live]');
        
        if (statsElements.length > 0) {
            // Simulación de actualización cada 30 segundos
            setInterval(() => {
                statsElements.forEach(el => {
                    const statType = el.getAttribute('data-stat-live');
                    // Aquí iría una llamada fetch/ajax real
                    // fetch(`/api/stats/${statType}/`)...
                });
            }, 30000);
        }
    }

    // ===========================
    // GESTOS TÁCTILES (MOBILE)
    // ===========================
    function initTouchGestures() {
        if ('ontouchstart' in window) {
            const cards = document.querySelectorAll('.action-card');
            
            cards.forEach(card => {
                let touchStartX = 0;
                let touchEndX = 0;

                card.addEventListener('touchstart', (e) => {
                    touchStartX = e.changedTouches[0].screenX;
                }, { passive: true });

                card.addEventListener('touchend', (e) => {
                    touchEndX = e.changedTouches[0].screenX;
                    handleSwipe();
                }, { passive: true });

                function handleSwipe() {
                    const swipeThreshold = 50;
                    const diff = touchStartX - touchEndX;

                    if (Math.abs(diff) > swipeThreshold) {
                        // Swipe detectado
                        card.style.transform = 'scale(0.98)';
                        setTimeout(() => {
                            card.style.transform = '';
                        }, 200);
                    }
                }
            });
        }
    }

    // ===========================
    // PRELOAD DE PÁGINAS (PREFETCH)
    // ===========================
    function initPagePrefetch() {
        const links = document.querySelectorAll('.action-link');
        
        links.forEach(link => {
            link.addEventListener('mouseenter', function() {
                const href = this.getAttribute('href');
                if (href && href.startsWith('/')) {
                    // Crear link prefetch
                    const prefetchLink = document.createElement('link');
                    prefetchLink.rel = 'prefetch';
                    prefetchLink.href = href;
                    document.head.appendChild(prefetchLink);
                }
            }, { once: true });
        });
    }

    // ===========================
    // PERFORMANCE MONITORING
    // ===========================
    function monitorPerformance() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                    
                    console.log(`Tiempo de carga de home: ${loadTime}ms`);
                    
                    // Si el tiempo de carga es muy alto, mostrar advertencia
                    if (loadTime > 3000) {
                        console.warn('Tiempo de carga alto detectado');
                    }
                }, 0);
            });
        }
    }

    // ===========================
    // BÚSQUEDA RÁPIDA
    // ===========================
    function initQuickSearch() {
        // Agregar un pequeño buscador flotante (opcional)
        const quickSearchInput = document.getElementById('quickSearch');
        
        if (quickSearchInput) {
            quickSearchInput.addEventListener('input', CESFAMUtils.debounce(function() {
                const query = this.value.toLowerCase();
                const cards = document.querySelectorAll('.action-card');
                
                cards.forEach(card => {
                    const title = card.querySelector('h5').textContent.toLowerCase();
                    const description = card.querySelector('p').textContent.toLowerCase();
                    
                    if (title.includes(query) || description.includes(query)) {
                        card.parentElement.style.display = '';
                    } else {
                        card.parentElement.style.display = 'none';
                    }
                });
            }, 300));
        }
    }

    // ===========================
    // EXPORTAR FUNCIONES
    // ===========================
    window.HomeUtils = {
        createRippleEffect: createRippleEffect,
        showCustomTooltip: showCustomTooltip,
        hideCustomTooltip: hideCustomTooltip
    };

    // ===========================
    // INICIALIZAR FUNCIONES OPCIONALES
    // ===========================
    initTouchGestures();
    initPagePrefetch();
    monitorPerformance();
    initQuickSearch();
    // initDarkMode(); // Descomentar si quieres modo oscuro

    // ===========================
    // LOG DE INICIALIZACIÓN
    // ===========================
    console.log('%c Home Dashboard Cargado ', 'background: #003366; color: white; font-size: 12px; padding: 4px 8px; border-radius: 3px;');
    console.log('Shortcuts disponibles:');
    console.log('  Ctrl/Cmd + K: Buscar niños');
    console.log('  1-6: Accesos rápidos');

})();
