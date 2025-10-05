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

// ===== USER MANAGEMENT FUNCTIONS =====

/**
 * Shows the Add User form dialog
 */
function showAddUserForm() {
    // Close all dropdowns when dialog opens
    $('#resource-dropdown').hide();
    $('#user-dropdown').hide();
    clearAddUserMessages();
    $('#user-name').val('');
    $('#user-email').val('');
    $('#user-password').val('');
    $('#add-user-form').dialog('open');
}

/**
 * Hides the Add User form dialog
 */
function hideAddUserForm() {
    $('#add-user-form').dialog('close');
}

/**
 * Clears error and success messages in Add User form
 */
function clearAddUserMessages() {
    $('#add-user-error').hide();
    $('#add-user-success').hide();
}

/**
 * Adds a new user via API call
 */
async function addUser() {
    const name = $('#user-name').val().trim();
    const email = $('#user-email').val().trim();
    const password = $('#user-password').val();

    // Validate required fields
    if (!name) {
        $('#add-user-error').text('User name is required').show();
        return;
    }
    if (!email) {
        $('#add-user-error').text('Email is required').show();
        return;
    }
    if (!password) {
        $('#add-user-error').text('Password is required').show();
        return;
    }

    // Hash the password before sending
    const hashedPassword = await hashPassword(password);

    // Prepare request data
    const requestData = {
        name: name,
        email: email,
        password: hashedPassword
    };

    try {
        // Make API call
        $.ajax({
        url: '/admin/user/add',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
            $('#add-user-success').text('User created successfully!').show();
            $('#add-user-error').hide();
            // Clear form after success
            setTimeout(() => {
                hideAddUserForm();
            }, 1500);
        },
        error: function(xhr) {
            let errorMessage = 'Failed to create user';
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            }
            $('#add-user-error').text(errorMessage).show();
            $('#add-user-success').hide();
        }
    });
    } catch (error) {
        $('#add-user-error').text('Password hashing failed').show();
        $('#add-user-success').hide();
    }
}