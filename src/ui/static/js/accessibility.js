/* Accessibility JavaScript */

// Keyboard navigation support
document.addEventListener('keydown', (e) => {
    // Alt + H for home
    if (e.altKey && e.key === 'h') {
        window.location.hash = '#plan';
    }
    // Alt + A for about
    if (e.altKey && e.key === 'a') {
        window.location.hash = '#about';
    }
});

// Focus management
function manageFocus(element) {
    if (element) {
        element.focus();
        // Announce to screen readers
        announceToScreenReader(`Navigated to ${element.textContent}`);
    }
}

// Screen reader announcements
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    setTimeout(() => announcement.remove(), 1000);
}

// Form validation feedback
document.querySelectorAll('input, select, textarea').forEach((field) => {
    field.addEventListener('invalid', (e) => {
        e.preventDefault();
        const errorId = `${field.id}-error`;
        let errorElement = document.getElementById(errorId);

        if (!errorElement) {
            errorElement = document.createElement('span');
            errorElement.id = errorId;
            errorElement.className = 'error-message';
            errorElement.setAttribute('role', 'alert');
            field.parentNode.appendChild(errorElement);
        }

        errorElement.textContent = field.validationMessage;
        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-describedby', errorId);
    });

    field.addEventListener('valid', () => {
        field.removeAttribute('aria-invalid');
        const errorId = `${field.id}-error`;
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.remove();
        }
    });
});

// Button state announcements
document.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => {
        const originalText = button.textContent;
        button.setAttribute('aria-busy', 'true');
        setTimeout(() => {
            button.setAttribute('aria-busy', 'false');
        }, 2000);
    });
});

// Hidden content for screen readers
const srOnly = document.createElement('style');
srOnly.textContent = `
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }
`;
document.head.appendChild(srOnly);

// Ensure proper heading hierarchy
function checkHeadingHierarchy() {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let prevLevel = 0;

    headings.forEach((heading) => {
        const level = parseInt(heading.tagName[1]);
        if (level - prevLevel > 1) {
            console.warn(`Heading hierarchy skipped: ${heading.textContent}`);
        }
        prevLevel = level;
    });
}

document.addEventListener('DOMContentLoaded', checkHeadingHierarchy);

// Color contrast checker
function checkColorContrast() {
    // This is a simple check - in production use axe-core or similar
    const elements = document.querySelectorAll('*');
    let contrastIssues = 0;

    elements.forEach((el) => {
        const computed = window.getComputedStyle(el);
        const bgColor = computed.backgroundColor;
        const fgColor = computed.color;

        // Simple contrast ratio calculation (simplified)
        if (bgColor && fgColor && bgColor !== 'rgba(0, 0, 0, 0)') {
            // Contrast check would go here
        }
    });

    if (contrastIssues > 0) {
        console.warn(`Found ${contrastIssues} potential contrast issues`);
    }
}

// Initialize accessibility features
document.addEventListener('DOMContentLoaded', () => {
    checkColorContrast();
    announceToScreenReader('Page loaded. Ready to plan your travel itinerary.');
});

// Language support
function setLanguage(lang) {
    document.documentElement.lang = lang;
    localStorage.setItem('preferredLanguage', lang);
}

// Get preferred language
const preferredLanguage = localStorage.getItem('preferredLanguage') || navigator.language.split('-')[0];
setLanguage(preferredLanguage);
