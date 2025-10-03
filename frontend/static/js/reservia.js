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

    updateLayout() {
        const resource_number = this.resources.length;
        const layout = this.calculateLayout(resource_number);

        for (let i = 0; i < this.resources.length; i++) {
            const row = Math.floor(i / layout.rectangles_per_row);
            const col = i % layout.rectangles_per_row;
            
            const rectangles_in_row = Math.min(layout.rectangles_per_row, resource_number - (row * layout.rectangles_per_row));
            const total_row_width = (rectangles_in_row * this.config.resource_width) + ((rectangles_in_row - 1) * this.config.resource_gap);
            const start_x = (layout.screen_width - total_row_width) / 2;
            
            const x_position = start_x + (col * (this.config.resource_width + this.config.resource_gap));
            const y_position = (row * (this.config.resource_height + this.config.resource_gap)) + 20;
            
            this.resources[i].element.css({
                left: x_position + 'px',
                top: y_position + 'px'
            });
        }
    }
}

// ===== RESOURCE CLASS =====
class Resource {
    constructor(id, list_size = 12) {
        this.id = id;
        this.list_size = list_size;
        this.pool = ResourcePool.getInstance();
        this.element = this.createElement();
    }

    createElement() {
        const config = this.pool.config;

        const rectangle = $('<div></div>')
            .addClass('resource-rectangle')
            .attr('id', `resource-${this.id}`)
            .css({
                position: 'absolute',
                left: '0px',
                top: '0px',
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

    addUser(name, id) {
        const user_list = $(`#user-list-${this.id}`);
        const user_item = $('<div></div>')
            .addClass('user-item')
            .attr('data-user-id', id)
            .text(name)
            .css('font-size', this.list_size + 'px')
            .click(() => {
                this.onUserSelected(id, name);
            });
        user_list.append(user_item);
    }

    removeUser(id) {
        $(`#user-list-${this.id} .user-item[data-user-id="${id}"]`).remove();
    }

    onUserSelected(user_id, user_name) {
        console.log(`User selected - Resource: ${this.id}, User ID: ${user_id}, Name: ${user_name}`);
    }
}



// ===== TEST DATA GENERATION =====
function fillUpResourcePoolWithTestData() {
    const pool = ResourcePool.getInstance();
    
    for (let i = 1; i <= 20; i++) {
        const resource = new Resource(i, 20);
        pool.addResource(resource);
        
        for (let j = 1; j < i; j++) {
            resource.addUser(j.toString(), j);
        }
    }
    
    pool.updateLayout();
}