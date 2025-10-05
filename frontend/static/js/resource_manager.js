// ===== RESOURCE MANAGER =====
// Handles loading and refreshing resources and their reservations from the server

/**
 * Loads active reservations for a specific resource from the server
 * and adds them as users to the resource card
 */
function loadUsersForResource(resourceCard) {
    // Fetch active reservations for this resource
    $.ajax({
        url: `/reservation/active?resource_id=${resourceCard.id}`,
        method: 'GET',
        success: function(reservationResponse) {
            // Add each reservation as a user to the resource card
            reservationResponse.reservations.forEach(reservation => {
                resourceCard.addUser(
                    reservation.user_name,
                    reservation.user_id,
                    reservation.status,        // 'approved' or 'requested'
                    reservation.request_date,
                    reservation.approved_date
                );
            });
        },
        error: function(xhr, status, error) {
            console.error(`Failed to load reservations for resource ${resourceCard.id}:`, xhr.status, error);
        }
    });
}

/**
 * Compares two user lists to check if they are identical
 * users1: Current users in ResourceCard (format: {id, status, ...})
 * users2: Users from server response (format: {user_id, status, ...})
 */
function usersEqual(users1, users2) {
    // Quick check: different lengths means different lists
    if (users1.length !== users2.length) return false;

    // Check if every user in list1 has a matching user in list2 (by ID and status)
    return users1.every(u1 =>
        users2.some(u2 => u1.id === u2.user_id && u1.status === u2.status)
    );
}

/**
 * Main refresh function - updates resources and users from server
 * Called every 5 seconds to keep UI synchronized with database
 */
function refreshResourcesFromServer() {
    const pool = ResourcePool.getInstance();

    // Step 1: Get all resources from the server
    $.ajax({
        url: '/info/resources',
        method: 'GET',
        success: function(response) {
            // Step 2: Process each resource from the server
            response.resources.forEach(resource => {
                // Step 3: Check if this resource already exists in our ResourcePool
                let resourceCard = pool.resources.find(r => r.id === resource.id);

                if (!resourceCard) {
                    // Case 1: New resource - add it to the pool and load its users
                    console.log(`Adding new resource: ${resource.name} (${resource.id})`);
                    resourceCard = new ResourceCard(resource.id, resource.name);
                    pool.addResource(resourceCard);
                    loadUsersForResource(resourceCard);
                } else {
                    // Case 2: Existing resource - check if users need updating
                    $.ajax({
                        url: `/reservation/active?resource_id=${resource.id}`,
                        method: 'GET',
                        success: function(reservationResponse) {
                            // Step 4: Compare current users with server users
                            if (!usersEqual(resourceCard.users, reservationResponse.reservations)) {
                                // Case 2.1: Users are different - clear and reload
                                console.log(`Updating users for resource: ${resource.name} (${resource.id})`);
                                resourceCard.users = [];                    // Clear user data
                                resourceCard.view?.user_list.empty();       // Clear DOM elements
                                resourceCard.view?.updateBackgroundColor(); // Update color for empty list

                                // Add updated users from server
                                reservationResponse.reservations.forEach(reservation => {
                                    resourceCard.addUser(
                                        reservation.user_name,
                                        reservation.user_id,
                                        reservation.status,
                                        reservation.request_date,
                                        reservation.approved_date
                                    );
                                });

                                // Update background color after all users are added (or if no users)
                                resourceCard.view?.updateBackgroundColor();
                            }
                            // Case 2.2: Users are the same - do nothing (implicit)
                        }
                    });
                }
            });
            // Step 5: Update the visual layout after all changes
            pool.updateLayout();
        },
        error: function(xhr, status, error) {
            console.error('Failed to load resources:', xhr.status, error);
        }
    });
}

/**
 * Initial load function - clears everything and loads fresh data
 * Used when the page first loads
 */
function loadResourcesFromServer() {
    const pool = ResourcePool.getInstance();
    pool.clear();                    // Remove all existing resources
    refreshResourcesFromServer();    // Load fresh data from server
}

/**
 * Gets the current logged-in user ID from global session data
 * Returns null if no user is logged in
 */
function getCurrentUserId() {
    return SessionManager.getCurrentUserId();
}

/**
 * Sets up production event listener for resource clicks
 * When user clicks on a resource, it attempts to make a reservation
 */
