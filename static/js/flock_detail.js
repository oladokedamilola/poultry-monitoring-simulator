document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Toggle Charts Visibility
    const toggleChartsBtn = document.getElementById('toggleChartsBtn');
    const chartsContainer = document.getElementById('chartsContainer');
    
    if (toggleChartsBtn && chartsContainer) {
        toggleChartsBtn.addEventListener('click', function() {
            const isHidden = chartsContainer.style.display === 'none';
            chartsContainer.style.display = isHidden ? 'block' : 'none';
            this.innerHTML = isHidden 
                ? '<i class="fas fa-eye-slash me-2"></i>Hide Charts' 
                : '<i class="fas fa-chart-line me-2"></i>Show Charts';
            
            // Initialize chart only when shown for the first time
            if (isHidden && !window.chartInitialized) {
                initializeChart();
                window.chartInitialized = true;
            }
        });
    }
    
    // 2. Initialize Chart.js Chart
    function initializeChart() {
        const ctx = document.getElementById('environmentChart')?.getContext('2d');
        if (!ctx) return;
        
        // Use data passed from Django template (ensure these variables are defined in your template)
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: window.chartLabels || [], // e.g., ['10:00', '10:05']
                datasets: [
                    {
                        label: 'Temperature (°C)',
                        data: window.chartTemperatures || [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Humidity (%)',
                        data: window.chartHumidities || [],
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Ammonia (ppm)',
                        data: window.chartAmmonia || [],
                        borderColor: 'rgb(255, 159, 64)',
                        backgroundColor: 'rgba(255, 159, 64, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { beginAtZero: false }
                },
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }
    
    // 3. Pass Chart Data from Django Template to JS
    // This script block should be INLINED in your HTML template, just before including this .js file.
    // It transfers the context variables from Django into the global window object for JS to use.
    // <script>
    //     window.chartLabels = {{ chart_labels|safe }};
    //     window.chartTemperatures = {{ chart_temperatures|safe }};
    //     window.chartHumidities = {{ chart_humidities|safe }};
    //     window.chartAmmonia = {{ chart_ammonia|safe }};
    // </script>
});