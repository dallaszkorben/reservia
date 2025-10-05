// ===== AJAX UTILITIES =====
// Standardized AJAX error handling and utilities

class AjaxUtils {
    static handleError(xhr, defaultMessage = 'Operation failed') {
        try {
            const errorResponse = JSON.parse(xhr.responseText);
            return errorResponse.error || errorResponse.message || defaultMessage;
        } catch (e) {
            return defaultMessage;
        }
    }
    
    static makeRequest(options) {
        return $.ajax({
            contentType: 'application/json',
            ...options,
            error: function(xhr, status, error) {
                const errorMessage = AjaxUtils.handleError(xhr, options.defaultError || 'Request failed');
                if (options.onError) {
                    options.onError(errorMessage, xhr);
                }
            }
        });
    }
    
    static setupGlobalErrorHandler() {
        $(document).ajaxError(function(event, xhr, settings) {
            if (xhr.status === 401 && settings.url !== '/session/status') {
                SessionManager.clearSessionData();
                showLoggedOutUI();
                FormManager.showError('login', 'Session expired. Please log in again.');
            }
        });
    }
}