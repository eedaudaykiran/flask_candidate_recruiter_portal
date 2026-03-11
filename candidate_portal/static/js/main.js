// Main JavaScript File for Animations and Interactions

document.addEventListener('DOMContentLoaded', function () {

    // Initialize all animations
    initAnimations();

    // Initialize form validations
    initFormValidation();

    // Initialize smooth scrolling
    initSmoothScroll();

    // Initialize hover effects
    initHoverEffects();

    // Initialize loading states
    initLoadingStates();

    // Initialize mobile menu
    initMobileMenu();
});

function initAnimations() {
    // Add animation classes to elements
    const animatedElements = document.querySelectorAll('.card, .btn, .stat-card');

    animatedElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
        element.classList.add('fade-in');
    });

    // Observe elements for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function () {
                validateInput(this);
            });

            input.addEventListener('input', function () {
                if (this.classList.contains('error')) {
                    validateInput(this);
                }
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required]');

    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });

    return isValid;
}

function validateInput(input) {
    const value = input.value.trim();
    let isValid = true;
    let errorMessage = '';

    if (!value) {
        isValid = false;
        errorMessage = 'This field is required';
    } else if (input.type === 'email' && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
    } else if (input.type === 'password' && value.length < 6) {
        isValid = false;
        errorMessage = 'Password must be at least 6 characters';
    }

    if (!isValid) {
        showError(input, errorMessage);
    } else {
        removeError(input);
    }

    return isValid;
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(input, message) {
    input.classList.add('error');

    let errorDiv = input.nextElementSibling;
    if (!errorDiv || !errorDiv.classList.contains('error-message')) {
        errorDiv = document.createElement('div');
        errorDiv.classList.add('error-message');
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
    }

    errorDiv.textContent = message;
    errorDiv.style.animation = 'slideInRight 0.3s ease';
}

function removeError(input) {
    input.classList.remove('error');

    const errorDiv = input.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains('error-message')) {
        errorDiv.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            errorDiv.remove();
        }, 300);
    }
}

function initSmoothScroll() {
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

function initHoverEffects() {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-10px)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });

    // 3D tilt effect on cards
    const tiltCards = document.querySelectorAll('.tilt-effect');

    tiltCards.forEach(card => {
        card.addEventListener('mousemove', function (e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });
    });
}

function initLoadingStates() {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (this.classList.contains('loading-btn')) {
                e.preventDefault();

                const originalText = this.textContent;
                this.innerHTML = '<span class="loading"></span> Loading...';
                this.disabled = true;

                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 2000);
            }
        });
    });
}

function initMobileMenu() {
    const menuButton = document.createElement('button');
    menuButton.classList.add('mobile-menu-btn');
    menuButton.innerHTML = '☰';

    const nav = document.querySelector('.nav-container');
    const navLinks = document.querySelector('.nav-links');

    if (window.innerWidth <= 768 && nav && navLinks) {
        nav.insertBefore(menuButton, navLinks);

        menuButton.addEventListener('click', function () {
            navLinks.classList.toggle('show');
            this.innerHTML = navLinks.classList.contains('show') ? '✕' : '☰';
        });
    }

    // Handle resize
    window.addEventListener('resize', function () {
        if (window.innerWidth <= 768) {
            if (!document.querySelector('.mobile-menu-btn')) {
                initMobileMenu();
            }
        } else {
            const menuBtn = document.querySelector('.mobile-menu-btn');
            if (menuBtn) {
                menuBtn.remove();
            }
            if (navLinks) {
                navLinks.classList.remove('show');
            }
        }
    });
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(20px); }
    }
    
    .error {
        border-color: var(--danger-color) !important;
        animation: shake 0.5s ease;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    .error-message {
        color: var(--danger-color);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        padding-left: 0.5rem;
    }
    
    .fade-in {
        animation: fadeIn 0.8s ease forwards;
        opacity: 0;
    }
    
    .in-view {
        animation: scaleIn 0.6s ease forwards;
    }
    
    .mobile-menu-btn {
        display: none;
        background: none;
        border: none;
        font-size: 2rem;
        cursor: pointer;
        color: var(--primary-color);
        transition: var(--transition);
    }
    
    .mobile-menu-btn:hover {
        transform: scale(1.1);
    }
    
    @media (max-width: 768px) {
        .mobile-menu-btn {
            display: block;
            position: absolute;
            right: 1rem;
            top: 1rem;
        }
        
        .nav-links {
            display: none;
            width: 100%;
            padding: 1rem 0;
        }
        
        .nav-links.show {
            display: flex;
            flex-direction: column;
            animation: slideInDown 0.5s ease;
        }
    }
`;

document.head.appendChild(style);