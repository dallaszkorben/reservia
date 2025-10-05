// ===== AUTO-HIDE MENU MANAGER =====
// Manages the auto-hiding menu that appears when cursor approaches top of screen

class MenuManager {
    static isMenuVisible = false;
    static hideTimeout = null;
    
    static initialize() {
        // Set up mouse move listener
        $(document).mousemove(this.handleMouseMove.bind(this));
        
        // Set up menu hover listeners to keep it visible
        $('#header').mouseenter(() => {
            this.showMenu();
            this.clearHideTimeout();
        });
        
        $('#header').mouseleave(() => {
            this.scheduleHide();
        });
    }
    
    static handleMouseMove(event) {
        const mouseY = event.clientY;
        const triggerDistance = GUI_CONFIG['menu-trigger-distance'];
        
        if (mouseY <= triggerDistance && !this.isMenuVisible) {
            this.showMenu();
        } else if (mouseY > triggerDistance && this.isMenuVisible && !this.isHoveringMenuArea()) {
            this.scheduleHide();
        }
    }
    
    static showMenu() {
        if (!this.isMenuVisible) {
            $('#header').addClass('visible');
            this.isMenuVisible = true;
            this.clearHideTimeout();
        }
    }
    
    static hideMenu() {
        if (this.isMenuVisible) {
            $('#header').removeClass('visible');
            this.isMenuVisible = false;
        }
    }
    
    static scheduleHide() {
        this.clearHideTimeout();
        this.hideTimeout = setTimeout(() => {
            if (!this.isHoveringMenuArea()) {
                this.hideMenu();
            }
        }, 1000); // Hide after 1 second delay
    }
    
    static clearHideTimeout() {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }
    }
    
    static isHoveringMenuArea() {
        return $('#header:hover').length > 0 || 
               $('#resource-dropdown:visible').length > 0 || 
               $('#user-dropdown:visible').length > 0 ||
               $('#modify-submenu:not(.hidden)').length > 0 ||
               $('#modify-user-submenu:not(.hidden)').length > 0;
    }
}