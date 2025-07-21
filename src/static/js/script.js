document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    const resultText = document.getElementById('result-text');
    const loader = document.getElementById('loader');
    const refreshAnalysisBtn = document.getElementById('refresh-analysis-btn');
    const startLogBtn = document.getElementById('start-log-btn');
    const stopLogBtn = document.getElementById('stop-log-btn');
    const loggingStatus = document.getElementById('logging-status');
    const predictionLog = document.getElementById('prediction-log');
    const formInputs = {
        acc_x: document.getElementById('acc_x'),
        acc_y: document.getElementById('acc_y'),
        acc_z: document.getElementById('acc_z'),
        gyro_x: document.getElementById('gyro_x'),
        gyro_y: document.getElementById('gyro_y'),
        gyro_z: document.getElementById('gyro_z'),
        heart_rate: document.getElementById('heart_rate'),
        spo2: document.getElementById('spo2')
    };
    let charts = {};

    // --- Page Navigation ---
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            pages.forEach(page => page.classList.toggle('active', page.id === targetId));
            if (targetId === 'analysis') loadAnalysisData();
        });
    });

    // --- Logging Controls ---
    startLogBtn.addEventListener('click', () => fetch('/api/start-logging', { method: 'POST' }));
    stopLogBtn.addEventListener('click', () => fetch('/api/stop-logging', { method: 'POST' }));

    // --- WebSocket Connection ---
    function connectWebSocket() {
        const socket = new WebSocket(`ws://${window.location.host}/ws/live`);
        socket.onopen = () => displayResult("Connected to live stream...", false, 'result-info');
        socket.onclose = () => displayResult("Live stream disconnected.", true);
        socket.onerror = () => displayResult("Connection error.", true);
        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.prediction) {
                displayResult(`Live Prediction: ${message.prediction}`);
                Object.keys(formInputs).forEach(key => formInputs[key].value = message.data[key]);
                
                const logItem = document.createElement('li');
                const time = new Date().toLocaleTimeString();
                logItem.innerHTML = `<strong>${message.prediction}</strong> <span class="log-time">@ ${time}</span>`;
                predictionLog.prepend(logItem);

                while (predictionLog.children.length > 50) {
                    predictionLog.lastChild.remove();
                }
            }
            if (message.status) updateLoggingStatus(message.status);
        };
    }
    connectWebSocket();

    // --- Analysis Page Logic ---
    refreshAnalysisBtn.addEventListener('click', loadAnalysisData);
    async function loadAnalysisData() {
        try {
            const response = await fetch('/api/analysis-data');
            const data = await response.json();
            if (data.length === 0) {
                alert("No data logged yet. Start and stop a logging session first.");
                return;
            }
            Object.values(charts).forEach(chart => chart.destroy());
            createPieChart(data);
            createLineChart(data);
            createGyroLineChart(data);
            createHealthChart(data);
        } catch (error) {
            console.error("Failed to load analysis data:", error);
        }
    }

    function createPieChart(data) {
        const ctx = document.getElementById('swingPieChart').getContext('2d');
        const counts = data.reduce((acc, row) => {
            // Check for 'prediction' first, then fall back to 'label'
            const key = row.prediction || row.label;
            if (key) { // Ensure the key is not null or undefined
                acc[key] = (acc[key] || 0) + 1;
            }
            return acc;
        }, {});
        charts.pie = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(counts),
                datasets: [{ data: Object.values(counts), backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0'] }]
            },
            options: { responsive: true, maintainAspectRatio: true }
        });
    }

    function createLineChart(data) {
        const ctx = document.getElementById('sensorLineChart').getContext('2d');
        charts.line = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((_, index) => index + 1),
                datasets: [
                    { label: 'Accel X', data: data.map(r => r.acc_x), borderColor: '#FF6384', fill: false, tension: 0.1 },
                    { label: 'Accel Y', data: data.map(r => r.acc_y), borderColor: '#36A2EB', fill: false, tension: 0.1 },
                    { label: 'Accel Z', data: data.map(r => r.acc_z), borderColor: '#FFCE56', fill: false, tension: 0.1 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: true, scales: { y: { beginAtZero: false } } }
        });
    }

    function createGyroLineChart(data) {
        const ctx = document.getElementById('gyroLineChart').getContext('2d');
        charts.gyroLine = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((_, index) => index + 1),
                datasets: [
                    { label: 'Gyro X', data: data.map(r => r.gyro_x), borderColor: '#4bc0c0', fill: false, tension: 0.1 },
                    { label: 'Gyro Y', data: data.map(r => r.gyro_y), borderColor: '#9966ff', fill: false, tension: 0.1 },
                    { label: 'Gyro Z', data: data.map(r => r.gyro_z), borderColor: '#ff9f40', fill: false, tension: 0.1 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: true, scales: { y: { beginAtZero: false } } }
        });
    }


    function createHealthChart(data) {
        const ctx = document.getElementById('healthDataChart').getContext('2d');
        charts.health = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((_, index) => index + 1),
                datasets: [
                    { label: 'Heart Rate (BPM)', data: data.map(r => r.heart_rate), borderColor: '#dc3545', fill: false, tension: 0.1 },
                    { label: 'SpO2 (%)', data: data.map(r => r.spo2), borderColor: '#007bff', fill: false, tension: 0.1 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: true, scales: { y: { beginAtZero: false } } }
        });
    }


    // --- UI Helper Functions ---
    const displayResult = (text, isError = false, customClass = null) => {
        loader.classList.add('hidden');
        resultText.classList.remove('hidden');
        resultText.textContent = text;
        resultText.className = 'result-text';
        if (customClass) resultText.classList.add(customClass);
        else resultText.classList.add(isError ? 'result-error' : 'result-success');
    };

    function updateLoggingStatus(status) {
        const statusText = loggingStatus.querySelector('.status-text');
        if (status === 'Logging Started') {
            loggingStatus.className = 'status-indicator recording';
            statusText.textContent = 'Recording Data';
            startLogBtn.disabled = true;
            stopLogBtn.disabled = false;
        } else if (status === 'Logging Stopped') {
            loggingStatus.className = 'status-indicator idle';
            statusText.textContent = 'Logging Idle';
            startLogBtn.disabled = false;
            stopLogBtn.disabled = true;
        }
    }
});