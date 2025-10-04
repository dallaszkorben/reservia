// ===== FRONTEND TEST FUNCTIONS =====

// Test function to populate ResourceCards with sample data for visual testing
function testLookOfTheResourceElements() {
    const pool = ResourcePool.getInstance('center');

    for (let i = 1; i <= 15; i++) {
        const resource_card = new ResourceCard(i, `Resource${i}`, 20);
        pool.addResource(resource_card);

        for (let j = 1; j < i; j++) {
            const currentDate = new Date().toISOString();
            resource_card.addUser(j.toString(), j, 'approved', currentDate, currentDate);
        }
    }

    pool.updateLayout();
}

// Interactive test function for simulating user operations (add, release, cancel reservations)
function testSimulateUserOperations() {
    const pool = ResourcePool.getInstance('center');

    // Create user input container
    const userContainer = $('<div></div>').css({
        'margin-top': '20px',
        'text-align': 'center'
    });

    const userLabel = $('<span>User: </span>');
    const userInput = $('<input type="number" id="current-user" value="1" min="1">');

    userContainer.append(userLabel).append(userInput);
    $('#resource-pool-container').after(userContainer);

    // Register event listeners
    pool.addEventListener('user_selected', (data) => {
        const currentUserId = parseInt($('#current-user').val());
        if (data.user_id === currentUserId) {
            const resource = pool.resources.find(r => r.id === data.resource_id);
            const isFirstUser = resource.users[0]?.id === currentUserId;

            resource.removeUser(currentUserId);

            if (isFirstUser) {
                console.log(`RELEASED - Resource: ${data.resource_name} (${data.resource_id}), User: ${data.user_name} (${currentUserId})`);
            } else {
                console.log(`CANCELLED - Resource: ${data.resource_name} (${data.resource_id}), User: ${data.user_name} (${currentUserId})`);
            }
        }
    });

    pool.addEventListener('resource_selected', (data) => {
        const currentUserId = parseInt($('#current-user').val());
        const resource = pool.resources.find(r => r.id === data.resource_id);
        const userExists = resource.users.some(u => u.id === currentUserId);

        if (!userExists) {
            const currentDate = new Date().toISOString();
            resource.addUser(currentUserId.toString(), currentUserId, 'approved', currentDate, currentDate);
            console.log(`ADDED - Resource: ${data.resource_name} (${data.resource_id}), User: ${currentUserId} (${currentUserId})`);
        }
    });

    // Create empty ResourceCards for user simulation
    for (let i = 1; i <= 3; i++) {
        const resource_card = new ResourceCard(i, `Resource${i}`, 20);
        pool.addResource(resource_card);
    }

    pool.updateLayout();
}