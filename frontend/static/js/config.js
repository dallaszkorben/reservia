// ===== GLOBAL CONFIGURATION =====
// Centralized configuration for all GUI dimensions, styling, and behavior

const GUI_CONFIG = {
    // Resource card dimensions (responsive)
    'resource-card-width': window.innerWidth <= 768 ? 180 : 250,
    'resource-card-height': window.innerWidth <= 768 ? 280 : 400,
    'resource-card-list-font-size': window.innerWidth <= 768 ? 12 : 15,
    'resource-card-title-font-size': window.innerWidth <= 768 ? 18 : 25,
    'resource-card-title-length': 25,

    // Layout configuration (responsive)
    'screen-margin': window.innerWidth <= 768 ? 20 : 40,
    'resource-gap': window.innerWidth <= 768 ? 15 : 20,
    'resource-list-side-gap': 6,
    'resource-list-top-gap': window.innerWidth <= 768 ? 40 : 50,
    'layout-top-margin': window.innerWidth <= 768 ? 15 : 20,

    // Timing configuration
    'auto-refresh-interval': 5000,
    'success-message-delay': 1500,
    'submenu-hover-delay': 100,
    'dialog-state-check-interval': 100,

    // Auto-hide menu configuration
    'menu-trigger-distance': 50,
    'menu-animation-duration': 100,

    // Dialog configuration
    'dialog-width': 400,
    'login-dialog-width': 350
};