// ===== AUTHENTICATION MANAGER =====
// Login/logout and session management functions

class AuthManager {
    static checkSession() {
        AjaxUtils.makeRequest({
            url: '/session/status',
            method: 'GET',
            success: function(response) {
                if (response.logged_in) {
                    AuthManager.showLoggedInUI(response);
                } else {
                    AuthManager.showLoggedOutUI();
                }
            },
            error: function() {
                AuthManager.showLoggedOutUI();
            }
        });
    }
    
    static showLoginForm() {
        DialogManager.showDialog('login-form');
        FormManager.clearForm('login', ['username', 'password']);
    }
    
    static hideLoginForm() {
        DialogManager.hideDialog('login-form');
    }
    
    static async login() {
        const username = $('#username').val();
        const password = $('#password').val();
        
        if (!username || !password) {
            FormManager.showError('login', 'Please enter username and password');
            return;
        }
        
        try {
            const hashedPassword = await hashPassword(password);
            
            AjaxUtils.makeRequest({
                url: '/session/login',
                method: 'POST',
                data: JSON.stringify({name: username, password: hashedPassword}),
                success: function(response) {
                    AuthManager.hideLoginForm();
                    AuthManager.checkSession();
                },
                onError: function() {
                    FormManager.showError('login', 'Login failed');
                }
            });
        } catch (error) {
            FormManager.showError('login', 'Password hashing failed');
        }
    }
    
    static logout() {
        AjaxUtils.makeRequest({
            url: '/session/logout',
            method: 'POST',
            success: function() {
                AuthManager.showLoggedOutUI();
            },
            error: function() {
                AuthManager.showLoggedOutUI();
            }
        });
    }
    
    static showLoggedInUI(response) {
        SessionManager.setSessionData(response);
        
        $('#login-btn').addClass('hidden');
        $('#logout-btn').removeClass('hidden');
        $('#modify-btn').removeClass('hidden');
        
        if (response.is_admin) {
            $('#manage-resource-container').removeClass('hidden');
            $('#manage-user-container').removeClass('hidden');
        } else {
            $('#manage-resource-container').addClass('hidden');
            $('#manage-user-container').addClass('hidden');
        }
        
        const tooltipContent = `<b>${response.user_name}</b><br>user_id: ${response.user_id}<br>user_email: ${response.user_email}<br>is_admin: ${response.is_admin}`;
        $('#logout-btn').attr('title', tooltipContent).tooltip({
            content: tooltipContent,
            position: { my: "left top+15", at: "left bottom" }
        });
        
        loadResourcesFromServer();
        startRefreshTimers();
    }
    
    static showLoggedOutUI() {
        SessionManager.clearSessionData();
        
        $('#login-btn').removeClass('hidden');
        $('#logout-btn').addClass('hidden');
        $('#modify-btn').addClass('hidden');
        $('#manage-resource-container').addClass('hidden');
        $('#manage-user-container').addClass('hidden');
        
        if ($('#logout-btn').data('ui-tooltip')) {
            $('#logout-btn').tooltip('destroy');
        }
        
        // Hide all dialogs
        Object.keys(DialogManager.dialogs).forEach(id => {
            DialogManager.hideDialog(id);
        });
        
        stopRefreshTimers();
        clearResourcesOnLogout();
    }
    
    static showModifyForm() {
        DialogManager.showDialog('modify-form');
        const userName = SessionManager.getCurrentUserName();
        const title = userName ? `Modify ${userName} Data` : 'Modify User Data';
        $('#modify-title').text(title);
        FormManager.clearForm('modify', ['modify-email', 'modify-password']);
    }
    
    static hideModifyForm() {
        DialogManager.hideDialog('modify-form');
    }
    
    static async modifyUser() {
        const email = $('#modify-email').val();
        const password = $('#modify-password').val();
        
        if (!email && !password) {
            FormManager.showError('modify', 'Please enter at least one field to modify');
            return;
        }
        
        const currentUserId = SessionManager.getCurrentUserId();
        if (!currentUserId) {
            FormManager.showError('modify', 'Unable to get current user ID');
            return;
        }
        
        try {
            const data = { user_id: currentUserId };
            if (email) data.email = email;
            if (password) data.password = await hashPassword(password);
            
            AjaxUtils.makeRequest({
                url: '/admin/user/modify',
                method: 'POST',
                data: JSON.stringify(data),
                success: function(response) {
                    FormManager.showSuccess('modify', 'User data modified successfully');
                    setTimeout(() => {
                        AuthManager.checkSession();
                        AuthManager.hideModifyForm();
                    }, GUI_CONFIG['success-message-delay']);
                },
                onError: function(errorMessage) {
                    FormManager.showError('modify', errorMessage);
                }
            });
        } catch (error) {
            FormManager.showError('modify', 'Password hashing failed');
        }
    }
}