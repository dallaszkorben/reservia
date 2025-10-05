// ===== APPLICATION INITIALIZATION =====
// Main application initialization and event binding

class AppInit {
    static initialize() {
        // Initialize jQuery UI elements
        $('button').button();
        
        // Initialize all dialogs
        DialogManager.initializeDialog('login-form', 'Login to Reservia', GUI_CONFIG['login-dialog-width']);
        DialogManager.initializeDialog('modify-form', 'Modify User Data');
        DialogManager.initializeDialog('add-resource-form', 'Add New Resource');
        DialogManager.initializeDialog('resource-select-form', 'Select Resource to Modify');
        DialogManager.initializeDialog('modify-resource-form', 'Modify Resource');
        DialogManager.initializeDialog('add-user-form', 'Add New User');
        DialogManager.initializeDialog('modify-user-form', 'Modify User');
        
        // Setup input clear handlers
        FormManager.setupInputClearHandlers('add-resource', ['resource-name', 'resource-comment']);
        FormManager.setupInputClearHandlers('modify', ['modify-email', 'modify-password']);
        FormManager.setupInputClearHandlers('modify-resource', ['modify-resource-name', 'modify-resource-comment']);
        FormManager.setupInputClearHandlers('add-user', ['user-name', 'user-email', 'user-password']);
        FormManager.setupInputClearHandlers('modify-user', ['modify-user-email', 'modify-user-password']);
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup global AJAX error handler
        AjaxUtils.setupGlobalErrorHandler();
        
        // Initialize ResourcePool and resource manager
        ResourcePool.getInstance();
        initializeResourceManager();
        
        // Initialize auto-hide menu
        MenuManager.initialize();
        
        // Check initial session
        AuthManager.checkSession();
        
        // Start dialog state monitoring
        setInterval(() => DialogManager.updateButtonStates(), GUI_CONFIG['dialog-state-check-interval']);
    }
    
    static setupEventListeners() {
        // Authentication buttons
        $('#login-btn').click(() => AuthManager.showLoginForm());
        $('#logout-btn').click(() => AuthManager.logout());
        $('#login-submit').click(() => AuthManager.login());
        $('#login-cancel').click(() => AuthManager.hideLoginForm());
        
        // User modification
        $('#modify-btn').click(() => {
            if (DialogManager.isAnyDialogOpen()) return;
            AuthManager.showModifyForm();
        });
        $('#modify-submit').click(() => AuthManager.modifyUser());
        $('#modify-cancel').click(() => AuthManager.hideModifyForm());
        
        // Resource management
        $('#add-resource-submit').click(() => ResourceFormManager.addResource());
        $('#add-resource-cancel').click(() => ResourceFormManager.hideAddResourceForm());
        $('#modify-resource-submit').click(() => ResourceFormManager.modifyResource());
        $('#modify-resource-cancel').click(() => ResourceFormManager.hideModifyResourceForm());
        
        // User management
        $('#add-user-submit').click(() => UserManager.addUser());
        $('#add-user-cancel').click(() => UserManager.hideAddUserForm());
        $('#modify-user-submit').click(() => UserManager.modifySelectedUser());
        $('#modify-user-cancel').click(() => UserManager.hideModifyUserForm());
        
        // Dropdown management
        this.setupDropdownListeners();
        
        // Window resize handler
        $(window).resize(() => ResourcePool.getInstance().updateLayout());
    }
    