function setupResourceEventListeners() {
    const pool = ResourcePool.getInstance();

    // Listen for resource selection events (when user clicks on empty area of resource card)
    pool.addEventListener('resource_selected', (data) => {
        console.log(`User clicked on resource: ${data.resource_name} (${data.resource_id})`);

        // Step 1: Send POST request to reserve the resource
        $.ajax({
            url: '/reservation/request',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                resource_id: data.resource_id
            }),
            success: function(response) {
                // Step 2: Log successful reservation
                console.log(`Reservation successful for resource ${data.resource_name}:`, response);

                // Step 3: Trigger immediate refresh to show updated state
                console.log('Triggering immediate refresh after reservation...');
                refreshResourcesFromServer();
            },
            error: function(xhr, status, error) {
                // Step 2: Log reservation errors to console
                //console.error(`Reservation failed for resource ${data.resource_name} (${data.resource_id}):`);
                //console.error('Status:', xhr.status);
                //console.error('Error:', error);

                //// Try to parse and log the error response
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    //console.error('Server response:', errorResponse);
                    console.log('Reservation was not successful:', errorResponse);
                } catch (e) {
                    console.error('Raw response:', xhr.responseText);
                }
            }
        });
    });

    // Listen for user selection events (when user clicks on a user in the list)
    pool.addEventListener('user_selected', (data) => {
        console.log(`User clicked on user: ${data.user_name} (${data.user_id}) in resource: ${data.resource_name} (${data.resource_id})`);

        // Step 1: Get current logged-in user ID
        const currentUserId = getCurrentUserId();
        if (!currentUserId) {
            console.error('No user logged in - cannot perform user operations');
            return;
        }

        // Step 2: Check if clicked user matches current logged-in user
        if (data.user_id !== currentUserId) {
            console.log(`Clicked user (${data.user_id}) is not the current user (${currentUserId}) - ignoring click`);
            return;
        }

        // Step 3: Find the resource and user to determine the action
        const resource = pool.resources.find(r => r.id === data.resource_id);
        if (!resource) {
            console.error(`Resource ${data.resource_id} not found`);
            return;
        }

        const user = resource.users.find(u => u.id === data.user_id);
        if (!user) {
            console.error(`User ${data.user_id} not found in resource ${data.resource_id}`);
            return;
        }

        // Step 4: Determine action based on user status
        let endpoint, action;
        if (user.status === 'approved') {
            // User has approved reservation - release it
            endpoint = '/reservation/release';
            action = 'release';
        } else {
            // User has requested reservation (or other status) - cancel it
            endpoint = '/reservation/cancel';
            action = 'cancel';
        }

        console.log(`Attempting to ${action} reservation for user ${data.user_name} (${data.user_id}) on resource ${data.resource_name} (${data.resource_id})`);

        // Step 5: Send the appropriate API request
        $.ajax({
            url: endpoint,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                resource_id: data.resource_id
            }),
            success: function(response) {
                // Step 6: Log successful operation
                console.log(`${action.toUpperCase()} successful for user ${data.user_name} on resource ${data.resource_name}:`, response);

                // Step 7: Trigger immediate refresh to show updated state
                console.log(`Triggering immediate refresh after ${action}...`);
                refreshResourcesFromServer();
            },
            error: function(xhr, status, error) {
                // Step 6: Log operation errors to console
                console.error(`${action.toUpperCase()} failed for user ${data.user_name} (${data.user_id}) on resource ${data.resource_name} (${data.resource_id}):`);
                console.error('Status:', xhr.status);
                console.error('Error:', error);

                // Try to parse and log the error response
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    console.error('Server response:', errorResponse);
                } catch (e) {
                    console.error('Raw response:', xhr.responseText);
                }
            }
        });
    });
}

// Global variable to store the auto-refresh interval ID
let autoRefreshInterval = null;

/**
 * Starts the auto-refresh system for logged-in users
 * Called when user successfully logs in
 */
function startAutoRefresh() {
    // Clear any existing interval to prevent duplicates
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }

    // Start auto-refresh system: Update resources every 5 seconds
    autoRefreshInterval = setInterval(refreshResourcesFromServer, 5000);
    console.log('Auto-refresh started for logged-in user');
}

/**
 * Stops the auto-refresh system for logged-out users
 * Called when user logs out
 */
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh stopped for logged-out user');
    }
}

/**
 * Clears all resources when user logs out
 * Called when user logs out to hide all ResourceCards
 */
function clearResourcesOnLogout() {
    const pool = ResourcePool.getInstance();
    pool.clear();
    // Update layout to maintain proper container height even with 0 resources
    pool.updateLayout();
    console.log('All resources cleared on logout');
}

/**
 * Initializes the resource management system
 * Should be called after the page is ready and ResourcePool is initialized
 */
function initializeResourceManager() {
    // Set up event listeners for resource and user interactions
    setupResourceEventListeners();

    console.log('Resource manager initialized with login-controlled auto-refresh and user click handling');
}