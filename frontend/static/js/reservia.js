// GUI_CONFIG is now imported from config.js

// ===== LAYOUT MANAGER =====
// Static utility class that calculates responsive grid positioning for resource cards
// Handles automatic layout calculation based on screen width and resource count
class LayoutManager {
    /**
     * Calculates how many resource cards fit per row and total rows needed
     * This enables responsive design that adapts to different screen sizes
     * @param {number} resource_count - Total number of resources to display
     * @param {object} config - Configuration object with dimensions
     * @returns {object} Layout information (rectangles_per_row, total_rows, screen_width, resource_count)
     */
    static calculateLayout(resource_count, config) {
        const screen_width = $(window).width() - GUI_CONFIG['screen-margin'];
        const rectangle_with_gap = config.resource_width + config.resource_gap;
        const rectangles_per_row = Math.floor(screen_width / rectangle_with_gap);
        const total_rows = Math.max(1, Math.ceil(resource_count / rectangles_per_row));

        return { rectangles_per_row, total_rows, screen_width, resource_count };
    }

    /**
     * Calculates exact pixel position for a resource card based on its index
     * Supports different alignment options (center, left, right)
     * @param {number} index - Zero-based index of the resource card
     * @param {object} layout - Layout information from calculateLayout()
     * @param {object} config - Configuration object with dimensions
     * @param {string} alignment - How to align the grid ('center', 'left', 'right')
     * @returns {object} Position coordinates {x, y} in pixels
     */
    static getPosition(index, layout, config, alignment = 'center') {
        const row = Math.floor(index / layout.rectangles_per_row);  // Which row this card is in
        const col = index % layout.rectangles_per_row;              // Which column this card is in

        // Calculate how many cards are in the current row (last row might be partial)
        const rectangles_in_current_row = Math.min(layout.rectangles_per_row, layout.resource_count - (row * layout.rectangles_per_row));
        const total_row_width = (rectangles_in_current_row * config.resource_width) + ((rectangles_in_current_row - 1) * config.resource_gap);

        // Calculate starting X position based on alignment preference
        let start_x;
        if (alignment === 'center') {
            start_x = (layout.screen_width - total_row_width) / 2;  // Center the row
        } else if (alignment === 'right') {
            start_x = layout.screen_width - total_row_width;        // Right-align the row
        } else { // 'left'
            start_x = 0;                                            // Left-align the row
        }

        const x_position = start_x + (col * (config.resource_width + config.resource_gap));
        const y_position = (row * (config.resource_height + config.resource_gap)) + GUI_CONFIG['layout-top-margin'];

        return { x: x_position, y: y_position };
    }
}

// ===== RESOURCE POOL SINGLETON =====
// Manages the collection of all resource cards and their layout
// Uses singleton pattern to ensure only one instance exists across the application
class ResourcePool {
    static instance = null;

    /**
     * Private constructor - use getInstance() instead
     * Initializes the resource pool with DOM container and event system
     * @param {string} alignment - How to align the resource grid ('center', 'left', 'right')
     */
    constructor(alignment = 'center') {
        if (ResourcePool.instance) {
            return ResourcePool.instance;  // Return existing instance (singleton pattern)
        }
        this.container = $('#resource-pool-container');  // Main DOM container for all resources
        this.resources = [];                             // Array of ResourceCard objects
        this.listeners = {};                             // Event listeners for custom events
        this.alignment = alignment;                      // Grid alignment preference
        ResourcePool.instance = this;

        // Set initial minimum height
        this.updateLayout();
    }

    /**
     * Gets the singleton instance, creating it if it doesn't exist
     * This ensures only one ResourcePool exists in the entire application
     * @param {string} alignment - Grid alignment preference
     * @returns {ResourcePool} The singleton instance
     */
    static getInstance(alignment = 'center') {
        if (!ResourcePool.instance) {
            ResourcePool.instance = new ResourcePool(alignment);
        } else if (alignment !== 'center') {
            ResourcePool.instance.alignment = alignment;  // Update alignment if different
        }
        return ResourcePool.instance;
    }

