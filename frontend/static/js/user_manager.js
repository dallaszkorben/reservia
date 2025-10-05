// ===== USER MANAGER =====
// User management functions separated from session manager

class UserManager {
    static showAddUserForm() {
        DialogManager.showDialog('add-user-form');
        FormManager.clearForm('add-user', ['user-name', 'user-email', 'user-password']);
    }
    
    static hideAddUserForm() {
        DialogManager.hideDialog('add-user-form');
    }
    
    static async addUser() {
        const name = $('#user-name').val().trim();
        const email = $('#user-email').val().trim();
        const password = $('#user-password').val();
        
        if (!name) {
            FormManager.showError('add-user', 'User name is required');
            return;
        }
        if (!email) {
            FormManager.showError('add-user', 'Email is required');
            return;
        }
        if (!password) {
            FormManager.showError('add-user', 'Password is required');
            return;
        }
        
        try {
            const hashedPassword = await hashPassword(password);
            
            AjaxUtils.makeRequest({
                url: '/admin/user/add',
                method: 'POST',
                data: JSON.stringify({
                    name: name,
                    email: email,
                    password: hashedPassword
                }),
                success: function(response) {
                    FormManager.showSuccess('add-user', 'User created successfully!');
                    setTimeout(() => UserManager.hideAddUserForm(), GUI_CONFIG['success-message-delay']);
                },
                onError: function(errorMessage) {
                    FormManager.showError('add-user', errorMessage);
                }
            });
        } catch (error) {
            FormManager.showError('add-user', 'Password hashing failed');
        }
    }
    
    static showModifyUserForm(userId, userName, userEmail) {
        DialogManager.showDialog('modify-user-form');
        $('#modify-user-title').text(`Modify User: ${userName}`);
        $('#modify-user-email').val(userEmail);
        $('#modify-user-password').val('');
        $('#modify-user-form').data('user-id', userId);
        FormManager.clearMessages('modify-user');
    }
    
    static hideModifyUserForm() {
        DialogManager.hideDialog('modify-user-form');
    }
    
    static async modifySelectedUser() {
        const userId = $('#modify-user-form').data('user-id');
        const email = $('#modify-user-email').val().trim();
        const password = $('#modify-user-password').val();
        
        if (!email) {
            FormManager.showError('modify-user', 'Email is required');
            return;
        }
        
        try {
            const data = { user_id: userId, email: email };
            if (password) {
                data.password = await hashPassword(password);
            }
            
            AjaxUtils.makeRequest({
                url: '/admin/user/modify',
                method: 'POST',
                data: JSON.stringify(data),
                success: function(response) {
                    FormManager.showSuccess('modify-user', 'User modified successfully');
                    setTimeout(() => UserManager.hideModifyUserForm(), GUI_CONFIG['success-message-delay']);
                },
                onError: function(errorMessage) {
                    FormManager.showError('modify-user', errorMessage);
                }
            });
        } catch (error) {
            FormManager.showError('modify-user', 'Password hashing failed');
        }
    }
    
    static loadUsersIntoSubmenu() {
        AjaxUtils.makeRequest({
            url: '/info/users',
            method: 'GET',
            success: function(response) {
                const submenu = $('#modify-user-submenu');
                submenu.empty();
                
                if (response.users && response.users.length > 0) {
                    response.users.forEach(user => {
                        const item = $('<div></div>')
                            .addClass('submenu-user-item')
                            .attr('data-user-id', user.id)
                            .attr('data-user-name', user.name)
                            .attr('data-user-email', user.email)
                            .text(user.name);
                        submenu.append(item);
                    });
                } else {
                    submenu.append('<div style="padding: 8px 12px; color: #999;">No users available</div>');
                }
            },
            onError: function() {
                const submenu = $('#modify-user-submenu');
                submenu.empty();
                submenu.append('<div style="padding: 8px 12px; color: #f00;">Failed to load users</div>');
            }
        });
    }
}