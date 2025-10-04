// ===== RESOURCE MANAGER =====

function loadResourcesFromServer() {
    const pool = ResourcePool.getInstance();
    
    $.ajax({
        url: '/admin/resources',
        method: 'GET',
        success: function(response) {
            console.log('Resources loaded:', response.count);
            
            // Clear existing resources
            pool.clear();
            
            // Add each resource to the pool
            response.resources.forEach(resource => {
                const resourceCard = new ResourceCard(resource.id, resource.name);
                pool.addResource(resourceCard);
            });
            
            // Update layout after adding all resources
            pool.updateLayout();
        },
        error: function(xhr, status, error) {
            console.error('Failed to load resources:', xhr.status, error);
            if (xhr.status === 403) {
                console.error('Admin access required to load resources');
            }
        }
    });
}