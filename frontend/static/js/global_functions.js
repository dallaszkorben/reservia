// ===== GLOBAL FUNCTIONS =====
// Functions that need to be globally accessible for backward compatibility

// Authentication functions (delegated to AuthManager)
function checkSession() { AuthManager.checkSession(); }
function showLoggedInUI(response) { AuthManager.showLoggedInUI(response); }
function showLoggedOutUI() { AuthManager.showLoggedOutUI(); }
function login() { AuthManager.login(); }
function logout() { AuthManager.logout(); }

// User management functions (delegated to UserManager)
function showAddUserForm() { UserManager.showAddUserForm(); }
function hideAddUserForm() { UserManager.hideAddUserForm(); }
function addUser() { UserManager.addUser(); }

// Resource management functions (delegated to ResourceFormManager)
function showAddResourceForm() { ResourceFormManager.showAddResourceForm(); }
function hideAddResourceForm() { ResourceFormManager.hideAddResourceForm(); }
function addResource() { ResourceFormManager.addResource(); }

// Form utility functions (delegated to FormManager)
function clearAddUserMessages() { FormManager.clearMessages('add-user'); }
function clearAddResourceMessages() { FormManager.clearMessages('add-resource'); }
function clearModifyMessages() { FormManager.clearMessages('modify'); }
function clearModifyResourceMessages() { FormManager.clearMessages('modify-resource'); }
function clearModifyUserMessages() { FormManager.clearMessages('modify-user'); }