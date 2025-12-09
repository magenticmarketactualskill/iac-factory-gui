/**
 * IaC Factory GUI - Main Application
 * Lightweight reactive UI without external frameworks
 */

// Application State
const state = {
    currentDesign: null,
    components: [],
    connections: [],
    selectedItem: null,
    selectedType: null, // 'component' or 'connection'
    connectionMode: false,
    connectionSource: null,
    unsavedChanges: false,
    nextComponentId: 1,
    nextConnectionId: 1
};

// API Base URL
const API_BASE = '/api';

// Utility Functions
function generateId() {
    return `id_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function showError(message) {
    alert(`Error: ${message}`);
}

function showSuccess(message) {
    console.log(`Success: ${message}`);
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }
        
        return await response.json();
    } catch (error) {
        showError(error.message);
        throw error;
    }
}

async function createDesign(name) {
    const design = await apiCall('/designs', {
        method: 'POST',
        body: JSON.stringify({ name })
    });
    state.currentDesign = design;
    state.components = design.components || [];
    state.connections = design.connections || [];
    return design;
}

async function loadDesign(designId) {
    const design = await apiCall(`/designs/${designId}`);
    state.currentDesign = design;
    state.components = design.components || [];
    state.connections = design.connections || [];
    renderCanvas();
    return design;
}

async function saveDesign() {
    if (!state.currentDesign) return;
    
    const designData = {
        ...state.currentDesign,
        components: state.components,
        connections: state.connections
    };
    
    await apiCall(`/designs/${state.currentDesign.design_id}`, {
        method: 'PUT',
        body: JSON.stringify(designData)
    });
    
    state.unsavedChanges = false;
    updateUnsavedIndicator();
    showSuccess('Design saved');
}

async function generateCode(format) {
    if (!state.currentDesign) {
        showError('No design loaded');
        return;
    }
    
    const result = await apiCall(`/designs/${state.currentDesign.design_id}/generate/${format}`, {
        method: 'POST'
    });
    
    return result.code;
}

// Canvas Functions
function getCanvas() {
    return document.getElementById('canvas');
}

function getComponentsGroup() {
    return document.getElementById('components');
}

function getConnectionsGroup() {
    return document.getElementById('connections');
}

function renderCanvas() {
    const componentsGroup = getComponentsGroup();
    const connectionsGroup = getConnectionsGroup();
    
    // Clear existing
    componentsGroup.innerHTML = '';
    connectionsGroup.innerHTML = '';
    
    // Render components
    state.components.forEach((comp, index) => {
        renderComponent(comp, index);
    });
    
    // Render connections
    state.connections.forEach((conn, index) => {
        renderConnection(conn, index);
    });
}

function renderComponent(comp, index) {
    const componentsGroup = getComponentsGroup();
    
    // Set default position if not set
    if (!comp.x) comp.x = 100 + (index % 5) * 150;
    if (!comp.y) comp.y = 100 + Math.floor(index / 5) * 100;
    
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'component');
    g.setAttribute('data-index', index);
    g.setAttribute('transform', `translate(${comp.x}, ${comp.y})`);
    
    // Rectangle
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('width', '120');
    rect.setAttribute('height', '60');
    rect.setAttribute('rx', '4');
    
    // Text
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', '60');
    text.setAttribute('y', '25');
    text.setAttribute('text-anchor', 'middle');
    text.textContent = comp.name;
    
    const typeText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    typeText.setAttribute('x', '60');
    typeText.setAttribute('y', '40');
    typeText.setAttribute('text-anchor', 'middle');
    typeText.setAttribute('font-size', '10');
    typeText.setAttribute('fill', '#666');
    typeText.textContent = comp.type;
    
    g.appendChild(rect);
    g.appendChild(text);
    g.appendChild(typeText);
    
    // Event listeners
    g.addEventListener('click', (e) => {
        e.stopPropagation();
        if (state.connectionMode) {
            handleConnectionClick(index);
        } else {
            selectComponent(index);
        }
    });
    
    // Drag functionality
    let isDragging = false;
    let startX, startY;
    
    g.addEventListener('mousedown', (e) => {
        if (state.connectionMode) return;
        isDragging = true;
        startX = e.clientX - comp.x;
        startY = e.clientY - comp.y;
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        comp.x = e.clientX - startX;
        comp.y = e.clientY - startY;
        g.setAttribute('transform', `translate(${comp.x}, ${comp.y})`);
        renderCanvas(); // Re-render to update connections
        markUnsaved();
    });
    
    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
    
    componentsGroup.appendChild(g);
}

function renderConnection(conn, index) {
    const connectionsGroup = getConnectionsGroup();
    
    // Find source and destination components
    const sourceComp = state.components.find(c => c.name === conn.source);
    const destComp = state.components.find(c => c.name === conn.destination);
    
    if (!sourceComp || !destComp) return;
    
    // Calculate positions (center of components)
    const x1 = (sourceComp.x || 0) + 60;
    const y1 = (sourceComp.y || 0) + 30;
    const x2 = (destComp.x || 0) + 60;
    const y2 = (destComp.y || 0) + 30;
    
    // Create path
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const d = `M ${x1} ${y1} L ${x2} ${y2}`;
    path.setAttribute('d', d);
    path.setAttribute('class', 'connection');
    path.setAttribute('data-index', index);
    
    path.addEventListener('click', (e) => {
        e.stopPropagation();
        selectConnection(index);
    });
    
    connectionsGroup.appendChild(path);
}

function selectComponent(index) {
    state.selectedItem = index;
    state.selectedType = 'component';
    
    // Update visual selection
    document.querySelectorAll('.component').forEach((el, i) => {
        el.classList.toggle('selected', i === index);
    });
    document.querySelectorAll('.connection').forEach(el => {
        el.classList.remove('selected');
    });
    
    showPropertiesPanel();
}

function selectConnection(index) {
    state.selectedItem = index;
    state.selectedType = 'connection';
    
    // Update visual selection
    document.querySelectorAll('.connection').forEach((el, i) => {
        el.classList.toggle('selected', i === index);
    });
    document.querySelectorAll('.component').forEach(el => {
        el.classList.remove('selected');
    });
    
    showPropertiesPanel();
}

function handleConnectionClick(componentIndex) {
    if (!state.connectionSource) {
        // First click - set source
        state.connectionSource = componentIndex;
        showSuccess('Source selected. Click destination component.');
    } else {
        // Second click - create connection
        const sourceComp = state.components[state.connectionSource];
        const destComp = state.components[componentIndex];
        
        if (state.connectionSource === componentIndex) {
            showError('Cannot connect component to itself');
            state.connectionSource = null;
            return;
        }
        
        const connection = {
            source: sourceComp.name,
            destination: destComp.name,
            label: `${sourceComp.name} to ${destComp.name}`,
            technology: ''
        };
        
        state.connections.push(connection);
        state.connectionSource = null;
        toggleConnectionMode();
        renderCanvas();
        markUnsaved();
    }
}

function toggleConnectionMode() {
    state.connectionMode = !state.connectionMode;
    state.connectionSource = null;
    
    const indicator = document.getElementById('connection-mode-indicator');
    indicator.classList.toggle('hidden', !state.connectionMode);
    
    if (!state.connectionMode) {
        renderCanvas();
    }
}

// Properties Panel
function showPropertiesPanel() {
    const panel = document.getElementById('properties-content');
    
    if (state.selectedType === 'component') {
        const comp = state.components[state.selectedItem];
        panel.innerHTML = `
            <div class="form-group">
                <label>Name</label>
                <input type="text" id="prop-name" value="${comp.name}">
            </div>
            <div class="form-group">
                <label>Domain Type</label>
                <select id="prop-domain">
                    <option value="Public" ${comp.domain_type === 'Public' ? 'selected' : ''}>Public</option>
                    <option value="Web" ${comp.domain_type === 'Web' ? 'selected' : ''}>Web</option>
                    <option value="Application" ${comp.domain_type === 'Application' ? 'selected' : ''}>Application</option>
                    <option value="Data" ${comp.domain_type === 'Data' ? 'selected' : ''}>Data</option>
                </select>
            </div>
            <div class="form-group">
                <label>Technology</label>
                <input type="text" id="prop-technology" value="${comp.technology || ''}">
            </div>
            <button class="btn" onclick="updateComponentProperties()">Update</button>
            <button class="btn" style="background: #e74c3c; margin-top: 0.5rem;" onclick="deleteComponent()">Delete</button>
        `;
    } else if (state.selectedType === 'connection') {
        const conn = state.connections[state.selectedItem];
        panel.innerHTML = `
            <div class="form-group">
                <label>Source</label>
                <input type="text" value="${conn.source}" disabled>
            </div>
            <div class="form-group">
                <label>Destination</label>
                <input type="text" value="${conn.destination}" disabled>
            </div>
            <div class="form-group">
                <label>Label</label>
                <input type="text" id="prop-label" value="${conn.label || ''}">
            </div>
            <div class="form-group">
                <label>Technology</label>
                <input type="text" id="prop-conn-technology" value="${conn.technology || ''}">
            </div>
            <button class="btn" onclick="updateConnectionProperties()">Update</button>
            <button class="btn" style="background: #e74c3c; margin-top: 0.5rem;" onclick="deleteConnection()">Delete</button>
        `;
    }
}

function updateComponentProperties() {
    const comp = state.components[state.selectedItem];
    comp.name = document.getElementById('prop-name').value;
    comp.domain_type = document.getElementById('prop-domain').value;
    comp.technology = document.getElementById('prop-technology').value;
    
    renderCanvas();
    markUnsaved();
    showSuccess('Component updated');
}

function updateConnectionProperties() {
    const conn = state.connections[state.selectedItem];
    conn.label = document.getElementById('prop-label').value;
    conn.technology = document.getElementById('prop-conn-technology').value;
    
    renderCanvas();
    markUnsaved();
    showSuccess('Connection updated');
}

function deleteComponent() {
    if (!confirm('Delete this component?')) return;
    
    const comp = state.components[state.selectedItem];
    
    // Remove connections involving this component
    state.connections = state.connections.filter(
        c => c.source !== comp.name && c.destination !== comp.name
    );
    
    // Remove component
    state.components.splice(state.selectedItem, 1);
    
    state.selectedItem = null;
    state.selectedType = null;
    
    document.getElementById('properties-content').innerHTML = 
        '<p class="placeholder">Select a component or connection to edit properties</p>';
    
    renderCanvas();
    markUnsaved();
}

function deleteConnection() {
    if (!confirm('Delete this connection?')) return;
    
    state.connections.splice(state.selectedItem, 1);
    
    state.selectedItem = null;
    state.selectedType = null;
    
    document.getElementById('properties-content').innerHTML = 
        '<p class="placeholder">Select a component or connection to edit properties</p>';
    
    renderCanvas();
    markUnsaved();
}

// Drag and Drop from Palette
function setupPalette() {
    const items = document.querySelectorAll('.component-item');
    
    items.forEach(item => {
        item.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('componentType', item.dataset.type);
        });
    });
    
    const canvas = getCanvas();
    
    canvas.addEventListener('dragover', (e) => {
        e.preventDefault();
    });
    
    canvas.addEventListener('drop', (e) => {
        e.preventDefault();
        
        const componentType = e.dataTransfer.getData('componentType');
        if (!componentType) return;
        
        // Get drop position relative to canvas
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        addComponent(componentType, x, y);
    });
}

function addComponent(type, x, y) {
    const component = {
        name: `${type} ${state.nextComponentId++}`,
        type: type,
        domain_type: getDefaultDomain(type),
        technology: getDefaultTechnology(type),
        x: x,
        y: y
    };
    
    state.components.push(component);
    renderCanvas();
    markUnsaved();
}

function getDefaultDomain(type) {
    const defaults = {
        'Gateway': 'Public',
        'Container': 'Application',
        'Lambda': 'Application',
        'Cache': 'Data',
        'Rdms': 'Data',
        'Archive': 'Data'
    };
    return defaults[type] || 'Application';
}

function getDefaultTechnology(type) {
    const defaults = {
        'Gateway': 'API Gateway',
        'Container': 'Docker',
        'Lambda': 'AWS Lambda',
        'Cache': 'Redis',
        'Rdms': 'PostgreSQL',
        'Archive': 'S3 Glacier'
    };
    return defaults[type] || '';
}

// Code Viewer Modal
function showCodeModal() {
    document.getElementById('code-modal').classList.remove('hidden');
}

function hideCodeModal() {
    document.getElementById('code-modal').classList.add('hidden');
}

async function generateAndShowCode() {
    if (!state.currentDesign) {
        // Create a temporary design
        await createDesign('Untitled Design');
        await saveDesign();
    }
    
    showCodeModal();
    
    // Generate all formats
    try {
        const mermaid = await generateCode('mermaid');
        document.getElementById('mermaid-code').textContent = mermaid;
        
        const pulumi = await generateCode('pulumi');
        document.getElementById('pulumi-code').textContent = pulumi;
        
        const cdk = await generateCode('cdk');
        document.getElementById('cdk-code').textContent = cdk;
    } catch (error) {
        showError('Failed to generate code');
    }
}

// Tab Switching
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update panes
            tabPanes.forEach(pane => {
                pane.classList.toggle('hidden', pane.id !== `${tabName}-tab`);
            });
        });
    });
}

// Copy to Clipboard
function setupCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const codeElement = btn.nextElementSibling.querySelector('code');
            navigator.clipboard.writeText(codeElement.textContent);
            showSuccess('Copied to clipboard');
        });
    });
}

// Unsaved Changes
function markUnsaved() {
    state.unsavedChanges = true;
    updateUnsavedIndicator();
}

function updateUnsavedIndicator() {
    const header = document.querySelector('.header h1');
    let indicator = header.querySelector('.unsaved-indicator');
    
    if (state.unsavedChanges && !indicator) {
        indicator = document.createElement('span');
        indicator.className = 'unsaved-indicator';
        indicator.textContent = '●';
        header.appendChild(indicator);
    } else if (!state.unsavedChanges && indicator) {
        indicator.remove();
    }
}

// Initialize Application
async function init() {
    console.log('Initializing IaC Factory GUI...');
    
    // Setup event listeners
    document.getElementById('save-btn').addEventListener('click', saveDesign);
    document.getElementById('generate-btn').addEventListener('click', generateAndShowCode);
    document.querySelector('.close-btn').addEventListener('click', hideCodeModal);
    
    // Setup palette drag and drop
    setupPalette();
    
    // Setup tabs
    setupTabs();
    
    // Setup copy buttons
    setupCopyButtons();
    
    // Create initial design
    await createDesign('My Infrastructure');
    
    // Add connection mode toggle (right-click on canvas)
    getCanvas().addEventListener('contextmenu', (e) => {
        e.preventDefault();
        toggleConnectionMode();
    });
    
    // Deselect on canvas click
    getCanvas().addEventListener('click', (e) => {
        if (e.target === getCanvas()) {
            state.selectedItem = null;
            state.selectedType = null;
            document.querySelectorAll('.component, .connection').forEach(el => {
                el.classList.remove('selected');
            });
            document.getElementById('properties-content').innerHTML = 
                '<p class="placeholder">Select a component or connection to edit properties</p>';
        }
    });
    
    console.log('Application initialized');
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
