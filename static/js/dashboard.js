// Dashboard JavaScript
let inventoryData = [];
let sensorData = {};
let volunteersData = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadInventory();
    loadSensorData();
    checkSpoilage();
    loadVolunteers();
    
    // Setup form submission
    document.getElementById('quick-add-form').addEventListener('submit', function(e) {
        e.preventDefault();
        addItem();
    });
    
    // Close modal when clicking outside
    document.getElementById('addItemModal').addEventListener('click', function(e) {
        if (e.target.id === 'addItemModal') {
            closeAddItemModal();
        }
    });
    
    // Setup volunteer form submission
    document.getElementById('volunteer-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveVolunteer();
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const itemModal = document.getElementById('addItemModal');
            const volunteerModal = document.getElementById('volunteerModal');
            if (itemModal && itemModal.style.display === 'flex') {
                closeAddItemModal();
            }
            if (volunteerModal && volunteerModal.style.display === 'flex') {
                closeVolunteerModal();
            }
        }
    });
    
    // Close volunteer modal when clicking outside
    document.getElementById('volunteerModal').addEventListener('click', function(e) {
        if (e.target.id === 'volunteerModal') {
            closeVolunteerModal();
        }
    });
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadInventory();
        loadSensorData();
        loadVolunteers();
    }, 30000);
});

