// ===== GLOBAL SESSION MANAGER =====
// Centralized session data storage and management

/**
 * Global session object to store current user data
 * Accessible from anywhere in the frontend
 */
window.SessionManager = {
    // Session data
    data: {
        logged_in: false,
        user_id: null,
        user_name: null,
        user_email: null,
        is_admin: false
    },

    /**
     * Updates session data from server response
     */
    setSessionData(response) {
        this.data = {
            logged_in: response.logged_in || false,
            user_id: response.user_id || null,
            user_name: response.user_name || null,
            user_email: response.user_email || null,
            is_admin: response.is_admin || false
        };
        this.updateAdminWarning();
    },

    /**
     * Clears session data on logout
     */
    clearSessionData() {
        this.data = {
            logged_in: false,
            user_id: null,
            user_name: null,
            user_email: null,
            is_admin: false
        };
        this.updateAdminWarning();
    },

    /**
     * Quick access methods
     */
    isLoggedIn() {
        return this.data.logged_in;
    },

    getCurrentUserId() {
        return this.data.user_id;
    },

    getCurrentUserName() {
        return this.data.user_name;
    },

    getCurrentUserEmail() {
        return this.data.user_email;
    },

    isAdmin() {
        return this.data.is_admin;
    },

    /**
     * Updates admin warning visual indicator
     */
    updateAdminWarning() {
        const header = document.getElementById('header');
        if (header) {
            if (this.data.logged_in && this.data.is_admin) {
                header.classList.add('admin-warning');
            } else {
                header.classList.remove('admin-warning');
            }
        }
    }
};