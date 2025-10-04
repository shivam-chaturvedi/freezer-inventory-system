// Pi Display JavaScript - Optimized for touch screen
let inventoryData = [];
let sensorData = {};

// Initialize display
document.addEventListener('DOMContentLoaded', function() {
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    loadInventory();
    loadSensorData();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadInventory();
        loadSensorData();
    }, 30000);
    
    // Auto-refresh every 5 minutes for full data sync
    setInterval(() => {
        location.reload();
    }, 300000);
    
    // Setup virtual keyboard for touch inputs
    setupVirtualKeyboard();
});

function setupVirtualKeyboard() {
    // Add click listeners to all input fields
    const inputs = document.querySelectorAll('input[type="text"], input[type="number"], textarea');
    
    inputs.forEach(input => {
        // Prevent default keyboard on touch devices
        input.addEventListener('focus', function(e) {
            e.preventDefault();
            virtualKeyboard.show(this);
        });
        
        // Also show keyboard on click/touch
        input.addEventListener('click', function(e) {
            e.preventDefault();
            virtualKeyboard.show(this);
        });
        
        // Show keyboard on touch start
        input.addEventListener('touchstart', function(e) {
            e.preventDefault();
            virtualKeyboard.show(this);
        });
    });
}

function updateCurrentTime() {
    const now = new Date();
    // Use local time with proper formatting
    const timeString = now.toLocaleTimeString('en-US', {
        hour12: true,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeString;
}

async function loadInventory() {
    try {
        const response = await fetch('/api/inventory');
        inventoryData = await response.json();
        renderInventoryList();
    } catch (error) {
        console.error('Error loading inventory:', error);
        showAlert('Error loading inventory data', 'error');
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
                <h4>No items in freezer</h4>
                <p>Add items using the "Add Item" button above</p>
            </div>
        `;
        return;
    }

    // Sort items by status and name
    const sortedItems = inventoryData.sort((a, b) => {
        // Spoiled items first
        if (a.is_spoiled !== b.is_spoiled) {
            return b.is_spoiled - a.is_spoiled;
        }
        
        // Then by expiry date (expiring soon first)
        if (a.expiry_date && b.expiry_date) {
            const aExpiry = new Date(a.expiry_date);
            const bExpiry = new Date(b.expiry_date);
            const now = new Date();
            const aDaysLeft = Math.ceil((aExpiry - now) / (1000 * 60 * 60 * 24));
            const bDaysLeft = Math.ceil((bExpiry - now) / (1000 * 60 * 60 * 24));
            
            if (aDaysLeft <= 3 && bDaysLeft > 3) return -1;
            if (aDaysLeft > 3 && bDaysLeft <= 3) return 1;
        }
        
        // Finally by name
        return a.name.localeCompare(b.name);
    });

    container.innerHTML = sortedItems.map(item => {
        const addedDate = new Date(item.added_date);
        const expiryDate = item.expiry_date ? new Date(item.expiry_date) : null;
        
        // Determine item status and styling
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
                // Only show as expired if it's been expired for more than 1 day
                const daysOverdue = Math.abs(daysUntilExpiry);
                if (daysOverdue > 1) {
                    statusClass = 'spoiled';
                    statusText = 'Expired';
                    statusIcon = 'fas fa-times-circle status-spoiled';
                } else {
                    statusClass = 'expiring';
                    statusText = 'Expires Today';
                    statusIcon = 'fas fa-clock status-expiring';
                }
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
            <div class="inventory-item ${statusClass}" onclick="editItem(${item.id})">
                <div class="item-header">
                    <h5 class="item-name">${item.name}</h5>
                    <div class="item-quantity">${item.quantity} ${item.unit}</div>
                </div>
                <div class="item-details">
                    <div class="item-category category-${item.category || 'other'}">
                        ${getCategoryEmoji(item.category)} ${item.category || 'Other'}
                    </div>
                    <div class="item-status">
                        <i class="${statusIcon}"></i>
                        ${statusText}
                    </div>
                </div>
                <div class="item-dates">
                    Added: ${addedDate.toLocaleDateString()}
                    ${expiryDate ? ` | Expires: ${expiryDate.toLocaleDateString()}` : ''}
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
    const co2Card = document.getElementById('co2-card');
    if (sensorData.co2_ppm !== undefined) {
        co2Element.textContent = `${sensorData.co2_ppm} PPM`;
        
        // Color code based on CO2 level
        co2Card.className = 'sensor-card';
        if (sensorData.co2_ppm > 1000) {
            co2Card.classList.add('danger');
        } else if (sensorData.co2_ppm > 500) {
            co2Card.classList.add('warning');
        } else {
            co2Card.classList.add('success');
        }
    } else {
        co2Element.textContent = '-- PPM';
    }

    // Update ammonia level
    const ammoniaElement = document.getElementById('ammonia-value');
    const ammoniaCard = document.getElementById('ammonia-card');
    if (sensorData.ammonia_ppm !== undefined) {
        ammoniaElement.textContent = `${sensorData.ammonia_ppm.toFixed(2)} PPM`;
        
        // Color code based on ammonia level
        ammoniaCard.className = 'sensor-card';
        if (sensorData.ammonia_ppm > 25) {
            ammoniaCard.classList.add('danger');
        } else if (sensorData.ammonia_ppm > 10) {
            ammoniaCard.classList.add('warning');
        } else {
            ammoniaCard.classList.add('success');
        }
    } else {
        ammoniaElement.textContent = '-- PPM';
    }

    // Update H2S level
    const h2sElement = document.getElementById('h2s-value');
    const h2sCard = document.getElementById('h2s-card');
    if (sensorData.h2s_ppm !== undefined) {
        h2sElement.textContent = `${sensorData.h2s_ppm.toFixed(2)} PPM`;
        
        // Color code based on H2S level
        h2sCard.className = 'sensor-card';
        if (sensorData.h2s_ppm > 10) {
            h2sCard.classList.add('danger');
        } else if (sensorData.h2s_ppm > 5) {
            h2sCard.classList.add('warning');
        } else {
            h2sCard.classList.add('success');
        }
    } else {
        h2sElement.textContent = '-- PPM';
    }

    // Update air quality
    const airQualityElement = document.getElementById('air-quality-value');
    const airQualityCard = document.getElementById('air-quality-card');
    if (sensorData.air_quality !== undefined) {
        airQualityElement.textContent = sensorData.air_quality.toUpperCase();
        
        // Color code based on air quality
        airQualityCard.className = 'sensor-card';
        if (sensorData.air_quality === 'poor') {
            airQualityCard.classList.add('danger');
        } else if (sensorData.air_quality === 'moderate') {
            airQualityCard.classList.add('warning');
        } else if (sensorData.air_quality === 'good') {
            airQualityCard.classList.add('success');
        }
    } else {
        airQualityElement.textContent = '--';
    }

    // Update spoiled count
    const spoiledCount = inventoryData.filter(item => item.is_spoiled).length;
    const spoiledElement = document.getElementById('spoiled-count');
    const alertCard = document.getElementById('spoilage-alert');
    
    spoiledElement.textContent = spoiledCount;
    
    if (spoiledCount > 0) {
        alertCard.classList.add('alert-pulse');
    } else {
        alertCard.classList.remove('alert-pulse');
    }
}

function showAddItemModal() {
    const modal = new bootstrap.Modal(document.getElementById('addItemModal'));
    modal.show();
    
    // Setup virtual keyboard for modal inputs
    setTimeout(() => {
        setupVirtualKeyboard();
        
        // Show virtual keyboard for the first input
        const nameInput = document.getElementById('item-name');
        if (nameInput) {
            virtualKeyboard.show(nameInput);
        }
    }, 500);
}

async function addItem() {
    const form = document.getElementById('add-item-form');
    
    const itemData = {
        name: document.getElementById('item-name').value.trim(),
        quantity: parseInt(document.getElementById('item-quantity').value),
        unit: document.getElementById('item-unit').value,
        category: document.getElementById('item-category').value,
        notes: document.getElementById('item-notes').value,
        expiry_date: document.getElementById('item-expiry').value || null
    };

    // Validate required fields
    if (!itemData.name || !itemData.quantity) {
        showAlert('Please fill in all required fields', 'error');
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
            const modal = bootstrap.Modal.getInstance(document.getElementById('addItemModal'));
            modal.hide();
            form.reset();
            loadInventory();
            showAlert('Item added successfully!', 'success');
        } else {
            throw new Error('Failed to add item');
        }
    } catch (error) {
        console.error('Error adding item:', error);
        showAlert('Error adding item', 'error');
    }
}

function editItem(itemId) {
    const item = inventoryData.find(i => i.id === itemId);
    if (!item) return;

    // Simple quantity edit for touch interface
    const newQuantity = prompt(`Edit quantity for ${item.name}:`, item.quantity);
    if (newQuantity !== null && !isNaN(newQuantity) && newQuantity > 0) {
        updateItemQuantity(itemId, parseInt(newQuantity));
    }
}

async function updateItemQuantity(itemId, newQuantity) {
    const item = inventoryData.find(i => i.id === itemId);
    if (!item) return;

    try {
        const response = await fetch(`/api/inventory/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...item,
                quantity: newQuantity
            })
        });

        if (response.ok) {
            loadInventory();
            showAlert('Item updated successfully!', 'success');
        } else {
            throw new Error('Failed to update item');
        }
    } catch (error) {
        console.error('Error updating item:', error);
        showAlert('Error updating item', 'error');
    }
}

