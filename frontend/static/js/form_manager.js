// ===== FORM MANAGER =====
// Generic form handling to eliminate repetitive form functions

class FormManager {
    static clearMessages(formId) {
        $(`#${formId}-error`).hide();
        $(`#${formId}-success`).hide();
    }
    
    static showError(formId, message) {
        $(`#${formId}-error`).text(message).show();
        $(`#${formId}-success`).hide();
    }
    
    static showSuccess(formId, message) {
        $(`#${formId}-success`).text(message).show();
        $(`#${formId}-error`).hide();
    }
    
    static clearForm(formId, fields) {
        fields.forEach(field => $(`#${field}`).val(''));
        this.clearMessages(formId);
    }
    
    static setupInputClearHandlers(formId, fields) {
        fields.forEach(field => {
            $(`#${field}`).on('input', () => this.clearMessages(formId));
        });
    }
}