// ===== RESOURCE FORM MANAGER =====
// Resource management form functions

class ResourceFormManager {
    static showAddResourceForm() {
        DialogManager.showDialog('add-resource-form');
        FormManager.clearForm('add-resource', ['resource-name', 'resource-comment']);
    }
    
    static hideAddResourceForm() {
        DialogManager.hideDialog('add-resource-form');
    }
    
    static addResource() {
        const name = $('#resource-name').val().trim();
        const comment = $('#resource-comment').val().trim();
        
        if (!name) {
            FormManager.showError('add-resource', 'Resource name is required');
            return;
        }
        
        if (name.length > GUI_CONFIG['resource-card-title-length']) {
            FormManager.showError('add-resource', `Resource name must be ${GUI_CONFIG['resource-card-title-length']} characters or less`);
            return;
        }
        
        const data = { name: name };
        if (comment) data.comment = comment;
        
        AjaxUtils.makeRequest({
            url: '/admin/resource/add',
            method: 'POST',
            data: JSON.stringify(data),
            success: function(response) {
                FormManager.showSuccess('add-resource', 'Resource added successfully');
                setTimeout(() => {
                    loadResourcesFromServer();
                    ResourceFormManager.hideAddResourceForm();
                }, GUI_CONFIG['success-message-delay']);
            },
            onError: function(errorMessage) {
                FormManager.showError('add-resource', errorMessage);
            }
        });
    }
    
    static showModifyResourceForm(resourceId, name, comment) {
        DialogManager.showDialog('modify-resource-form');
        $('#modify-resource-title').text(`Modify Resource: ${name}`);
        $('#modify-resource-name').val(name);
        $('#modify-resource-comment').val(comment || '');
        $('#modify-resource-form').data('resource-id', resourceId);
        FormManager.clearMessages('modify-resource');
    }
    
    static hideModifyResourceForm() {
        DialogManager.hideDialog('modify-resource-form');
    }
    
    static modifyResource() {
        const resourceId = $('#modify-resource-form').data('resource-id');
        const name = $('#modify-resource-name').val().trim();
        const comment = $('#modify-resource-comment').val().trim();
        
        if (!name) {
            FormManager.showError('modify-resource', 'Resource name is required');
            return;
        }
        
        if (name.length > GUI_CONFIG['resource-card-title-length']) {
            FormManager.showError('modify-resource', `Resource name must be ${GUI_CONFIG['resource-card-title-length']} characters or less`);
            return;
        }
        
        const data = {
            resource_id: resourceId,
            name: name,
            comment: comment
        };
        
        AjaxUtils.makeRequest({
            url: '/admin/resource/modify',
            method: 'POST',
            data: JSON.stringify(data),
            success: function(response) {
                FormManager.showSuccess('modify-resource', 'Resource modified successfully');
                setTimeout(() => location.reload(), GUI_CONFIG['success-message-delay']);
            },
            onError: function(errorMessage) {
                FormManager.showError('modify-resource', errorMessage);
            }
        });
    }
    
    static loadResourcesIntoSubmenu() {
        AjaxUtils.makeRequest({
            url: '/info/resources',
            method: 'GET',
            success: function(response) {
                const submenu = $('#modify-submenu');
                submenu.empty();
                
                if (response.resources && response.resources.length > 0) {
                    response.resources.forEach(resource => {
                        const item = $('<div></div>')
                            .addClass('submenu-resource-item')
                            .attr('data-resource-id', resource.id)
                            .attr('data-resource-name', resource.name)
                            .attr('data-resource-comment', resource.comment || '')
                            .text(resource.name);
                        submenu.append(item);
                    });
                } else {
                    submenu.append('<div style="padding: 8px 12px; color: #999;">No resources available</div>');
                }
            },
            onError: function() {
                const submenu = $('#modify-submenu');
                submenu.empty();
                submenu.append('<div style="padding: 8px 12px; color: #f00;">Failed to load resources</div>');
            }
        });
    }
}