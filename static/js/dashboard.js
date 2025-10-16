// Dashboard JavaScript
let inventoryData = [];
let sensorData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadInventory();
    loadSensorData();
    checkSpoilage();
    
    // Setup form submission
    document.getElementById('quick-add-form').addEventListener('submit', function(e) {
        e.preventDefault();
        addItem();
    });
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadInventory();
        loadSensorData();
    }, 30000);
});

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
    // Update CO2 level
    const co2Element = document.getElementById('co2-value');
    if (sensorData.co2_ppm !== undefined) {
        co2Element.textContent = `${sensorData.co2_ppm} PPM`;
    } else {
        co2Element.textContent = '-- PPM';
    }

    // Update ammonia level
    const ammoniaElement = document.getElementById('ammonia-value');
    if (sensorData.ammonia_ppm !== undefined) {
        ammoniaElement.textContent = `${sensorData.ammonia_ppm.toFixed(2)} PPM`;
    } else {
        ammoniaElement.textContent = '-- PPM';
    }

    // Update H2S level
    const h2sElement = document.getElementById('h2s-value');
    if (sensorData.h2s_ppm !== undefined) {
        h2sElement.textContent = `${sensorData.h2s_ppm.toFixed(2)} PPM`;
    } else {
        h2sElement.textContent = '-- PPM';
    }

    // Update air quality
    const airQualityElement = document.getElementById('air-quality-value');
    if (sensorData.air_quality !== undefined) {
        airQualityElement.textContent = sensorData.air_quality.toUpperCase();
    } else {
        airQualityElement.textContent = '--';
    }

    // Update door status
    const doorElement = document.getElementById('door-status');
    if (sensorData.door_open !== undefined) {
        doorElement.textContent = sensorData.door_open ? 'OPEN' : 'CLOSED';
    } else {
        doorElement.textContent = '--';
    }

    // Update spoiled count
    const spoiledCount = inventoryData.filter(item => item.is_spoiled).length;
    document.getElementById('spoiled-count').textContent = spoiledCount;

    // Update timestamp
    const timestampElement = document.getElementById('sensor-timestamp');
    if (sensorData.timestamp) {
        const date = new Date(sensorData.timestamp);
        timestampElement.textContent = `Last updated: ${date.toLocaleString()}`;
    } else {
        timestampElement.textContent = 'Last updated: --';
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

function refreshData() {
    loadInventory();
    loadSensorData();
    checkSpoilage();
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