    /**
     * Adds a new resource card to the pool and creates its visual representation
     * Links the data model (ResourceCard) with its view (ResourceView)
     * @param {ResourceCard} resource_card - The resource data model to add
     */
    addResource(resource_card) {
        this.resources.push(resource_card);
        const view = new ResourceView(resource_card, this.container, this);  // Create DOM representation
        resource_card.setView(view);  // Link model to view for two-way communication
    }

    /**
     * Removes all resources from the pool and cleans up their DOM elements
     * Used when logging out or refreshing the resource list
     */
    clear() {
        this.resources.forEach(resource_card => resource_card.view?.destroy());  // Clean up DOM
        this.container.empty();  // Remove all child elements from container
        this.resources = [];     // Clear the array
    }

    /**
     * Recalculates and updates the position of all resource cards
     * Called when window is resized or resources are added/removed
     * This makes the layout responsive to screen size changes
     */
    updateLayout() {
        const config = ResourceCard.config;
        const layout = LayoutManager.calculateLayout(this.resources.length, config);

        // Adjust container height to fit all rows
        this.container.height((layout.total_rows * (config.resource_height + config.resource_gap)) - config.resource_gap + 5);

//        // Calculate container height - minimum of one resource card height
//        const minHeight = config.resource_height + GUI_CONFIG['layout-top-margin'] + 40; // 40px for padding
//        const calculatedHeight = (layout.total_rows * (config.resource_height + config.resource_gap)) - config.resource_gap + 5;
//        const containerHeight = Math.max(minHeight, calculatedHeight);
//
//        this.container.height(containerHeight);

        // Update position of each resource card
        this.resources.forEach((resource_card, index) => {
            const position = LayoutManager.getPosition(index, layout, config, this.alignment);
            resource_card.view?.setPosition(position.x, position.y);
        });
    }

