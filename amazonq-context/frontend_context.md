# Frontend Context for Amazon Q

> This document provides complete frontend architecture context for Amazon Q to reproduce the project from scratch.

## Overview
The Reservia frontend implements a clean, object-oriented architecture with proper separation of concerns between data models, view components, and layout management.

## Core Classes

### LayoutManager (Static Utility)
**Purpose**: Handles responsive grid positioning calculations

**Key Methods**:
- `calculateLayout(resource_count, config)`: Determines grid dimensions based on screen width
- `getPosition(index, layout, config)`: Calculates exact pixel coordinates for resource positioning

**Features**:
- Responsive design that adapts to screen width
- Centered grid layout with proper spacing
- Automatic row/column calculations

### ResourcePool (Singleton)
**Purpose**: Manages the collection of resources and overall layout

**Key Methods**:
- `addResource(resource)`: Adds resource to pool and creates its view
- `updateLayout()`: Repositions all resources in responsive grid
- `clear()`: Removes all resources and cleans up DOM
- `onResourceSelected(resource_id)`: Handles resource click events

**Features**:
- Singleton pattern ensures single pool per page
- Automatic view creation and management
- Window resize support

### Resource (Data Model)
**Purpose**: Pure data model representing a resource with user management

**Key Properties**:
- `id`: Unique resource identifier
- `list_font_size`: Configurable font size for user list items (default: 20px)
- `users[]`: Array of user objects
- `static config`: Shared configuration for all resources

**Key Methods**:
- `addUser(name, id)`: Adds user to resource and updates view
- `removeUser(id)`: Removes user from resource and updates view
- `onUserSelected(user_id, user_name)`: Handles user click events

**Features**:
- Independent of DOM and ResourcePool
- Static configuration shared across all instances
- Customizable user list font sizes

### ResourceView (DOM Management)
**Purpose**: Handles DOM creation, rendering, and event management

**Key Methods**:
- `createElement()`: Creates the resource rectangle DOM structure
- `addUser(user, fontSize)`: Adds user item to scrollable list
- `removeUser(id)`: Removes user item from list
- `setPosition(x, y)`: Updates resource position
- `destroy()`: Cleans up DOM elements

**Features**:
- Proper event delegation and handling
- Scrollable user lists with Apple-styled scrollbars
- Click event separation (resource vs user clicks)

## Architecture Benefits

### Separation of Concerns
- **Data**: Resource class manages user data
- **View**: ResourceView handles DOM manipulation
- **Layout**: LayoutManager calculates positioning
- **Collection**: ResourcePool manages resource lifecycle

### Independence
- Resource class has no DOM dependencies
- ResourceView can be modified without affecting Resource
- Layout logic is reusable and testable
- Clear interfaces between components

### Event System
- **Resource Clicks**: Title, empty areas → `ResourcePool.onResourceSelected()`
- **User Clicks**: User list items → `Resource.onUserSelected()`
- No event bubbling conflicts
- Proper event target detection

## Configuration

### Resource Configuration (Static)
```javascript
Resource.config = {
    resource_width: 200,        // Resource rectangle width
    resource_height: 400,       // Resource rectangle height
    resource_gap: 20,           // Gap between resources
    resource_list_side_gap: 6,  // Side padding for user list
    resource_list_top_gap: 50,  // Top space for title
};
```

### Scrollbar Styling
- **Width**: 7px with 3.5px border-radius for perfect alignment
- **Colors**: Apple blue theme (rgba(0,122,255))
- **Track**: Light blue background (10% opacity)
- **Thumb**: Medium blue (60% opacity), darker on hover (80%)

## Usage Example

```javascript
// Initialize ResourcePool
const pool = ResourcePool.getInstance();

// Create resource with custom font size
const resource = new Resource(1, 24); // ID=1, font size=24px
pool.addResource(resource);

// Add users to resource
resource.addUser("John", 101);
resource.addUser("Jane", 102);

// Update layout for responsive positioning
pool.updateLayout();
```

## Test Data Generation

The `fillUpResourcePoolWithTestData()` function creates 20 resources with progressive user counts:
- Resource 1: 0 users
- Resource 2: 1 user
- Resource 3: 2 users
- ...
- Resource 20: 19 users

This provides comprehensive testing of scrollable lists and layout responsiveness.