// Modal functions
function openAddItemModal() {
    document.getElementById('addItemModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeAddItemModal() {
    document.getElementById('addItemModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    // Reset form
    document.getElementById('quick-add-form').reset();
}

async function loadInventory() {
    try {
        const response = await fetch('/api/inventory');
        inventoryData = await response.json();
        renderInventoryList();
    } catch (error) {
        console.error('Error loading inventory:', error);
        showToast('Error loading inventory data', 'danger');
    }
}

async function loadSensorData() {
    try {
        const response = await fetch('/api/sensors');
        sensorData = await response.json();
        updateSensorDisplay();
    } catch (error) {
        console.error('Error loading sensor data:', error);
    }
}

function renderInventoryList() {
    const container = document.getElementById('inventory-list');
    
    if (inventoryData.length === 0) {
        container.innerHTML = `
            <div class="empty-inventory">
                <i class="fas fa-box-open"></i>
                <h5>No items in fridge</h5>
                <p>Add items using the form</p>
            </div>
        `;
        return;
    }

    // Sort items by status and name
    const sortedItems = inventoryData.sort((a, b) => {
        if (a.is_spoiled !== b.is_spoiled) {
            return b.is_spoiled - a.is_spoiled;
        }
        return a.name.localeCompare(b.name);
    });

    container.innerHTML = sortedItems.map(item => {
        const addedDate = new Date(item.added_date);
        const expiryDate = item.expiry_date ? new Date(item.expiry_date) : null;
        
        let statusClass = '';
        let statusText = '';
        let statusIcon = '';
        
        if (item.is_spoiled) {
            statusClass = 'spoiled';
            statusText = 'Spoiled';
            statusIcon = 'fas fa-exclamation-triangle status-spoiled';
        } else if (expiryDate) {
            const daysUntilExpiry = Math.ceil((expiryDate - new Date()) / (1000 * 60 * 60 * 24));
            if (daysUntilExpiry < 0) {
                statusClass = 'spoiled';
                statusText = 'Expired';
                statusIcon = 'fas fa-times-circle status-spoiled';
            } else if (daysUntilExpiry <= 3) {
                statusClass = 'expiring';
                statusText = 'Expires Soon';
                statusIcon = 'fas fa-clock status-expiring';
            } else {
                statusClass = '';
                statusText = 'Fresh';
                statusIcon = 'fas fa-check-circle status-fresh';
            }
        } else {
            statusClass = '';
            statusText = 'Fresh';
            statusIcon = 'fas fa-check-circle status-fresh';
        }

        return `
            <div class="inventory-item ${statusClass}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="item-name">${item.name}</div>
                        <div class="item-quantity">${item.quantity} ${item.unit}</div>
                        ${item.category ? `<div class="item-category category-${item.category}">${getCategoryEmoji(item.category)} ${item.category}</div>` : ''}
                        <div class="item-dates">
                            Added: ${addedDate.toLocaleDateString()}
                            ${expiryDate ? ` | Expires: ${expiryDate.toLocaleDateString()}` : ''}
                        </div>
                        <div class="item-status">
                            <i class="${statusIcon}"></i>
                            ${statusText}
                        </div>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteItem(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function getCategoryEmoji(category) {
    const emojis = {
        'meat': '🥩',
        'dairy': '🥛',
        'vegetables': '🥬',
        'fruits': '🍎',
        'seafood': '🐟',
        'frozen': '❄️',
        'other': '📦'
    };
    return emojis[category] || '📦';
}

function updateSensorDisplay() {
    // Update CO2 level (compact format)
    const co2Element = document.getElementById('co2-value');
    if (sensorData.co2_ppm !== undefined) {
        co2Element.textContent = `${sensorData.co2_ppm}`;
    } else {
        co2Element.textContent = '--';
    }

    // Update ammonia level (compact format)
    const ammoniaElement = document.getElementById('ammonia-value');
    if (sensorData.ammonia_ppm !== undefined) {
        ammoniaElement.textContent = `${sensorData.ammonia_ppm.toFixed(1)}`;
    } else {
        ammoniaElement.textContent = '--';
    }

    // Update H2S level (compact format)
    const h2sElement = document.getElementById('h2s-value');
    if (sensorData.h2s_ppm !== undefined) {
        h2sElement.textContent = `${sensorData.h2s_ppm.toFixed(1)}`;
    } else {
        h2sElement.textContent = '--';
    }

    // Update air quality (compact format)
    const airQualityElement = document.getElementById('air-quality-value');
    if (sensorData.air_quality !== undefined) {
        const airQuality = sensorData.air_quality.toUpperCase();
        airQualityElement.textContent = airQuality.length > 4 ? airQuality.substring(0, 4) : airQuality;
    } else {
        airQualityElement.textContent = '--';
    }

    // Update door status (compact format)
    const doorElement = document.getElementById('door-status');
    if (sensorData.door_open !== undefined) {
        doorElement.textContent = sensorData.door_open ? 'OPEN' : 'CLOSED';
    } else {
        doorElement.textContent = '--';
    }

    // Update spoiled count
    const spoiledCount = inventoryData.filter(item => item.is_spoiled).length;
    document.getElementById('spoiled-count').textContent = spoiledCount;

    // Update timestamp (compact format)
    const timestampElement = document.getElementById('sensor-timestamp');
    if (sensorData.timestamp) {
        const date = new Date(sensorData.timestamp);
        const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        timestampElement.textContent = `Updated: ${timeStr}`;
    } else {
        timestampElement.textContent = 'Updated: --';
    }
}

async function addItem() {
    const form = document.getElementById('quick-add-form');
    
    const itemData = {
        name: document.getElementById('item-name').value.trim(),
        quantity: parseInt(document.getElementById('item-quantity').value),
        unit: document.getElementById('item-unit').value,
        category: document.getElementById('item-category').value,
        notes: document.getElementById('item-notes').value,
        expiry_date: document.getElementById('item-expiry').value || null
    };

    if (!itemData.name || !itemData.quantity) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(itemData)
        });

        if (response.ok) {
            form.reset();
            closeAddItemModal();
            loadInventory();
            showToast('Item added successfully!', 'success');
        } else {
            throw new Error('Failed to add item');
        }
    } catch (error) {
        console.error('Error adding item:', error);
        showToast('Error adding item', 'danger');
    }
}

async function deleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
        const response = await fetch(`/api/inventory/${itemId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadInventory();
            showToast('Item deleted successfully!', 'success');
        } else {
            throw new Error('Failed to delete item');
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        showToast('Error deleting item', 'danger');
    }
}

async function checkSpoilage() {
    try {
        const response = await fetch('/api/check_spoilage');
        const result = await response.json();
        
        if (result.spoiled_items.length > 0) {
            showToast(`Warning: ${result.spoiled_items.length} items may be spoiled!`, 'warning');
        }
        
        if (result.door_open) {
            showToast('Door is open! Please close the fridge door.', 'warning');
        }
        
        loadInventory();
    } catch (error) {
        console.error('Error checking spoilage:', error);
    }
}

async function loadVolunteers() {
    try {
        const response = await fetch('/api/volunteers');
        if (response.ok) {
            volunteersData = await response.json();
            renderVolunteers();
        } else {
            console.error('Error loading volunteers:', response.statusText);
            showToast('Error loading volunteers', 'danger');
        }
    } catch (error) {
        console.error('Error loading volunteers:', error);
        showToast('Error loading volunteers', 'danger');
    }
}

function renderVolunteers() {
    const container = document.getElementById('volunteers-list');
    
    if (volunteersData.length === 0) {
        container.innerHTML = `
            <div class="empty-volunteers">
                <i class="fas fa-users"></i>
                <p>No volunteers</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = volunteersData.map(volunteer => {
        // Get initials for badge
        const initials = volunteer.name.split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
        
        return `
            <div class="volunteer-item">
                <div class="volunteer-badge">${initials}</div>
                <div class="volunteer-info">
                    <div class="volunteer-name">${volunteer.name}</div>
                    <div class="volunteer-email">${volunteer.email}</div>
                </div>
                <div class="volunteer-actions">
                    <button class="volunteer-action-btn edit" onclick="editVolunteer(${volunteer.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="volunteer-action-btn delete" onclick="deleteVolunteer(${volunteer.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Volunteer Modal Functions
function openAddVolunteerModal() {
    document.getElementById('volunteer-id').value = '';
    document.getElementById('volunteer-name').value = '';
    document.getElementById('volunteer-email').value = '';
    document.getElementById('volunteer-modal-title').innerHTML = '<i class="fas fa-user-plus"></i> Add Volunteer';
    document.getElementById('volunteer-submit-btn').innerHTML = '<i class="fas fa-save"></i> Save';
    document.getElementById('volunteerModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeVolunteerModal() {
    document.getElementById('volunteerModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    document.getElementById('volunteer-form').reset();
    document.getElementById('volunteer-id').value = '';
}

function editVolunteer(volunteerId) {
    const volunteer = volunteersData.find(v => v.id === volunteerId);
    if (!volunteer) return;
    
    document.getElementById('volunteer-id').value = volunteer.id;
    document.getElementById('volunteer-name').value = volunteer.name;
    document.getElementById('volunteer-email').value = volunteer.email;
    document.getElementById('volunteer-modal-title').innerHTML = '<i class="fas fa-user-edit"></i> Edit Volunteer';
    document.getElementById('volunteer-submit-btn').innerHTML = '<i class="fas fa-save"></i> Update';
    document.getElementById('volunteerModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

async function saveVolunteer() {
    const volunteerId = document.getElementById('volunteer-id').value;
    const name = document.getElementById('volunteer-name').value.trim();
    const email = document.getElementById('volunteer-email').value.trim().toLowerCase();
    
    if (!name || !email) {
        showToast('Please fill in all fields', 'warning');
        return;
    }
    
    try {
        const url = volunteerId ? `/api/volunteers/${volunteerId}` : '/api/volunteers';
        const method = volunteerId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email })
        });
        
        if (response.ok) {
            closeVolunteerModal();
            loadVolunteers();
            showToast(volunteerId ? 'Volunteer updated successfully!' : 'Volunteer added successfully!', 'success');
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to save volunteer', 'danger');
        }
    } catch (error) {
        console.error('Error saving volunteer:', error);
        showToast('Error saving volunteer', 'danger');
    }
}

async function deleteVolunteer(volunteerId) {
    const volunteer = volunteersData.find(v => v.id === volunteerId);
    if (!volunteer) return;
    
    if (!confirm(`Are you sure you want to delete ${volunteer.name}?`)) return;
    
    try {
        const response = await fetch(`/api/volunteers/${volunteerId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadVolunteers();
            showToast('Volunteer deleted successfully!', 'success');
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to delete volunteer', 'danger');
        }
    } catch (error) {
        console.error('Error deleting volunteer:', error);
        showToast('Error deleting volunteer', 'danger');
    }
}

function refreshData() {
    loadInventory();
    loadSensorData();
    checkSpoilage();
    loadVolunteers();
    showToast('Data refreshed!', 'success');
}

function showToast(message, type) {
    const toastDiv = document.createElement('div');
    toastDiv.className = `alert alert-${type} alert-dismissible fade show toast-notification`;
    toastDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(toastDiv);
    
    setTimeout(() => {
        if (toastDiv.parentNode) {
            toastDiv.remove();
        }
    }, 3000);
}

// Add haptic feedback for mobile
document.addEventListener('click', function(e) {
    if (e.target.matches('button, .btn')) {
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }
});