function refreshData() {
    loadInventory();
    loadSensorData();
    showAlert('Data refreshed!', 'info');
}

function showAlert(message, type) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

async function showQRCode() {
    const modal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
    modal.show();
    
    try {
        const response = await fetch('/api/qr-code');
        const data = await response.json();
        
        const container = document.getElementById('qr-code-container');
        container.innerHTML = `
            <img src="${data.qr_code}" alt="QR Code" class="img-fluid" style="max-width: 200px;">
            <p class="mt-2"><strong>Mobile URL:</strong><br>
            <small class="text-muted">${data.mobile_url}</small></p>
        `;
    } catch (error) {
        console.error('Error generating QR code:', error);
        const container = document.getElementById('qr-code-container');
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Error generating QR code
            </div>
        `;
    }
}

// Add haptic feedback for touch interactions
function addHapticFeedback() {
    if ('vibrate' in navigator) {
        navigator.vibrate(50); // 50ms vibration
    }
}

// Add haptic feedback to buttons and items
document.addEventListener('click', function(e) {
    if (e.target.matches('button, .btn, .inventory-item')) {
        addHapticFeedback();
    }
});

// Prevent context menu on long press
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

// Handle touch events for better responsiveness
document.addEventListener('touchstart', function(e) {
    if (e.target.closest('.inventory-item')) {
        e.target.closest('.inventory-item').style.transform = 'scale(0.98)';
    }
});

document.addEventListener('touchend', function(e) {
    if (e.target.closest('.inventory-item')) {
        e.target.closest('.inventory-item').style.transform = '';
    }
});
