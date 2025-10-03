// Dashboard JavaScript
let inventoryData = [];
let sensorData = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    loadInventory();
    loadSensorData();
    checkSpoilage();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadInventory();
        loadSensorData();
    }, 30000);
});

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('current-time').textContent = timeString;
}

async function loadInventory() {
    try {
        const response = await fetch('/api/inventory');
        inventoryData = await response.json();
        renderInventoryTable();
    } catch (error) {
        console.error('Error loading inventory:', error);
        showAlert('Error loading inventory data', 'danger');
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

function updateSensorDisplay() {
    // Update CO2 level
    const co2Element = document.getElementById('co2-value');
    const co2Card = document.getElementById('co2-card');
    if (sensorData.co2_ppm !== undefined) {
        co2Element.textContent = `${sensorData.co2_ppm} PPM`;
        
        // Color code based on CO2 level
        co2Card.className = 'card text-white';
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
        ammoniaCard.className = 'card text-white';
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
        h2sCard.className = 'card text-white';
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
        airQualityCard.className = 'card text-white';
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

    // Update door status
    const doorElement = document.getElementById('door-status');
    const doorCard = document.getElementById('door-card');
    if (sensorData.door_open !== undefined) {
        doorElement.textContent = sensorData.door_open ? 'OPEN' : 'CLOSED';
        doorCard.className = 'card text-white';
        if (sensorData.door_open) {
            doorCard.classList.add('danger');
        } else {
            doorCard.classList.add('success');
        }
    } else {
        doorElement.textContent = '--';
    }
}

function renderInventoryTable() {
    const tbody = document.getElementById('inventory-tbody');
    tbody.innerHTML = '';

    if (inventoryData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-box-open fa-2x mb-2"></i><br>
                    No items in inventory
                </td>
            </tr>
        `;
        return;
    }

    inventoryData.forEach(item => {
        const row = document.createElement('tr');
        
        // Determine item status
        let statusClass = 'fresh-item';
        let statusText = 'Fresh';
        let statusIcon = 'status-fresh';
        
        if (item.is_spoiled) {
            statusClass = 'spoiled-item';
            statusText = 'Spoiled';
            statusIcon = 'status-spoiled';
        } else if (item.expiry_date) {
            const expiryDate = new Date(item.expiry_date);
            const daysUntilExpiry = Math.ceil((expiryDate - new Date()) / (1000 * 60 * 60 * 24));
            if (daysUntilExpiry <= 0) {
                statusClass = 'spoiled-item';
                statusText = 'Expired';
                statusIcon = 'status-spoiled';
            } else if (daysUntilExpiry <= 3) {
                statusClass = 'expiring-soon';
                statusText = 'Expiring Soon';
                statusIcon = 'status-expiring';
            }
        }

        row.className = statusClass;
        row.innerHTML = `
            <td>
                <strong>${item.name}</strong>
                ${item.notes ? `<br><small class="text-muted">${item.notes}</small>` : ''}
            </td>
            <td>${item.quantity} ${item.unit}</td>
            <td>
                <span class="badge bg-secondary">${item.category || 'Uncategorized'}</span>
            </td>
            <td>${new Date(item.added_date).toLocaleDateString()}</td>
            <td>${item.expiry_date ? new Date(item.expiry_date).toLocaleDateString() : 'N/A'}</td>
            <td>
                <span class="${statusIcon}"></span>
                ${statusText}
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="editItem(${item.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteItem(${item.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });

    // Update spoiled count
    const spoiledCount = inventoryData.filter(item => item.is_spoiled).length;
    document.getElementById('spoiled-count').textContent = spoiledCount;
}

function showAddItemModal() {
    const modal = new bootstrap.Modal(document.getElementById('addItemModal'));
    modal.show();
}

async function addItem() {
    const form = document.getElementById('add-item-form');
    const formData = new FormData(form);
    
    const itemData = {
        name: document.getElementById('item-name').value,
        quantity: parseInt(document.getElementById('item-quantity').value),
        unit: document.getElementById('item-unit').value,
        category: document.getElementById('item-category').value,
        notes: document.getElementById('item-notes').value,
        expiry_date: document.getElementById('item-expiry').value || null
    };

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
        showAlert('Error adding item', 'danger');
    }
}

async function editItem(itemId) {
    const item = inventoryData.find(i => i.id === itemId);
    if (!item) return;

    // For now, just show an alert. In a real implementation, you'd show an edit modal
    const newQuantity = prompt(`Edit quantity for ${item.name}:`, item.quantity);
    if (newQuantity !== null && !isNaN(newQuantity)) {
        try {
            const response = await fetch(`/api/inventory/${itemId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...item,
                    quantity: parseInt(newQuantity)
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
            showAlert('Error updating item', 'danger');
        }
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
            showAlert('Item deleted successfully!', 'success');
        } else {
            throw new Error('Failed to delete item');
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        showAlert('Error deleting item', 'danger');
    }
}

async function checkSpoilage() {
    try {
        const response = await fetch('/api/check_spoilage');
        const result = await response.json();
        
        if (result.spoiled_items.length > 0) {
            showAlert(`Spoilage detected! ${result.spoiled_items.length} items may be spoiled.`, 'warning');
        }
        
        if (result.temperature_warning) {
            showAlert('Temperature warning! Freezer temperature is above safe levels.', 'danger');
        }
        
        if (result.door_open) {
            showAlert('Door is open! Please close the freezer door.', 'warning');
        }
        
        loadInventory(); // Refresh to show updated spoilage status
    } catch (error) {
        console.error('Error checking spoilage:', error);
        showAlert('Error checking spoilage', 'danger');
    }
}

function refreshData() {
    loadInventory();
    loadSensorData();
    checkSpoilage();
    showAlert('Data refreshed!', 'info');
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

