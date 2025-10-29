// ===== RESOURCE MANAGER =====
// Handles loading and refreshing resources and their reservations from the server

/**
 * Loads active reservations for a specific resource from the server
 * and adds them as users to the resource card
 */
function loadUsersForResource(resourceCard) {
    // Fetch all active reservations and filter for this resource
    $.ajax({
        url: '/reservation/active/all_users',
        method: 'GET',
        success: function(reservationResponse) {
            // Filter reservations for this specific resource
            const resourceReservations = reservationResponse.reservations.filter(
                reservation => reservation.resource_id === resourceCard.id
            );
            
            // Add each reservation as a user to the resource card
            resourceReservations.forEach(reservation => {
                resourceCard.addUser(
                    reservation.user_name,
                    reservation.user_id,
                    reservation.status,        // 'approved' or 'requested'
                    reservation.request_date,
                    reservation.approved_date,
                    reservation.valid_until_date
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
 * users1: Current users in ResourceCard (format: {id, status, valid_until_date, ...})
 * users2: Users from server response (format: {user_id, status, valid_until_date, ...})
 */
function usersEqual(users1, users2) {
    // Quick check: different lengths means different lists
    if (users1.length !== users2.length) return false;

    // Check if every user in list1 has a matching user in list2 (by ID, status, and valid_until_date)
    return users1.every(u1 =>
        users2.some(u2 => u1.id === u2.user_id && u1.status === u2.status && u1.valid_until_date === u2.valid_until_date)
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
                        url: '/reservation/active/all_users',
                        method: 'GET',
                        success: function(reservationResponse) {
                            // Filter reservations for this specific resource
                            const resourceReservations = reservationResponse.reservations.filter(
                                reservation => reservation.resource_id === resource.id
                            );
                            
                            // Step 4: Compare current users with server users
                            if (!usersEqual(resourceCard.users, resourceReservations)) {
                                // Case 2.1: Users are different - clear and reload
                                console.log(`Updating users for resource: ${resource.name} (${resource.id})`);
                                resourceCard.users = [];                    // Clear user data
                                resourceCard.view?.user_list.empty();       // Clear DOM elements
                                resourceCard.view?.updateBackgroundColor(); // Update color for empty list

                                // Add updated users from server
                                resourceReservations.forEach(reservation => {
                                    resourceCard.addUser(
                                        reservation.user_name,
                                        reservation.user_id,
                                        reservation.status,
                                        reservation.request_date,
                                        reservation.approved_date,
                                        reservation.valid_until_date
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
                // Log reservation errors
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    console.log('Reservation was not successful:', errorResponse);
                } catch (e) {
                    console.error('Raw response:', xhr.responseText);
                }
            }
        });
    });



    // Listen for user action events (from hover buttons)
    pool.addEventListener('user_action', (data) => {
        console.log(`User action: ${data.action} for user ${data.user_name} (${data.user_id}) on resource ${data.resource_name} (${data.resource_id})`);

        // Map actions to endpoints
        const actionMap = {
            'release': '/reservation/release',
            'cancel': '/reservation/cancel',
            'keep_alive': '/reservation/keep_alive'
        };

        const endpoint = actionMap[data.action];
        if (!endpoint) {
            console.error(`Unknown action: ${data.action}`);
            return;
        }

        // Send API request
        $.ajax({
            url: endpoint,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                resource_id: data.resource_id
            }),
            success: function(response) {
                console.log(`${data.action.toUpperCase()} successful:`, response);
                refreshResourcesFromServer();
            },
            error: function(xhr, status, error) {
                console.error(`${data.action.toUpperCase()} failed:`, xhr.status, error);
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

// Global variables for auto-refresh system
let autoRefreshInterval = null;
let timeUpdateInterval = null;

/**
 * Updates only the remaining time displays for approved reservations
 * Called every second to refresh countdown timers
 */
function updateRemainingTimesOnly() {
    const pool = ResourcePool.getInstance();
    pool.resources.forEach(resourceCard => {
        resourceCard.view?.updateRemainingTimes();
    });
}

/**
 * Starts both server refresh and time update intervals for logged-in users
 * Called when user successfully logs in
 */
function startRefreshTimers() {
    // Clear any existing intervals to prevent duplicates
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
    }

    // Start 5-second server refresh (from config)
    autoRefreshInterval = setInterval(refreshResourcesFromServer, GUI_CONFIG['auto-refresh-interval']);
    console.log('Auto-refresh started for logged-in user (5 second interval)');

    // Start 1-second time update (hardcoded)
    timeUpdateInterval = setInterval(updateRemainingTimesOnly, 1000);
    console.log('Time update started for logged-in user (1 second interval)');
}

/**
 * Stops both server refresh and time update intervals for logged-out users
 * Called when user logs out
 */
function stopRefreshTimers() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh stopped for logged-out user');
    }
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
        timeUpdateInterval = null;
        console.log('Time update stopped for logged-out user');
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