    /**
     * Registers an event listener for custom events
     * Enables communication between different parts of the application
     * @param {string} event - Event name (e.g., 'resource_selected', 'user_selected')
     * @param {function} callback - Function to call when event occurs
     */
    addEventListener(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    /**
     * Removes a specific event listener
     * @param {string} event - Event name
     * @param {function} callback - The specific callback function to remove
     */
    removeEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    /**
     * Triggers all listeners for a specific event
     * This is how different parts of the app communicate with each other
     * @param {string} event - Event name to trigger
     * @param {object} data - Data to pass to the event listeners
     */
    dispatchEvent(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    /**
     * Handles when a resource card is clicked (not a user within it)
     * Dispatches a 'resource_selected' event for other components to handle
     * @param {number} resource_id - ID of the selected resource
     * @param {string} resource_name - Name of the selected resource
     */
    onResourceSelected(resource_id, resource_name) {
        this.dispatchEvent('resource_selected', { resource_id, resource_name });
    }
}

// ===== RESOURCE CARD CLASS (Data Model) =====
// Pure data model representing a bookable resource and its current reservations
// Follows Model-View pattern: this class holds data, ResourceView handles DOM
class ResourceCard {
    // Static configuration shared by all resource cards
    // Links to global GUI_CONFIG for consistent styling
    static config = {
        resource_width: GUI_CONFIG['resource-card-width'],
        resource_height: GUI_CONFIG['resource-card-height'],
        resource_gap: GUI_CONFIG['resource-gap'],
        resource_list_side_gap: GUI_CONFIG['resource-list-side-gap'],
        resource_list_top_gap: GUI_CONFIG['resource-list-top-gap']
    };

    /**
     * Creates a new resource card data model
     * @param {number} id - Unique resource identifier from database
     * @param {string} name - Display name of the resource
     * @param {number} list_font_size - Font size for user names in this resource
     */
    constructor(id, name, list_font_size = GUI_CONFIG['resource-card-list-font-size']) {
        this.id = id;                           // Database ID
        this.name = name;                       // Resource name (e.g., "Meeting Room A")
        this.list_font_size = list_font_size;   // Customizable font size for user list
        this.users = [];                        // Array of users who have reservations
        this.view = null;                       // Reference to ResourceView (set later)
    }

    /**
     * Links this data model to its visual representation
     * Enables two-way communication between model and view
     * @param {ResourceView} view - The DOM view component for this resource
     */
    setView(view) {
        this.view = view;
    }

    /**
     * Adds a user reservation to this resource
     * Updates both the data model and the visual representation
     * @param {string} name - User's display name
     * @param {number} id - User's database ID
     * @param {string} status - Reservation status ('approved', 'requested', etc.)
     * @param {string} request_date - When the reservation was requested
     * @param {string} approved_date - When the reservation was approved (if applicable)
     * @param {number} valid_until_date - Unix timestamp when reservation expires (for approved reservations)
     */
    addUser(name, id, status, request_date, approved_date, valid_until_date) {
        const user = { name, id, status, request_date, approved_date, valid_until_date };
        this.users.push(user);                          // Add to data model
        this.view?.addUser(user, this.list_font_size);  // Update visual representation
        this.view?.updateBackgroundColor();             // Change card color based on occupancy
    }

    /**
     * Removes a user reservation from this resource
     * Updates both the data model and the visual representation
     * @param {number} id - User ID to remove
     */
    removeUser(id) {
        this.users = this.users.filter(user => user.id !== id);  // Remove from data model
        this.view?.removeUser(id);                               // Remove from visual representation
        this.view?.updateBackgroundColor();                      // Update card color
    }

    /**
     * Handles when a user within this resource is clicked
     * Currently just a placeholder - the view handles the actual event delegation
     * @param {number} user_id - ID of the clicked user
     * @param {string} user_name - Name of the clicked user
     */
    onUserSelected(user_id, user_name) {
        // Resource doesn't know about ResourcePool - view handles event delegation
        // This separation keeps the data model independent of the UI framework
    }
}

// ===== RESOURCE VIEW (DOM Management) =====
// Handles all DOM manipulation and visual representation for a ResourceCard
// Follows Model-View pattern: this class manages UI, ResourceCard holds data
class ResourceView {
    /**
     * Creates the visual representation of a resource card
     * @param {ResourceCard} resource_card - The data model this view represents
     * @param {jQuery} container - Parent DOM element to append this view to
     * @param {ResourcePool} pool - Reference to the pool for event delegation
     */
    constructor(resource_card, container, pool) {
        this.resource_card = resource_card;  // Link to data model
        this.container = container;          // Parent DOM container
        this.pool = pool;                    // Reference for event handling
        this.element = this.createElement(); // Create the DOM structure
        this.updateBackgroundColor();       // Set initial background color
        this.container.append(this.element); // Add to DOM
    }

    /**
     * Creates the complete DOM structure for a resource card
     * Builds: main card container + title + scrollable user list
     * @returns {jQuery} The complete DOM element for this resource card
     */
    createElement() {
        const config = ResourceCard.config;
        const id = this.resource_card.id;

        // Main card container - positioned absolutely for grid layout
        const rectangle = $('<div></div>')
            .addClass('resource-card')
            .attr('data-resource-id', id)  // For easy DOM queries
            .css({
                position: 'absolute',  // Enables precise positioning in grid
                left: '0px',           // Will be updated by setPosition()
                top: '0px',            // Will be updated by setPosition()
                width: config.resource_width + 'px',
                height: config.resource_height + 'px'
            })
            .click((e) => {
                // Only trigger resource selection if user didn't click on a user item
                if (!$(e.target).hasClass('user-item')) {
                    this.pool.onResourceSelected(id, this.resource_card.name);
                }
            });

        // Resource title - displays the resource name at the top
        const title = $('<div></div>')
            .addClass('resource-title')
            .text(this.resource_card.name)
            .css({
                position: 'absolute',
                left: config.resource_list_side_gap + 'px',
                top: '10px',
                width: (config.resource_width - (2 * config.resource_list_side_gap)) + 'px',
                height: 'auto',  // Allow multi-line titles
                'font-size': GUI_CONFIG['resource-card-title-font-size'] + 'px'
            });

        // User list container - scrollable area for user reservations
        this.user_list = $('<div></div>')
            .addClass('user-list')
            .css({
                position: 'absolute',
                left: config.resource_list_side_gap + 'px',
                width: (config.resource_width - (2 * config.resource_list_side_gap)) + 'px',
                bottom: config.resource_list_side_gap + 'px',
                height: (config.resource_height - config.resource_list_top_gap - config.resource_list_side_gap) + 'px'
            });

        rectangle.append(title).append(this.user_list);

        // Dynamically adjust user list height based on actual title height
        // setTimeout ensures title is rendered before measuring
        setTimeout(() => this.adjustUserListHeight(), 0);

        return rectangle;
    }

    /**
     * Updates the card's background color based on occupancy status
     * Green = available (no users), Orange = occupied (has users)
     */
    updateBackgroundColor() {
        const isEmpty = this.resource_card.users.length === 0;
        const background = isEmpty ?
            'linear-gradient(135deg, rgb(3 167 118), rgb(246 248 249))' :         // Green gradient for empty resource card background
            'linear-gradient(135deg, rgb(0 107 165), rgb(255 255 255)';           // Orange gradient for occupied resource card background
        this.element.css('background', background);
    }

    /**
     * Adds a user item to the visual user list
     * Creates a colored, clickable element representing a user's reservation
     * @param {object} user - User data (name, id, status, etc.)
     * @param {number} fontSize - Font size for the user's name
     */
    addUser(user, fontSize) {
        // Color-code based on reservation status
        let backgroundColor;
        if (user.status === 'approved') {
            backgroundColor = 'linear-gradient(135deg, rgb(205 36 27), rgb(247 211 211))';  // Red gradient for approved user item
        } else if (user.status === 'requested') {
            backgroundColor = 'linear-gradient(135deg, rgb(45 143 141), rgb(216, 222, 255))';   // Blue gradient for requested user item
        } else {
            backgroundColor = 'linear-gradient(135deg, #8E8E93, #AEAEB2)';   // Gray gradient for other status user item
        }

        // Highlight the current logged-in user's reservations with a black border
        const currentUserId = this.getCurrentUserId();
        const isCurrentUser = currentUserId && user.id === currentUserId;

        // Check if user has countdown (approved with valid_until_date)
        const hasCountdown = user.status === 'approved' && user.valid_until_date;
        
        // Create user item container
        const user_item = $('<div></div>')
            .addClass('user-item')
            .attr('data-user-id', user.id)
            .css({
                'background': backgroundColor,
                'border': isCurrentUser ? '2px solid #000000' : 'none',
                'position': 'relative',
                'height': hasCountdown ? '40px' : '25px'  // Taller for countdown
            });

        // Create user name element
        const nameElement = $('<div></div>')
            .addClass('user-name')
            .text(user.name)
            .css({
                'font-size': fontSize + 'px',
                'text-align': 'center',
                'line-height': hasCountdown ? '20px' : '25px'
            });

        user_item.append(nameElement);

        // Add countdown on second line if approved
        if (hasCountdown) {
            const countdownElement = $('<div></div>')
                .addClass('user-countdown')
                .css({
                    'font-size': (fontSize - 2) + 'px',
                    'text-align': 'center',
                    'line-height': '20px',
                    'color': '#333'
                });
            user_item.append(countdownElement);
        }

        // Add hover actions for current user only
        if (isCurrentUser) {
            const actionsContainer = $('<div></div>')
                .addClass('user-actions')
                .css({
                    'position': 'absolute',
                    'right': '5px',
                    'top': '50%',
                    'transform': 'translateY(-50%)',
                    'display': 'none'
                });

            // Release/Cancel button
            const primaryAction = user.status === 'approved' ? 'release' : 'cancel';
            const primaryIcon = user.status === 'approved' ? '❌' : '🚫';
            const primaryButton = $('<span></span>')
                .addClass('action-btn primary-action')
                .attr('data-action', primaryAction)
                .text(primaryIcon)
                .css({
                    'cursor': 'pointer',
                    'margin-left': '3px',
                    'font-size': '14px'
                });

            actionsContainer.append(primaryButton);

            // Keep alive button (only for approved reservations)
            if (user.status === 'approved') {
                const keepAliveButton = $('<span></span>')
                    .addClass('action-btn keep-alive-action')
                    .attr('data-action', 'keep_alive')
                    .text('⏰')
                    .css({
                        'cursor': 'pointer',
                        'margin-left': '3px',
                        'font-size': '14px'
                    });
                actionsContainer.append(keepAliveButton);
            }

            user_item.append(actionsContainer);

            // Hover events
            user_item.hover(
                () => actionsContainer.show(),
                () => actionsContainer.hide()
            );

            // Action button clicks
            actionsContainer.on('click', '.action-btn', (e) => {
                e.stopPropagation();
                const action = $(e.target).attr('data-action');
                this.handleUserAction(user, action);
            });
        }

        // Click handler disabled - users must use hover action buttons

        this.user_list.append(user_item);
    }

    /**
     * Removes a user item from the visual user list
     * @param {number} id - User ID to remove
     */
    removeUser(id) {
        this.user_list.find(`[data-user-id="${id}"]`).remove();
    }

    /**
     * Updates the absolute position of this resource card in the grid
     * Called by ResourcePool.updateLayout() when repositioning cards
     * @param {number} x - X coordinate in pixels
     * @param {number} y - Y coordinate in pixels
     */
    setPosition(x, y) {
        this.element.css({
            left: x + 'px',
            top: y + 'px'
        });
    }

    /**
     * Gets the current logged-in user's ID from the session manager
     * Used to highlight the user's own reservations
     * @returns {number|null} Current user ID or null if not logged in
     */
    getCurrentUserId() {
        return SessionManager.getCurrentUserId();
    }

    /**
     * Dynamically adjusts the user list height based on the actual title height
     * This handles multi-line titles by measuring the rendered title and adjusting accordingly
     * Called after the title is rendered to ensure accurate measurements
     */
    adjustUserListHeight() {
        const config = ResourceCard.config;
        const title = this.element.find('.resource-title');
        const actualTitleHeight = title.outerHeight();  // Get actual rendered height
        const titleTop = 10;                            // Title's top position
        const newUserListTop = titleTop + actualTitleHeight + 5;  // 5px gap between title and list
        const newUserListHeight = config.resource_height - newUserListTop - config.resource_list_side_gap;

        // Update the user list position and height
        this.user_list.css({
            top: newUserListTop + 'px',
            height: newUserListHeight + 'px'
        });
    }

    /**
     * Converts seconds to HH:MM:SS format
     * @param {number} seconds - Number of seconds to convert
     * @returns {string} Time in HH:MM:SS format
     */
    convertToHHMMSS(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Handles action button clicks for user items
     * @param {object} user - User data
     * @param {string} action - Action to perform ('release', 'cancel', 'keep_alive')
     */
    handleUserAction(user, action) {
        this.pool.dispatchEvent('user_action', {
            resource_id: this.resource_card.id,
            resource_name: this.resource_card.name,
            user_id: user.id,
            user_name: user.name,
            action: action
        });
    }

    /**
     * Updates the remaining time display for approved reservations
     * Called every second to refresh countdown timers
     */
    updateRemainingTimes() {
        this.resource_card.users.forEach(user => {
            const userElement = this.user_list.find(`[data-user-id="${user.id}"]`);
            const countdownElement = userElement.find('.user-countdown');
            
            if (countdownElement.length > 0 && user.status === 'approved' && user.valid_until_date) {
                const currentTime = Math.floor(Date.now() / 1000);
                const remainingSeconds = user.valid_until_date - currentTime;
                if (remainingSeconds > 0) {
                    const timeString = this.convertToHHMMSS(remainingSeconds);
                    countdownElement.text(timeString);
                } else {
                    countdownElement.text('EXPIRED');
                }
            }
        });
    }

    /**
     * Removes this view from the DOM and cleans up resources
     * Called when the resource is removed or the pool is cleared
     */
    destroy() {
        this.element.remove();
    }
}



