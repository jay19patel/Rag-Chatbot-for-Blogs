// Main JavaScript file for the application
console.log('Main JavaScript file loaded');
// CSRF Token Management
function readCookie(name) {
    const nameEQ = name + "=";
    const parts = document.cookie.split(';');
    for (let i = 0; i < parts.length; i++) {
        let c = parts[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

async function getCsrfToken() {
    console.log('Getting CSRF token');
    const storedSignedToken = localStorage.getItem("csrf_token");
    const csrfCookie = readCookie("csrf_token");

    // If we have both a signed token and the raw cookie, reuse the signed token
    if (storedSignedToken && csrfCookie) {
        return storedSignedToken;
    }

    // Otherwise, fetch a fresh token/cookie pair
    try {
        const response = await fetch('/api/auth/csrf-token', {
            credentials: "include"
        });
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("csrf_token", data.csrf_token);
            return data.csrf_token;
        }
    } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
    }
    return null;
}

// Ensure CSRF token is available
async function ensureCsrfToken() {
    return await getCsrfToken();
}

// Wrapper around fetch to automatically include CSRF token and credentials
async function csrfFetch(url, options = {}) {
    const opts = { ...options };
    // Always include credentials so cookies are sent
    if (!opts.credentials) {
        opts.credentials = 'include';
    }
    // For unsafe methods, attach the CSRF header
    const method = (opts.method || 'GET').toUpperCase();
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
        const csrfToken = await getCsrfToken();
        opts.headers = { ...(opts.headers || {}) };
        if (csrfToken) {
            opts.headers['X-CSRF-Token'] = csrfToken;
        }
        // Default content-type for JSON if body is an object and header not set
        if (opts.body && !(opts.body instanceof FormData) && !opts.headers['Content-Type']) {
            opts.headers['Content-Type'] = 'application/json';
        }
    }
    return fetch(url, opts);
}

// Toast Notification System
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = toast.querySelector('svg');
    const toastBorder = toast.querySelector('div');

    toastMessage.textContent = message;

    if (type === 'error') {
        toastBorder.className = 'bg-white border-l-4 border-red-500 rounded-lg shadow-lg p-4 max-w-md';
        toastIcon.className = 'h-5 w-5 text-red-500';
    } else {
        toastBorder.className = 'bg-white border-l-4 border-green-500 rounded-lg shadow-lg p-4 max-w-md';
        toastIcon.className = 'h-5 w-5 text-green-500';
    }

    toast.classList.remove('hidden');
    setTimeout(hideToast, 5000);
}

function hideToast() {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.classList.add('hidden');
    }
}

// Logout Function
async function logout() {
    try {
        const response = await csrfFetch('/api/auth/logout', {
            method: 'POST'
        });

        if (response.ok) {
            localStorage.removeItem("csrf_token");
            window.location.href = '/login';
        } else {
            const data = await response.json();
            showToast(data.detail || 'Logout failed', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showToast('Logout failed', 'error');
    }
}

// Mobile Menu Toggle
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

// Form Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

function validateUsername(username) {
    const re = /^[a-zA-Z0-9_-]{3,100}$/;
    return re.test(username);
}

// Smooth Scrolling
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animation on Scroll
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Initialize all functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initSmoothScrolling();
    initScrollAnimations();
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize CSRF token if user is logged in
    const userElement = document.querySelector('[data-user]');
    if (userElement) {
        console.log('Initializing CSRF token');
        getCsrfToken();
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// Handle form submissions with loading states
function handleFormSubmission(formId, submitCallback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Loading...';
        
        try {
            await submitCallback(form);
        } catch (error) {
            console.error('Form submission error:', error);
            showToast('An error occurred. Please try again.', 'error');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Export functions for use in other scripts
window.AppUtils = {
    getCsrfToken,
    ensureCsrfToken,
    csrfFetch,
    showToast,
    hideToast,
    logout,
    validateEmail,
    validatePassword,
    validateUsername,
    handleFormSubmission
};
