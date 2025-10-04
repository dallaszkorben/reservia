// ===== LAYOUT MANAGER =====
class LayoutManager {
    static calculateLayout(resource_count, config) {
        const screen_width = $(window).width() - 40;
        const rectangle_with_gap = config.resource_width + config.resource_gap;
        const rectangles_per_row = Math.floor(screen_width / rectangle_with_gap);
        const total_rows = Math.max(1, Math.ceil(resource_count / rectangles_per_row));

        return { rectangles_per_row, total_rows, screen_width, resource_count };
    }

    static getPosition(index, layout, config, alignment = 'center') {
        const row = Math.floor(index / layout.rectangles_per_row);
        const col = index % layout.rectangles_per_row;

        const rectangles_in_current_row = Math.min(layout.rectangles_per_row, layout.resource_count - (row * layout.rectangles_per_row));
        const total_row_width = (rectangles_in_current_row * config.resource_width) + ((rectangles_in_current_row - 1) * config.resource_gap);

        let start_x;
        if (alignment === 'center') {
            start_x = (layout.screen_width - total_row_width) / 2;
        } else if (alignment === 'right') {
            start_x = layout.screen_width - total_row_width;
        } else { // 'left'
            start_x = 0;
        }

        const x_position = start_x + (col * (config.resource_width + config.resource_gap));
        const y_position = (row * (config.resource_height + config.resource_gap)) + 20;

        return { x: x_position, y: y_position };
    }
}

// ===== RESOURCE POOL SINGLETON =====
class ResourcePool {
    static instance = null;

    constructor(alignment = 'center') {
        if (ResourcePool.instance) {
            return ResourcePool.instance;
        }
        this.container = $('#resource-pool-container');
        this.resources = [];
        this.listeners = {};
        this.alignment = alignment;
        ResourcePool.instance = this;
    }

    static getInstance(alignment = 'center') {
        if (!ResourcePool.instance) {
            ResourcePool.instance = new ResourcePool(alignment);
        } else if (alignment !== 'center') {
            ResourcePool.instance.alignment = alignment;
        }
        return ResourcePool.instance;
    }

    addResource(resource_card) {
        this.resources.push(resource_card);
        const view = new ResourceView(resource_card, this.container, this);
        resource_card.setView(view);
    }

    clear() {
        this.resources.forEach(resource_card => resource_card.view?.destroy());
        this.container.empty();
        this.resources = [];
    }

    updateLayout() {
        const config = ResourceCard.config;
        const layout = LayoutManager.calculateLayout(this.resources.length, config);

        this.container.height((layout.total_rows * (config.resource_height + config.resource_gap)) - config.resource_gap + 5);

        this.resources.forEach((resource_card, index) => {
            const position = LayoutManager.getPosition(index, layout, config, this.alignment);
            resource_card.view?.setPosition(position.x, position.y);
        });
    }

