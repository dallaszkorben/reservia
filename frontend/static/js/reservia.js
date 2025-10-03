// ===== RESOURCE POOL SINGLETON =====
class ResourcePool {
    static instance = null;

    constructor() {
        if (ResourcePool.instance) {
            return ResourcePool.instance;
        }
        this.container = $('#resource-container');
        this.resources = [];
        this.config = {
            resource_width: 200,
            resource_height: 400,
            resource_gap: 20,
            resource_list_side_gap: 6,
            resource_list_top_gap: 50,
        };
        ResourcePool.instance = this;
    }

    static getInstance() {
        if (!ResourcePool.instance) {
            ResourcePool.instance = new ResourcePool();
        }
        return ResourcePool.instance;
    }

    addResource(resource) {
        this.resources.push(resource);
        this.container.append(resource.element);
    }

    clear() {
        this.container.empty();
        this.resources = [];
    }

    calculateLayout(resource_number) {
        const screen_width = $(window).width() - 40;
        const rectangle_with_gap = this.config.resource_width + this.config.resource_gap;
        const rectangles_per_row = Math.floor(screen_width / rectangle_with_gap);
        const total_rows = Math.max(1, Math.ceil(resource_number / rectangles_per_row));
        const row_with_gap = this.config.resource_height + this.config.resource_gap;

        this.container.height((total_rows * row_with_gap) - this.config.resource_gap + 40);

        return { rectangles_per_row, total_rows, screen_width };
    }
}

// ===== RESOURCE CLASS =====
class Resource {
    constructor(id, x_position, y_position) {
        this.id = id;
        this.pool = ResourcePool.getInstance();
        this.element = this.createElement(x_position, y_position);
        this.populateUsers();
    }

    createElement(x_position, y_position) {
        const config = this.pool.config;

        const rectangle = $('<div></div>')
            .addClass('resource-rectangle')
            .attr('id', `resource-${this.id}`)
            .css({
                position: 'absolute',
                left: x_position + 'px',
                top: y_position + 'px',
                width: config.resource_width + 'px',
                height: config.resource_height + 'px'
            });

        const title = $('<div></div>')
            .addClass('resource-title')
            .text(`R${this.id}`)
            .css({
                position: 'absolute',
                left: config.resource_list_side_gap + 'px',
                top: '10px',
                width: (config.resource_width - (2 * config.resource_list_side_gap)) + 'px',
                height: '15px'
            });

        const user_list = $('<div></div>')
            .addClass('user-list')
            .attr('id', `user-list-${this.id}`)
            .css({
                position: 'absolute',
                left: config.resource_list_side_gap + 'px',
                right: config.resource_list_side_gap + 'px',
                bottom: config.resource_list_side_gap + 'px',
                height: (config.resource_height - config.resource_list_top_gap - config.resource_list_side_gap) + 'px'
            });

        rectangle.append(title).append(user_list);
        return rectangle;
    }

    populateUsers() {
        for (let user_id = 1; user_id <= 30; user_id++) {
            addUserToList(this.id, user_id.toString(), user_id);
        }
    }
}

// ===== RESOURCE GENERATION =====
function generateResourceRectangles() {
    const resource_number = 20;
    const pool = ResourcePool.getInstance();
    const layout = pool.calculateLayout(resource_number);

    console.log(`Creating ${resource_number} rectangles in ${layout.total_rows} rows (${layout.rectangles_per_row} per row)`);

    for (let row = 0; row < layout.total_rows; row++) {
        const start_index = row * layout.rectangles_per_row;
        const end_index = Math.min(start_index + layout.rectangles_per_row, resource_number);
        const rectangles_in_row = end_index - start_index;

        const total_row_width = (rectangles_in_row * pool.config.resource_width) + ((rectangles_in_row - 1) * pool.config.resource_gap);
        const start_x = (layout.screen_width - total_row_width) / 2;

        for (let i = 0; i < rectangles_in_row; i++) {
            const rectangle_id = start_index + i + 1;
            const x_position = start_x + (i * (pool.config.resource_width + pool.config.resource_gap));
            const y_position = (row * (pool.config.resource_height + pool.config.resource_gap)) + 20;

            const resource = new Resource(rectangle_id, x_position, y_position);
            pool.addResource(resource);
        }

        console.log(`Row ${row + 1}: ${rectangles_in_row} rectangles, starting at x=${start_x}`);
    }
}

// ===== USER LIST MANAGEMENT =====
function addUserToList(resource_id, name, id) {
    const user_list = $(`#user-list-${resource_id}`);
    const user_item = $('<div></div>')
        .addClass('user-item')
        .attr('data-user-id', id)
        .text(name)
        .click(function() {
            onUserSelected(resource_id, id, name);
        });
    user_list.append(user_item);
}

function removeUserFromList(resource_id, id) {
    $(`#user-list-${resource_id} .user-item[data-user-id="${id}"]`).remove();
}

function onUserSelected(resource_id, user_id, user_name) {
    console.log(`User selected - Resource: ${resource_id}, User ID: ${user_id}, Name: ${user_name}`);
}