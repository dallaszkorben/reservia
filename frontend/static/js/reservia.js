// ===== LAYOUT MANAGER =====
class LayoutManager {
    static calculateLayout(resource_count, config) {
        const screen_width = $(window).width() - 40;
        const rectangle_with_gap = config.resource_width + config.resource_gap;
        const rectangles_per_row = Math.floor(screen_width / rectangle_with_gap);
        const total_rows = Math.max(1, Math.ceil(resource_count / rectangles_per_row));
        
        return { rectangles_per_row, total_rows, screen_width };
    }

    static getPosition(index, layout, config) {
        const row = Math.floor(index / layout.rectangles_per_row);
        const col = index % layout.rectangles_per_row;
        
        const rectangles_in_row = Math.min(layout.rectangles_per_row, layout.total_rows * layout.rectangles_per_row - (row * layout.rectangles_per_row));
        const total_row_width = (rectangles_in_row * config.resource_width) + ((rectangles_in_row - 1) * config.resource_gap);
        const start_x = (layout.screen_width - total_row_width) / 2;
        
        const x_position = start_x + (col * (config.resource_width + config.resource_gap));
        const y_position = (row * (config.resource_height + config.resource_gap)) + 20;
        
        return { x: x_position, y: y_position };
    }
}

// ===== RESOURCE POOL SINGLETON =====
class ResourcePool {
    static instance = null;

    constructor() {
        if (ResourcePool.instance) {
            return ResourcePool.instance;
        }
        this.container = $('#resource-container');
        this.resources = [];
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
        const view = new ResourceView(resource, this.container);
        resource.setView(view);
    }

    clear() {
        this.resources.forEach(resource => resource.view?.destroy());
        this.container.empty();
        this.resources = [];
    }

    updateLayout() {
        const config = Resource.config;
        const layout = LayoutManager.calculateLayout(this.resources.length, config);
        
        this.container.height((layout.total_rows * (config.resource_height + config.resource_gap)) - config.resource_gap + 40);
        
        this.resources.forEach((resource, index) => {
            const position = LayoutManager.getPosition(index, layout, config);
            resource.view?.setPosition(position.x, position.y);
        });
    }

    onResourceSelected(resource_id) {
        console.log(`Resource selected - Resource ID: ${resource_id}`);
    }
}

// ===== RESOURCE CLASS (Data Model) =====
class Resource {
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
    }

    removeUser(id) {
        this.users = this.users.filter(user => user.id !== id);
        this.view?.removeUser(id);
    }

    onUserSelected(user_id, user_name) {
        console.log(`User selected - Resource: ${this.id}, User ID: ${user_id}, Name: ${user_name}`);
    }
}

// ===== RESOURCE VIEW (DOM Management) =====
class ResourceView {
    constructor(resource, container) {
        this.resource = resource;
        this.container = container;
        this.element = this.createElement();
        this.container.append(this.element);
    }

    createElement() {
        const config = Resource.config;
        const id = this.resource.id;

        const rectangle = $('<div></div>')
            .addClass('resource-rectangle')
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
                    ResourcePool.getInstance().onResourceSelected(id);
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

    addUser(user, fontSize) {
        const user_item = $('<div></div>')
            .addClass('user-item')
            .attr('data-user-id', user.id)
            .text(user.name)
            .css('font-size', fontSize + 'px')
            .click(() => {
                this.resource.onUserSelected(user.id, user.name);
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