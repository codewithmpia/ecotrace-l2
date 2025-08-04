/**
 * EcoTrace - Scripts globaux
 */

// ============================================================================
// LOADER DE PAGE
// ============================================================================
window.addEventListener('load', function() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
        }, 500);
    }
});

// ============================================================================
// INITIALISATION AU CHARGEMENT DU DOM
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================================================
    // NAVIGATION MOBILE
    // ========================================================================
    initMobileNavigation();
    
    // ========================================================================
    // FLASH MESSAGES AUTO-HIDE
    // ========================================================================
    initFlashMessages();
    
    // ========================================================================
    // SMOOTH SCROLLING POUR LES LIENS D'ANCRAGE
    // ========================================================================
    initSmoothScrolling();
    
    // ========================================================================
    // LAZY LOADING POUR LES IMAGES
    // ========================================================================
    initLazyLoading();
});

// ============================================================================
// BOUTON RETOUR EN HAUT
// ============================================================================
window.addEventListener('scroll', function() {
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        if (window.pageYOffset > 300) {
            backToTop.style.opacity = '1';
            backToTop.style.pointerEvents = 'all';
        } else {
            backToTop.style.opacity = '0';
            backToTop.style.pointerEvents = 'none';
        }
    }
});

// Click sur le bouton retour en haut
document.addEventListener('DOMContentLoaded', function() {
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        backToTop.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});

// ============================================================================
// FONCTIONS D'INITIALISATION
// ============================================================================

/**
 * Initialise la navigation mobile
 */
function initMobileNavigation() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');
    const closeIcon = document.getElementById('close-icon');
    
    // Vérifier que tous les éléments existent
    if (!mobileMenuButton || !mobileMenu || !menuIcon || !closeIcon) {
        console.warn('Navigation mobile: Certains éléments sont manquants');
        return;
    }
    
    /**
     * Basculer l'état du menu mobile
     */
    function toggleMobileMenu() {
        const isHidden = mobileMenu.classList.contains('hidden');
        
        if (isHidden) {
            // Ouvrir le menu
            mobileMenu.classList.remove('hidden');
            menuIcon.classList.add('hidden');
            closeIcon.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Empêcher le scroll
        } else {
            // Fermer le menu
            closeMobileMenu();
        }
    }
    
    /**
     * Fermer le menu mobile
     */
    function closeMobileMenu() {
        mobileMenu.classList.add('hidden');
        menuIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
        document.body.style.overflow = ''; // Restaurer le scroll
    }
    
    // Event listeners
    mobileMenuButton.addEventListener('click', toggleMobileMenu);
    
    // Fermer le menu en cliquant sur les liens
    mobileMenu.querySelectorAll('a, button[type="submit"]').forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    // Fermer le menu en cliquant à l'extérieur
    document.addEventListener('click', function(event) {
        if (!mobileMenu.contains(event.target) && !mobileMenuButton.contains(event.target)) {
            closeMobileMenu();
        }
    });
    
    // Fermer le menu avec la touche Échap
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeMobileMenu();
        }
    });
    
    // Fermer le menu lors du redimensionnement vers desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 1024) { // lg breakpoint de Tailwind
            closeMobileMenu();
        }
    });
}

/**
 * Initialise les messages flash avec auto-hide et bouton de fermeture
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Supprimer tout bouton existant pour éviter les doublons
        const existingButtons = message.querySelectorAll('button');
        existingButtons.forEach(btn => btn.remove());
        
        // Créer le bouton de fermeture
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'ml-3 text-gray-400 hover:text-gray-600 focus:outline-none transition-colors duration-200 flex-shrink-0';
        closeButton.innerHTML = '<svg fill="currentColor" class="w-4 h-4" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 0 1 1.414 0L10 8.586l4.293-4.293a1 1 0 1 1 1.414 1.414L11.414 10l4.293 4.293a1 1 0 0 1-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 0 1-1.414-1.414L8.586 10 4.293 5.707a1 1 0 0 1 0-1.414z" clip-rule="evenodd"/></svg>';
        closeButton.addEventListener('click', () => removeFlashMessage(message));
        
        // Trouver le conteneur flex et ajouter le bouton
        const flexContainer = message.querySelector('.flex');
        if (flexContainer) {
            flexContainer.appendChild(closeButton);
        } else {
            // Si pas de conteneur flex, en créer un
            const content = message.innerHTML;
            message.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex items-center flex-1">
                        ${content}
                    </div>
                </div>
            `;
            message.querySelector('.flex').appendChild(closeButton);
        }
        
        // Auto-hide après 5 secondes
        setTimeout(() => {
            removeFlashMessage(message);
        }, 5000);
    });
}

/**
 * Supprime un message flash avec animation
 */
function removeFlashMessage(message) {
    if (message && message.parentNode) {
        message.style.opacity = '0';
        message.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 300);
    }
}

/**
 * Initialise le smooth scrolling pour les liens d'ancrage
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Ignorer les liens vides ou juste "#"
            if (href === '#' || href === '') {
                return;
            }
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                const offsetTop = target.offsetTop - 80; // Offset pour la navbar sticky
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Initialise le lazy loading pour les images
 */
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Charger l'image
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        
                        // Optionnel: ajouter une classe quand l'image est chargée
                        img.addEventListener('load', function() {
                            img.classList.add('loaded');
                        });
                        
                        imageObserver.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px 0px', // Commencer à charger 50px avant que l'image ne soit visible
            threshold: 0.01
        });
        
        // Observer toutes les images avec data-src
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback pour les navigateurs sans IntersectionObserver
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
}

// ============================================================================
// UTILITAIRES GLOBAUX
// ============================================================================

/**
 * Débounce function pour optimiser les événements fréquents
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        
        if (callNow) func.apply(context, args);
    };
}

/**
 * Afficher un message toast (optionnel - si vous utilisez un système de toast)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    const bgColor = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-yellow-500',
        'info': 'bg-blue-500'
    };
    
    toast.className = `${bgColor[type] || bgColor.info} text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Animation d'entrée
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-remove
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }, duration);
}

// ============================================================================
// EXPOSITION DES FONCTIONS GLOBALES
// ============================================================================
window.EcoTrace = {
    showToast,
    debounce,
    removeFlashMessage
};