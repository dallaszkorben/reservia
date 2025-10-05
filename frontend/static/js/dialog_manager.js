// ===== DIALOG MANAGER =====
// Centralized dialog management to eliminate duplicate configuration

class DialogManager {
    static dialogs = {};
    
    static initializeDialog(id, title, width = GUI_CONFIG['dialog-width']) {
        const dialog = $(`#${id}`).dialog({
            autoOpen: false,
            modal: true,
            width: width,
            resizable: false,
            draggable: true,
            title: title
        });
        
        this.dialogs[id] = dialog;
        return dialog;
    }
    
    static showDialog(id) {
        this.closeAllDropdowns();
        const dialog = $(`#${id}`);
        if (dialog.length && dialog.hasClass('ui-dialog-content')) {
            dialog.dialog('open');
        } else {
            console.error(`Dialog ${id} not properly initialized`);
        }
    }
    
    static hideDialog(id) {
        const dialog = $(`#${id}`);
        if (dialog.length && dialog.hasClass('ui-dialog-content')) {
            dialog.dialog('close');
        }
    }
    
    static isAnyDialogOpen() {
        const dialogIds = ['login-form', 'modify-form', 'add-resource-form', 'resource-select-form', 'modify-resource-form', 'add-user-form', 'modify-user-form'];
        return dialogIds.some(id => {
            const dialog = $(`#${id}`);
            return dialog.length && dialog.hasClass('ui-dialog-content') && dialog.dialog('isOpen');
        });
    }
    
    static closeAllDropdowns() {
        $('#resource-dropdown').hide();
        $('#user-dropdown').hide();
    }
    
    static updateButtonStates() {
        if (this.isAnyDialogOpen()) {
            $('#modify-btn, #manage-resource-btn, #manage-user-btn').addClass('dialog-disabled');
        } else {
            $('#modify-btn, #manage-resource-btn, #manage-user-btn').removeClass('dialog-disabled');
        }
    }
}