    addEventListener(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    removeEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    dispatchEvent(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    onResourceSelected(resource_id) {
        this.dispatchEvent('resource_selected', { resource_id });
    }
}

// ===== RESOURCE CARD CLASS (Data Model) =====
class ResourceCard {
    static config = {
        resource_width: 200,
        resource_height: 400,
        resource_gap: 20,
        resource_list_side_gap: 6,
        resource_list_top_gap: 50,
    };

    constructor(id, list_font_size = 20) {
        this.id = id;
        this.list_font_size = list_font_size;
        this.users = [];
        this.view = null;
    }

    setView(view) {
        this.view = view;
    }

    addUser(name, id) {
        const user = { name, id };
        this.users.push(user);
        this.view?.addUser(user, this.list_font_size);
        this.view?.updateBackgroundColor();
    }

    removeUser(id) {
        this.users = this.users.filter(user => user.id !== id);
        this.view?.removeUser(id);
        this.view?.updateBackgroundColor();
    }

    onUserSelected(user_id, user_name) {
        // Resource doesn't know about ResourcePool - view handles event delegation
        console.log(`User selected - Resource: ${this.id}, User ID: ${user_id}, Name: ${user_name}`);
    }
}

// ===== RESOURCE VIEW (DOM Management) =====
class ResourceView {
    constructor(resource_card, container, pool) {
        this.resource_card = resource_card;
        this.container = container;
        this.pool = pool;
        this.element = this.createElement();
        this.updateBackgroundColor();
        this.container.append(this.element);
    }

    createElement() {
        const config = ResourceCard.config;
        const id = this.resource_card.id;

        const rectangle = $('<div></div>')
            .addClass('resource-card')
            .attr('data-resource-id', id)
            .css({
                position: 'absolute',
                left: '0px',
                top: '0px',
                width: config.resource_width + 'px',
                height: config.resource_height + 'px'
            })
            .click((e) => {
                if (!$(e.target).hasClass('user-item')) {
                    this.pool.onResourceSelected(id);
                }
            });

        const title = $('<div></div>')
            .addClass('resource-title')
            .text(`R${id}`)
            .css({
                position: 'absolute',
                left: config.resource_list_side_gap + 'px',
                top: '10px',
                width: (config.resource_width - (2 * config.resource_list_side_gap)) + 'px',
                height: '15px'
            });

        this.user_list = $('<div></div>')
            .addClass('user-list')
            .css({
                position: 'absolute',
                left: config.resource_list_side_gap + 'px',
                right: config.resource_list_side_gap + 'px',
                bottom: config.resource_list_side_gap + 'px',
                height: (config.resource_height - config.resource_list_top_gap - config.resource_list_side_gap) + 'px'
            });

        rectangle.append(title).append(this.user_list);
        return rectangle;
    }

    updateBackgroundColor() {
        const isEmpty = this.resource_card.users.length === 0;
        const background = isEmpty ? 
            'linear-gradient(135deg, #34C759 0%, #32D74B 30%, #5AC8FA 100%)' : 
            'linear-gradient(135deg, #FFB366, #FFCC99)';
        this.element.css('background', background);
    }

    addUser(user, fontSize) {
        const isFirstUser = this.resource_card.users.length === 1;
        const backgroundColor = isFirstUser ? 
            'linear-gradient(135deg, #FF3B30, #FF6B6B)' :  // Red gradient for first user (active/approved)
            'linear-gradient(135deg, #007AFF, #5AC8FA)';   // Blue gradient for queued users
        
        const user_item = $('<div></div>')
            .addClass('user-item')
            .attr('data-user-id', user.id)
            .text(user.name)
            .css({
                'font-size': fontSize + 'px',
                'background': backgroundColor
            })
            .click(() => {
                this.resource_card.onUserSelected(user.id, user.name);
                this.pool.dispatchEvent('user_selected', {
                    resource_id: this.resource_card.id,
                    user_id: user.id,
                    user_name: user.name
                });
            });
        this.user_list.append(user_item);
    }

    removeUser(id) {
        this.user_list.find(`[data-user-id="${id}"]`).remove();
    }

    setPosition(x, y) {
        this.element.css({
            left: x + 'px',
            top: y + 'px'
        });
    }

    destroy() {
        this.element.remove();
    }
}



// ===== TEST DATA GENERATION =====
function testLookOfTheResourceElements() {
    const pool = ResourcePool.getInstance('center');

    for (let i = 1; i <= 3; i++) {
        const resource_card = new ResourceCard(i, 20);
        pool.addResource(resource_card);

        for (let j = 1; j < i; j++) {
            resource_card.addUser(j.toString(), j);
        }
    }

    pool.updateLayout();
}

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
                console.log(`RELEASED - Resource: R${data.resource_id}, User: ${currentUserId}`);
            } else {
                console.log(`CANCELLED - Resource: R${data.resource_id}, User: ${currentUserId}`);
            }
        }
    });

    pool.addEventListener('resource_selected', (data) => {
        const currentUserId = parseInt($('#current-user').val());
        const resource = pool.resources.find(r => r.id === data.resource_id);
        const userExists = resource.users.some(u => u.id === currentUserId);

        if (!userExists) {
            resource.addUser(currentUserId.toString(), currentUserId);
            console.log(`ADDED - Resource: R${data.resource_id}, User: ${currentUserId}`);
        }
    });

    testLookOfTheResourceElements();
}