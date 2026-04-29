const tbody = document.getElementById('process-body');
const addProcessBtn = document.getElementById('add-process-btn');
const simulateBtn = document.getElementById('simulate-btn');
const resultsSection = document.getElementById('results-section');
let processCount = 0;

// Custom table charts will be used instead of Chart.js

// Initial processes
const initialProcesses = [
    { id: 'P1', at: 0, bt: 0, pr: 0 },
    { id: 'P2', at: 0, bt: 0, pr: 0 },
    { id: 'P3', at: 0, bt: 0, pr: 0 }
];

function addRow(id = '', at = 0, bt = 0, pr = 0) {
    if(!id) {
        processCount++;
        id = `P${processCount}`;
    } else {
        processCount = Math.max(processCount, parseInt(id.replace('P', '')));
    }
    
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="text" class="p-id" value="${id}" readonly></td>
        <td><input type="number" class="p-at" value="${at}" min="0"></td>
        <td><input type="number" class="p-bt" value="${bt}" min="0"></td>
        <td><input type="number" class="p-pr" value="${pr}" min="0"></td>
        <td><button class="btn rem-btn" onclick="this.closest('tr').remove()">×</button></td>
    `;
    tbody.appendChild(tr);
}

initialProcesses.forEach(p => addRow(p.id, p.at, p.bt, p.pr));

addProcessBtn.addEventListener('click', () => addRow());

simulateBtn.addEventListener('click', async () => {
    simulateBtn.innerText = "Simulating...";
    const rows = document.querySelectorAll('#process-body tr');
    const data = [];
    
    rows.forEach(row => {
        data.push({
            id: row.querySelector('.p-id').value,
            arrival: row.querySelector('.p-at').value,
            burst: row.querySelector('.p-bt').value,
            priority: row.querySelector('.p-pr').value
        });
    });

    const timeQuantumInput = document.getElementById('time-quantum');
    const timeQuantum = timeQuantumInput ? parseInt(timeQuantumInput.value) : 2;

    try {
        const response = await fetch('/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ processes: data, time_quantum: timeQuantum })
        });
        
        const result = await response.json();
        
        renderResults(result);
    } catch (e) {
        alert("Make sure the Flask server is running! Error: " + e.message);
    }
    simulateBtn.innerText = "Run";
});

function renderResults(res) {
    resultsSection.classList.remove('hidden');
    
    // Populate the matching metrics table
    const metricsBody = document.getElementById('metrics-body');
    metricsBody.innerHTML = `
        <tr>
            <td><strong>FCFS</strong></td>
            <td>${res.fcfs.energy.toFixed(2)}</td>
            <td>${res.fcfs.tat.toFixed(2)}</td>
            <td>${res.fcfs.wt.toFixed(2)}</td>
        </tr>
        <tr>
            <td><strong>Priority</strong></td>
            <td>${res.priority.energy.toFixed(2)}</td>
            <td>${res.priority.tat.toFixed(2)}</td>
            <td>${res.priority.wt.toFixed(2)}</td>
        </tr>
        <tr>
            <td><strong>Round Robin</strong></td>
            <td>${res.rr.energy.toFixed(2)}</td>
            <td>${res.rr.tat.toFixed(2)}</td>
            <td>${res.rr.wt.toFixed(2)}</td>
        </tr>
        <tr style="background: rgba(0, 255, 136, 0.1); color: var(--success); font-weight: 600;">
            <td>EAAS (Proposed)</td>
            <td>${res.eaas.energy.toFixed(2)}</td>
            <td>${res.eaas.tat.toFixed(2)}</td>
            <td>${res.eaas.wt.toFixed(2)}</td>
        </tr>
    `;

    // Draw Gantt Charts
    drawGantt('gantt-fcfs', res.fcfs.gantt);
    drawGantt('gantt-priority', res.priority.gantt);
    drawGantt('gantt-rr', res.rr.gantt);
    drawGantt('gantt-eaas', res.eaas.gantt);

    // Draw Custom Table Charts
    const algorithms = ['FCFS', 'Priority', 'RR', 'EAAS'];
    const energyData = [res.fcfs.energy, res.priority.energy, res.rr.energy, res.eaas.energy];
    const waitData = [res.fcfs.wt, res.priority.wt, res.rr.wt, res.eaas.wt];
    const bgColors = ['#4299e1', '#9f7aea', '#ed8936', '#48bb78'];

    drawTableChart('energyChartContainer', 'Energy Comparison (Lower is Better)', algorithms, energyData, bgColors);
    drawTableChart('performanceChartContainer', 'Performance - Wait Time (Lower is Better)', algorithms, waitData, bgColors);
    
    // Smooth scroll
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function drawGantt(elementId, ganttData) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';
    
    if(ganttData.length === 0) return;

    const totalTime = ganttData[ganttData.length - 1][2] - ganttData[0][1];
    
    // Color generator based on PID
    const getColor = (pid) => {
        const colors = ['#2ecc71', '#f1c40f', '#3498db', '#e74c3c', '#9b59b6', '#1abc9c', '#e67e22'];
        const num = parseInt(pid.replace('P', '')) || 0;
        return colors[(num - 1) % colors.length];
    };

    ganttData.forEach((block, index) => {
        const [pid, start, end] = block;
        const duration = end - start;
        const widthPercent = (duration / totalTime) * 100;
        
        const div = document.createElement('div');
        div.className = 'gantt-block';
        div.style.width = widthPercent + '%';
        div.style.backgroundColor = getColor(pid);
        
        div.innerHTML = `<span>${pid}</span>`;
        
        if (index === 0) {
            div.innerHTML += `<span class="gantt-time-start">${start}</span>`;
        }
        div.innerHTML += `<span class="gantt-time">${end}</span>`;
        
        container.appendChild(div);
    });
}

function drawTableChart(containerId, title, labels, data, colors) {
    const container = document.getElementById(containerId);
    container.innerHTML = `<h3 style="color: #2d3748; font-size: 16px; margin-bottom: 1rem; text-align: center;">${title}</h3>`;
    
    const table = document.createElement('table');
    table.className = 'table-chart';
    
    const maxData = Math.max(...data) || 1; // Prevent division by zero
    
    labels.forEach((label, i) => {
        const val = data[i].toFixed(2);
        // Calculate width percentage relative to max value (leaving some space for the value text)
        const widthPercent = (data[i] / maxData) * 85; 
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="table-chart-label">${label}</td>
            <td class="table-chart-bar-container">
                <div class="table-chart-bar" style="width: ${widthPercent}%; background-color: ${colors[i]};"></div>
                <span class="table-chart-value">${val}</span>
            </td>
        `;
        table.appendChild(tr);
    });
    
    container.appendChild(table);
}

