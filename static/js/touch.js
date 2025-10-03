// Touch Interface JavaScript
let inventoryData = [];
let sensorData = {};
let selectedCategory = '';

// Initialize touch interface
document.addEventListener('DOMContentLoaded', function() {
    loadInventory();
    loadSensorData();
    
    // Set up category button handlers
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            selectedCategory = this.dataset.category;
            document.getElementById('touch-category').value = selectedCategory;
        });
    });
    
    // Set up form submission
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
        showMessage('Error loading inventory data', 'error');
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
    // Update temperature
    const tempElement = document.getElementById('touch-temp');
    const tempCard = document.getElementById('touch-temp-card');
    if (sensorData.temperature !== undefined) {
        tempElement.textContent = `${sensorData.temperature.toFixed(1)}°C`;
        
        // Color code based on temperature
        tempCard.className = 'card text-center sensor-card';
        if (sensorData.temperature > 4) {
            tempCard.classList.add('danger');
        } else if (sensorData.temperature > 2) {
            tempCard.classList.add('warning');
        } else {
            tempCard.classList.add('success');
        }
    } else {
        tempElement.textContent = '--°C';
    }

    // Update humidity
    const humidityElement = document.getElementById('touch-humidity');
    const humidityCard = document.getElementById('touch-humidity-card');
    if (sensorData.humidity !== undefined) {
        humidityElement.textContent = `${sensorData.humidity.toFixed(1)}%`;
        
        // Color code based on humidity
        humidityCard.className = 'card text-center sensor-card';
        if (sensorData.humidity > 80) {
            humidityCard.classList.add('warning');
        } else if (sensorData.humidity < 30) {
            humidityCard.classList.add('danger');
        } else {
            humidityCard.classList.add('success');
        }
    } else {
        humidityElement.textContent = '--%';
    }

    // Update door status
    const doorElement = document.getElementById('touch-door');
    const doorCard = document.getElementById('touch-door-card');
    if (sensorData.door_open !== undefined) {
        doorElement.textContent = sensorData.door_open ? 'OPEN' : 'CLOSED';
        doorCard.className = 'card text-center sensor-card';
        if (sensorData.door_open) {
            doorCard.classList.add('danger');
        } else {
            doorCard.classList.add('success');
        }
    } else {
        doorElement.textContent = '--';
    }
}

function renderInventoryList() {
    const container = document.getElementById('touch-inventory-list');
    
    if (inventoryData.length === 0) {
        container.innerHTML = `
            <div class="empty-inventory">
                <i class="fas fa-box-open"></i>
                <h5>No items in freezer</h5>
                <p>Add items using the form on the left</p>
            </div>
        `;
        return;
    }

    // Sort items by category and name
    const sortedItems = inventoryData.sort((a, b) => {
        if (a.category !== b.category) {
            return (a.category || '').localeCompare(b.category || '');
        }
        return a.name.localeCompare(b.name);
    });

    container.innerHTML = sortedItems.map(item => {
        const addedDate = new Date(item.added_date);
        const expiryDate = item.expiry_date ? new Date(item.expiry_date) : null;
        
        // Determine if item is expiring soon or spoiled
        let statusClass = '';
        let statusText = '';
        
        if (item.is_spoiled) {
            statusClass = 'text-danger';
            statusText = 'Spoiled';
        } else if (expiryDate) {
            const daysUntilExpiry = Math.ceil((expiryDate - new Date()) / (1000 * 60 * 60 * 24));
            if (daysUntilExpiry <= 0) {
                statusClass = 'text-danger';
                statusText = 'Expired';
            } else if (daysUntilExpiry <= 3) {
                statusClass = 'text-warning';
                statusText = 'Expires Soon';
            }
        }

        return `
            <div class="inventory-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="item-name">${item.name}</div>
                        <div class="item-details">
                            ${item.quantity} ${item.unit}
                            ${item.category ? `<span class="item-category category-${item.category}">${item.category}</span>` : ''}
                        </div>
                        <div class="item-details">
                            Added: ${addedDate.toLocaleDateString()}
                            ${expiryDate ? ` | Expires: ${expiryDate.toLocaleDateString()}` : ''}
                            ${statusText ? `<span class="${statusClass}"> | ${statusText}</span>` : ''}
                        </div>
                    </div>
                    <div class="text-end">
                        <button class="btn btn-sm btn-outline-danger" onclick="removeItem(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function addItem() {
    const form = document.getElementById('quick-add-form');
    const formData = new FormData(form);
    
    const itemData = {
        name: document.getElementById('touch-item-name').value.trim(),
        quantity: parseInt(document.getElementById('touch-quantity').value),
        unit: document.getElementById('touch-unit').value,
        category: selectedCategory || '',
        notes: '',
        expiry_date: document.getElementById('touch-expiry').value || null
    };

    // Validate required fields
    if (!itemData.name || !itemData.quantity) {
        showMessage('Please fill in all required fields', 'error');
        return;
    }

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="loading-spinner"></span> Adding...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(itemData)
        });

        if (response.ok) {
            // Show success animation
            form.classList.add('success-animation');
            setTimeout(() => form.classList.remove('success-animation'), 600);
            
            // Show success modal
            const modal = new bootstrap.Modal(document.getElementById('successModal'));
            modal.show();
            
            // Reset form
            form.reset();
            document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
            selectedCategory = '';
            document.getElementById('touch-category').value = '';
            
            // Reload inventory
            loadInventory();
        } else {
            throw new Error('Failed to add item');
        }
    } catch (error) {
        console.error('Error adding item:', error);
        showMessage('Error adding item. Please try again.', 'error');
    } finally {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function removeItem(itemId) {
    if (!confirm('Remove this item from the freezer?')) return;

    try {
        const response = await fetch(`/api/inventory/${itemId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadInventory();
            showMessage('Item removed successfully!', 'success');
        } else {
            throw new Error('Failed to remove item');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showMessage('Error removing item', 'error');
    }
}

function viewInventory() {
    // Scroll to inventory section
    document.getElementById('touch-inventory-list').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

function showMessage(message, type) {
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

// Add haptic feedback for touch interactions
function addHapticFeedback() {
    if ('vibrate' in navigator) {
        navigator.vibrate(50); // 50ms vibration
    }
}

// Add haptic feedback to buttons
document.addEventListener('click', function(e) {
    if (e.target.matches('button, .btn, .category-btn')) {
        addHapticFeedback();
    }
});