    static setupDropdownListeners() {
        // Manage Resource dropdown
        $('#manage-resource-btn').click((e) => {
            e.stopPropagation();
            if (DialogManager.isAnyDialogOpen()) return;
            $('#user-dropdown').hide();
            $('#resource-dropdown').toggle();
        });
        
        // Manage User dropdown
        $('#manage-user-btn').click((e) => {
            e.stopPropagation();
            if (DialogManager.isAnyDialogOpen()) return;
            $('#resource-dropdown').hide();
            $('#user-dropdown').toggle();
        });
        
        // Hide dropdowns when clicking outside
        $(document).click(() => {
            $('#resource-dropdown').hide();
            $('#user-dropdown').hide();
        });
        
        // Prevent dropdowns from closing when clicking inside
        $('#resource-dropdown, #user-dropdown').click((e) => e.stopPropagation());
        
        // Hide dropdowns when mouse leaves (but not when going to submenus)
        $('#user-dropdown').mouseleave(() => {
            setTimeout(() => {
                if (!$('#modify-user-submenu:not(.hidden)').length) {
                    $('#user-dropdown').hide();
                }
            }, GUI_CONFIG['submenu-hover-delay']);
        });
        
        $('#resource-dropdown').mouseleave(() => {
            setTimeout(() => {
                if (!$('#modify-submenu:not(.hidden)').length) {
                    $('#resource-dropdown').hide();
                }
            }, GUI_CONFIG['submenu-hover-delay']);
        });
        
        // Resource dropdown actions
        $('#resource-dropdown .dropdown-item').click(function(e) {
            const action = $(this).data('action');
            if (action === 'add') {
                $('#resource-dropdown').hide();
                ResourceFormManager.showAddResourceForm();
            } else if (action === 'remove') {
                $('#resource-dropdown').hide();
                console.log('Remove resource clicked - TODO: Implement');
            }
        });
        
        // User dropdown actions
        $('#user-dropdown .dropdown-item').click(function(e) {
            const action = $(this).data('action');
            if (action === 'add') {
                $('#user-dropdown').hide();
                UserManager.showAddUserForm();
            } else if (action === 'remove') {
                $('#user-dropdown').hide();
                console.log('Remove user clicked - TODO: Implement');
            }
        });
        
        // Setup submenu hover handlers
        this.setupSubmenuHandlers();
    }
    
    static setupSubmenuHandlers() {
        // Resource submenu
        $('#resource-dropdown .dropdown-submenu').mouseenter(() => {
            ResourceFormManager.loadResourcesIntoSubmenu();
            $('#modify-submenu').removeClass('hidden');
        });
        
        $('#resource-dropdown .dropdown-submenu').mouseleave(() => {
            setTimeout(() => {
                if (!$('#modify-submenu:hover').length) {
                    $('#modify-submenu').addClass('hidden');
                }
            }, GUI_CONFIG['submenu-hover-delay']);
        });
        
        $('#modify-submenu').mouseenter(function() { $(this).removeClass('hidden'); });
        $('#modify-submenu').mouseleave(function() { $(this).addClass('hidden'); });
        
        // User submenu
        $('#user-dropdown .dropdown-submenu').mouseenter(() => {
            UserManager.loadUsersIntoSubmenu();
            $('#modify-user-submenu').removeClass('hidden');
        });
        
        $('#user-dropdown .dropdown-submenu').mouseleave(() => {
            setTimeout(() => {
                if (!$('#modify-user-submenu:hover').length) {
                    $('#modify-user-submenu').addClass('hidden');
                }
            }, GUI_CONFIG['submenu-hover-delay']);
        });
        
        $('#modify-user-submenu').mouseenter(function() { $(this).removeClass('hidden'); });
        $('#modify-user-submenu').mouseleave(function() { $(this).addClass('hidden'); });
        
        // Handle clicks in submenus
        $('#modify-submenu').on('click', '.submenu-resource-item', function(e) {
            e.stopPropagation();
            const resourceId = $(this).data('resource-id');
            const resourceName = $(this).data('resource-name');
            const resourceComment = $(this).data('resource-comment');
            
            $('#resource-dropdown').hide();
            $('#modify-submenu').addClass('hidden');
            ResourceFormManager.showModifyResourceForm(resourceId, resourceName, resourceComment);
        });
        
        $('#modify-user-submenu').on('click', '.submenu-user-item', function(e) {
            e.stopPropagation();
            const userId = $(this).data('user-id');
            const userName = $(this).data('user-name');
            const userEmail = $(this).data('user-email');
            
            $('#user-dropdown').hide();
            $('#modify-user-submenu').addClass('hidden');
            UserManager.showModifyUserForm(userId, userName, userEmail);
        });
    }
}

// Initialize application when document is ready
$(document).ready(() => AppInit.initialize());