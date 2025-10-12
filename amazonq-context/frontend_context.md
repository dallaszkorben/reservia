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

### Global GUI Configuration
```javascript
const GUI_CONFIG = {
    'resource-card-width': 250,           // Width of each resource card in pixels
    'resource-card-height': 400,          // Height of each resource card in pixels
    'resource-card-list-font-size': 15,   // Font size for user names in the resource card
    'resource-card-title-font-size': 25,  // Font size for resource title
    'resource-card-title-length': 25      // Maximum characters allowed in resource name
};
```

### Resource Configuration (Static)
```javascript
ResourceCard.config = {
    resource_width: GUI_CONFIG['resource-card-width'],    // Card width in pixels
    resource_height: GUI_CONFIG['resource-card-height'],  // Card height in pixels
    resource_gap: 20,                                     // Space between cards
    resource_list_side_gap: 6,                           // Left/right padding inside card
    resource_list_top_gap: 50,                           // Space reserved for title area
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

## Recent Updates

### Configurable Requested Reservation Expiration (Latest)
**Features**: Conditional countdown display based on backend configuration
- **Dual Expiration Model**: Supports both approved and requested reservation expiration
- **Conditional Display**: Countdown and keep-alive only shown when `valid_until_date != null`
- **Backend Integration**: Respects `requested_keep_alive_sec` configuration setting
- **Flexible UI**: Single-line (no expiration) vs multi-line (with countdown) user items

**Implementation Details**:
- `hasCountdown = user.valid_until_date != null && user.valid_until_date > 0`
- Keep-alive button only appears for reservations with expiration times
- Height adjustment: 25px (no countdown) vs 40px (with countdown)
- Null-safe countdown timer updates

### Hover Action Interface
**Features**: Icon-based user actions with improved UX
- **Hover Actions**: ❌ (Release/Cancel) and ⏰ (Keep Alive) icons appear on hover
- **User Restrictions**: Only logged-in user sees action buttons on their own reservations
- **Multi-line Layout**: User name and countdown timer on separate lines (40px height vs 25px)
- **Transparent Icons**: Action buttons with transparent backgrounds for subtle appearance
- **Disabled Simple Clicks**: Users must use hover icons, no accidental actions from regular clicks

**Implementation Details**:
- `handleUserAction()`: Processes icon-based actions with `user_action` events
- Dynamic height adjustment: 25px (standard) vs 40px (with countdown)
- Removed `user_selected` event handler for simplified interaction model
- CSS flexbox layout for proper vertical alignment of name and countdown

### Reservation Expiration & Keep-Alive System
**Features**: Real-time countdown and keep-alive functionality
- **Live Countdown Display**: Shows remaining time in HH:MM:SS format for approved reservations
- **Dual-Timer System**: 5-second server sync + 1-second UI countdown updates
- **Keep-Alive Integration**: ⏰ icon to extend reservation validity
- **Time Formatting**: `convertToHHMMSS()` helper for consistent time display
- **Refresh Optimization**: Separate timers prevent visual "jumps" in countdown

**Implementation Details**:
- `updateRemainingTimes()`: Updates countdown displays in separate DOM elements
- `usersEqual()`: Compares `valid_until_date` to detect keep-alive changes
- Dual timer management: `autoRefreshInterval` (5s) + `timeUpdateInterval` (1s)

### User List Layout Fix
**Issue**: Inconsistent spacing in resource card user lists - 10px gap on left, no gap on right
**Root Cause**: CSS `.user-list` class had `padding: 5px` conflicting with JavaScript positioning
**Solution**: Removed CSS padding, letting JavaScript `resource_list_side_gap: 6` control all spacing
**Result**: Uniform 6px gaps on left, right, and bottom sides of user lists

### Global Configuration System
**Implementation**: Created centralized `GUI_CONFIG` object for all dimensions and font sizes
**Benefits**: 
- Single location for customizing entire interface
- Replaced hardcoded values throughout codebase
- JavaScript-controlled styling overrides CSS for dynamic configuration

### Resource Modification Workflow
**Features**: Complete admin resource modification system
- Hover-based submenu: "Manage Resource" → "Modify >" → resource list
- Direct resource selection opens modify dialog
- REST API integration with `/admin/resource/modify` endpoint
- Proper z-index layering for nested dropdowns

## Test Data Generation

The `fillUpResourcePoolWithTestData()` function creates 20 resources with progressive user counts:
- Resource 1: 0 users
- Resource 2: 1 user
- Resource 3: 2 users
- ...
- Resource 20: 19 users

This provides comprehensive testing of scrollable lists and layout responsiveness.