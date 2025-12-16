// live_simulation.js - Complete implementation
window.PGLiveSim = (function() {
  let canvas, ctx;
  let simulationInterval;
  let statusCheckInterval;
  let isPaused = false;
  let isDayTime = true;
  let currentData = null;
  let config = {};
  let currentSimulatorRunning = false;
  
  // Initialize the simulation
  function init(initConfig) {
    console.log('Initializing canvas simulation with config:', initConfig);
    config = initConfig;
    currentSimulatorRunning = config.simulatorRunning;
    
    // Get canvas element
    canvas = document.getElementById('farmCanvas');
    if (!canvas) {
      console.error('Canvas element not found');
      return;
    }
    
    // Get context
    ctx = canvas.getContext('2d');
    
    // Set canvas size based on container
    resizeCanvas();
    
    // Handle window resize
    window.addEventListener('resize', resizeCanvas);
    
    // Start simulation status check
    startStatusCheck();
    
    // Start data polling if simulator is running
    if (currentSimulatorRunning) {
      startPolling();
    } else {
      console.log('Simulator is not running. Start simulation to begin data updates.');
      draw(); // Draw initial state
    }
    
    // Set up control button handlers
    setupControlButtons();
  }
  
  // Resize canvas to fit container
  function resizeCanvas() {
    if (!canvas) return;
    
    const container = canvas.parentElement;
    if (!container) return;
    
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    
    // Set canvas dimensions
    canvas.width = containerWidth;
    canvas.height = containerHeight;
    
    console.log(`Canvas resized to ${containerWidth}x${containerHeight}`);
    
    // Redraw with new dimensions
    draw();
  }
  
  // Start polling for data
  function startPolling() {
    if (simulationInterval) {
      clearInterval(simulationInterval);
    }
    
    // Initial fetch
    fetchData();
    
    // Set up interval for polling
    simulationInterval = setInterval(() => {
      if (!isPaused) {
        fetchData();
      }
    }, config.pollInterval || 2000);
    
    console.log(`Started polling every ${config.pollInterval || 2000}ms`);
  }
  
  // Fetch data from API
  function fetchData() {
    if (!config.blockId) {
      console.error('No block ID configured');
      return;
    }
    
    // For now, use simulated data. Replace with actual API call later
    generateSimulatedData();
    
    // Example of actual API call:
    /*
    fetch(`${config.apiBaseUrl}monitoring/data/latest/?block_id=${config.blockId}`)
      .then(response => response.json())
      .then(data => {
        currentData = data;
        updateHUD(data);
        draw();
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        // Use simulated data as fallback
        generateSimulatedData();
      });
    */
  }
  
  // Generate simulated data
  function generateSimulatedData() {
    // Base values with some randomness
    const baseTemp = 22.5;
    const baseHumidity = 65;
    const baseAmmonia = 12;
    const baseFeed = 75;
    const baseWater = 80;
    const baseActivity = isDayTime ? 50 : 20; // Less activity at night
    
    currentData = {
      temperature: baseTemp + (Math.random() * 4 - 2),
      humidity: baseHumidity + (Math.random() * 10 - 5),
      ammonia: baseAmmonia + (Math.random() * 6 - 3),
      feed_level: Math.max(0, Math.min(100, baseFeed + (Math.random() * 10 - 5))),
      water_level: Math.max(0, Math.min(100, baseWater + (Math.random() * 10 - 5))),
      activity: Math.max(0, Math.min(100, baseActivity + (Math.random() * 20 - 10))),
      timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})
    };
    
    console.log('Generated simulated data:', currentData);
    updateHUD(currentData);
    draw();
  }
  
  // Update HUD display
  function updateHUD(data) {
    // Update temperature
    const tempEl = document.getElementById('kpi-temp');
    if (tempEl) tempEl.textContent = data.temperature ? `${data.temperature.toFixed(1)} °C` : '-- °C';
    
    // Update humidity
    const humEl = document.getElementById('kpi-hum');
    if (humEl) humEl.textContent = data.humidity ? `${data.humidity.toFixed(1)} %` : '-- %';
    
    // Update ammonia
    const ammoEl = document.getElementById('kpi-ammo');
    if (ammoEl) ammoEl.textContent = data.ammonia ? `${data.ammonia.toFixed(1)} ppm` : '-- ppm';
    
    // Update feed
    const feedEl = document.getElementById('kpi-feed');
    if (feedEl) feedEl.textContent = data.feed_level ? `${data.feed_level.toFixed(1)} %` : '-- %';
    
    // Update water
    const waterEl = document.getElementById('kpi-water');
    if (waterEl) waterEl.textContent = data.water_level ? `${data.water_level.toFixed(1)} %` : '-- %';
    
    // Update activity
    const activityEl = document.getElementById('kpi-activity');
    if (activityEl) activityEl.textContent = data.activity ? `${data.activity.toFixed(1)} %` : '-- %';
    
    // Update last update time
    const lastUpdateEl = document.getElementById('last-update');
    if (lastUpdateEl) lastUpdateEl.textContent = data.timestamp || '--:--';
    
    // Update progress bars
    updateProgressBar('hud-feed', data.feed_level || 0);
    updateProgressBar('hud-water', data.water_level || 0);
    
    // Update alert count
    updateAlertCount();
  }
  
  // Update a progress bar
  function updateProgressBar(elementId, value) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Clamp value between 0 and 100
    const clampedValue = Math.max(0, Math.min(100, value));
    element.style.width = `${clampedValue}%`;
    
    // Update color based on value
    if (clampedValue < 20) {
      element.className = 'fill pg-fill-danger';
    } else if (clampedValue < 40) {
      element.className = 'fill pg-fill-warning';
    } else {
      element.className = 'fill pg-fill-good';
    }
  }
  
  // Update alert count
  function updateAlertCount() {
    const alertCountEl = document.getElementById('alert-count');
    if (!alertCountEl) return;
    
    // Simulate some alerts based on data
    let alertCount = 0;
    if (currentData) {
      if (currentData.temperature > 28 || currentData.temperature < 18) alertCount++;
      if (currentData.humidity > 80 || currentData.humidity < 50) alertCount++;
      if (currentData.ammonia > 25) alertCount++;
      if (currentData.feed_level < 20) alertCount++;
      if (currentData.water_level < 20) alertCount++;
    }
    
    alertCountEl.textContent = alertCount;
    
    // Update alert list if needed
    if (alertCount > 0) {
      updateAlertList();
    }
  }
  
  // Update alert list (simplified)
  function updateAlertList() {
    const alertsListEl = document.getElementById('alertsList');
    if (!alertsListEl) return;
    
    // Clear existing alerts
    alertsListEl.innerHTML = '';
    
    // Add simulated alerts based on conditions
    const alerts = [];
    if (currentData) {
      if (currentData.temperature > 28) {
        alerts.push({
          type: 'High Temperature',
          message: `Temperature is high: ${currentData.temperature.toFixed(1)}°C`,
          level: 'warning'
        });
      } else if (currentData.temperature < 18) {
        alerts.push({
          type: 'Low Temperature',
          message: `Temperature is low: ${currentData.temperature.toFixed(1)}°C`,
          level: 'warning'
        });
      }
      
      if (currentData.feed_level < 20) {
        alerts.push({
          type: 'Low Feed',
          message: `Feed level is low: ${currentData.feed_level.toFixed(1)}%`,
          level: 'danger'
        });
      }
      
      if (currentData.water_level < 20) {
        alerts.push({
          type: 'Low Water',
          message: `Water level is low: ${currentData.water_level.toFixed(1)}%`,
          level: 'danger'
        });
      }
    }
    
    // Render alerts
    if (alerts.length === 0) {
      alertsListEl.innerHTML = '<div class="pg-small pg-muted">No active alerts</div>';
    } else {
      alerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert-item alert-${alert.level} mb-2`;
        alertDiv.innerHTML = `
          <div class="alert-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="alert-content">
            <h6>${alert.type}</h6>
            <p>${alert.message}</p>
            <small>Just now</small>
          </div>
        `;
        alertsListEl.appendChild(alertDiv);
      });
    }
  }
  
  // Draw the simulation on canvas
  function draw() {
    if (!canvas || !ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Set background based on day/night
    if (isDayTime) {
      ctx.fillStyle = '#f0f8ff'; // Light blue for day
    } else {
      ctx.fillStyle = '#0a1a2a'; // Dark blue for night
    }
    ctx.fillRect(0, 0, width, height);
    
    // Draw barn outline
    ctx.strokeStyle = isDayTime ? '#8B4513' : '#654321'; // Darker brown at night
    ctx.lineWidth = 4;
    ctx.strokeRect(40, 40, width - 80, height - 80);
    
    // Draw barn interior
    ctx.fillStyle = isDayTime ? '#FAF0E6' : '#2a2a2a'; // Lighter interior for day
    ctx.fillRect(42, 42, width - 84, height - 84);
    
    // Draw title
    ctx.fillStyle = isDayTime ? '#333' : '#fff';
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`Block ${config.blockId} - ${config.flockSize || 0} Birds`, width/2, 30);
    
    // Draw status
    ctx.font = '14px Arial';
    const statusText = currentSimulatorRunning ? 'Simulation Running' : 'Simulation Stopped';
    const statusColor = currentSimulatorRunning ? (isDayTime ? '#4CAF50' : '#8BC34A') : (isDayTime ? '#9E9E9E' : '#757575');
    ctx.fillStyle = statusColor;
    ctx.fillText(statusText, width/2, 55);
    
    // Draw data if available
    if (currentData) {
      ctx.font = '12px Arial';
      ctx.textAlign = 'left';
      ctx.fillStyle = isDayTime ? '#666' : '#ccc';
      
      const dataY = height - 60;
      ctx.fillText(`Temp: ${currentData.temperature.toFixed(1)}°C`, 60, dataY);
      ctx.fillText(`Humidity: ${currentData.humidity.toFixed(1)}%`, 60, dataY + 20);
      ctx.fillText(`Ammonia: ${currentData.ammonia.toFixed(1)}ppm`, width - 150, dataY);
      ctx.fillText(`Activity: ${currentData.activity.toFixed(1)}%`, width - 150, dataY + 20);
    }
    
    // Draw birds (circles representing birds)
    const birdCount = Math.min(config.flockSize || 0, 100); // Limit for performance
    for (let i = 0; i < birdCount; i++) {
      // Birds cluster more at night (resting)
      const clusterFactor = isDayTime ? 0.7 : 0.3;
      const x = 80 + Math.random() * (width - 160) * clusterFactor + (1 - clusterFactor) * (width - 160) / 2;
      const y = 80 + Math.random() * (height - 160);
      
      // Different colors based on activity and time
      let birdColor;
      if (!currentData) {
        birdColor = isDayTime ? '#FF9800' : '#FFB74D'; // Orange/Yellow
      } else {
        const activity = currentData.activity || 50;
        if (activity > 70) {
          birdColor = isDayTime ? '#FF5722' : '#FF8A65'; // Bright orange for high activity
        } else if (activity > 30) {
          birdColor = isDayTime ? '#FF9800' : '#FFB74D'; // Medium orange
        } else {
          birdColor = isDayTime ? '#FFC107' : '#FFD54F'; // Light yellow for low activity
        }
      }
      
      ctx.fillStyle = birdColor;
      ctx.beginPath();
      
      // Size varies slightly
      const size = 3 + Math.random() * 4;
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fill();
      
      // Add a small highlight for day time
      if (isDayTime) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(x - size/3, y - size/3, size/2, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    
    // Draw feed station
    drawFeedStation(width - 100, 80);
    
    // Draw water station
    drawWaterStation(60, 80);
    
    // Draw time indicator
    const time = new Date();
    const timeString = time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    ctx.fillStyle = isDayTime ? '#333' : '#fff';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(timeString, width - 40, height - 20);
    
    // Draw day/night indicator
    ctx.textAlign = 'left';
    ctx.fillText(isDayTime ? '☀ Day' : '🌙 Night', 40, height - 20);
  }
  
  // Draw feed station
  function drawFeedStation(x, y) {
    // Feed silo
    ctx.fillStyle = isDayTime ? '#795548' : '#5D4037';
    ctx.fillRect(x, y, 40, 60);
    
    // Feed level indicator
    const feedLevel = currentData ? currentData.feed_level : 50;
    const feedHeight = (feedLevel / 100) * 50;
    
    ctx.fillStyle = feedLevel < 30 ? '#D32F2F' : (feedLevel < 50 ? '#FF9800' : '#8BC34A');
    ctx.fillRect(x + 5, y + 55 - feedHeight, 30, feedHeight);
    
    // Silo details
    ctx.strokeStyle = isDayTime ? '#5D4037' : '#3E2723';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, 40, 60);
    
    // Label
    ctx.fillStyle = isDayTime ? '#333' : '#fff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('FEED', x + 20, y + 75);
  }
  
  // Draw water station
  function drawWaterStation(x, y) {
    // Water tank
    ctx.fillStyle = '#2196F3';
    ctx.beginPath();
    ctx.ellipse(x + 20, y, 25, 10, 0, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = isDayTime ? '#E3F2FD' : '#0D47A1';
    ctx.fillRect(x - 5, y, 50, 50);
    
    // Water level indicator
    const waterLevel = currentData ? currentData.water_level : 50;
    const waterHeight = (waterLevel / 100) * 40;
    
    ctx.fillStyle = waterLevel < 30 ? '#D32F2F' : (waterLevel < 50 ? '#2196F3' : '#64B5F6');
    ctx.fillRect(x - 3, y + 48 - waterHeight, 46, waterHeight);
    
    // Tank details
    ctx.strokeStyle = '#1976D2';
    ctx.lineWidth = 2;
    ctx.strokeRect(x - 5, y, 50, 50);
    
    // Label
    ctx.fillStyle = isDayTime ? '#333' : '#fff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('WATER', x + 20, y + 70);
  }
  
  // Start status check interval
  function startStatusCheck() {
    // Check status every 5 seconds
    statusCheckInterval = setInterval(() => {
      checkSimulationStatus();
    }, 5000);
  }
  
  // Check simulation status from server
  function checkSimulationStatus() {
    if (!config.blockId) return;
    
    // For now, we'll just log. In production, make an API call here.
    console.log(`Checking status for block ${config.blockId}`);
    
    // Example API call:
    /*
    fetch(`${config.apiBaseUrl}monitoring/sim/status/${config.blockId}/`)
      .then(response => response.json())
      .then(data => {
        if (data.is_running !== currentSimulatorRunning) {
          currentSimulatorRunning = data.is_running;
          console.log('Simulator status changed to:', currentSimulatorRunning);
          
          if (currentSimulatorRunning) {
            startPolling();
          } else {
            if (simulationInterval) {
              clearInterval(simulationInterval);
              simulationInterval = null;
            }
          }
          
          draw();
        }
      })
      .catch(error => {
        console.error('Error checking simulation status:', error);
      });
    */
  }
  
  // Setup control button event handlers
  function setupControlButtons() {
    // Pause/Resume button
    const pauseBtn = document.getElementById('pauseBtn');
    if (pauseBtn) {
      pauseBtn.addEventListener('click', function() {
        if (isPaused) {
          isPaused = false;
          this.innerHTML = '<i class="fas fa-pause me-2"></i>Pause Updates';
          console.log('Updates resumed');
          
          // If simulator is running, fetch data immediately
          if (currentSimulatorRunning) {
            fetchData();
          }
        } else {
          isPaused = true;
          this.innerHTML = '<i class="fas fa-play me-2"></i>Resume Updates';
          console.log('Updates paused');
        }
      });
    }
    
    // Toggle Day/Night button
    const toggleDayBtn = document.getElementById('toggleDayBtn');
    if (toggleDayBtn) {
      toggleDayBtn.addEventListener('click', function() {
        isDayTime = !isDayTime;
        this.innerHTML = isDayTime 
          ? '<i class="fas fa-sun me-2"></i>Toggle to Night' 
          : '<i class="fas fa-moon me-2"></i>Toggle to Day';
        console.log('Day/Night toggled:', isDayTime ? 'Day' : 'Night');
        draw();
      });
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function() {
        console.log('Manual refresh requested');
        if (currentSimulatorRunning && !isPaused) {
          fetchData();
        } else {
          draw(); // Just redraw
        }
      });
    }
  }
  
  // Public API
  return {
    init: init,
    pause: function() { 
      isPaused = true; 
      console.log('Simulation updates paused');
      
      // Update button text if button exists
      const pauseBtn = document.getElementById('pauseBtn');
      if (pauseBtn) {
        pauseBtn.innerHTML = '<i class="fas fa-play me-2"></i>Resume Updates';
      }
    },
    resume: function() { 
      isPaused = false; 
      console.log('Simulation updates resumed');
      
      // Update button text if button exists
      const pauseBtn = document.getElementById('pauseBtn');
      if (pauseBtn) {
        pauseBtn.innerHTML = '<i class="fas fa-pause me-2"></i>Pause Updates';
      }
      
      if (currentSimulatorRunning) {
        fetchData();
      }
    },
    toggleDayNight: function() { 
      isDayTime = !isDayTime; 
      console.log('Day/Night toggled:', isDayTime ? 'Day' : 'Night');
      
      // Update button text if button exists
      const toggleDayBtn = document.getElementById('toggleDayBtn');
      if (toggleDayBtn) {
        toggleDayBtn.innerHTML = isDayTime 
          ? '<i class="fas fa-sun me-2"></i>Toggle to Night' 
          : '<i class="fas fa-moon me-2"></i>Toggle to Day';
      }
      
      draw();
    },
    refresh: function() {
      console.log('Manual refresh requested');
      if (currentSimulatorRunning && !isPaused) {
        fetchData();
      } else {
        draw(); // Just redraw
      }
    },
    updateSimulationStatus: function(isRunning) {
      currentSimulatorRunning = isRunning;
      console.log('Simulation status updated to:', isRunning ? 'Running' : 'Stopped');
      
      if (isRunning) {
        startPolling();
      } else {
        if (simulationInterval) {
          clearInterval(simulationInterval);
          simulationInterval = null;
        }
        currentData = null;
        draw();
        updateHUD({});
      }
    },
    checkStatus: function() {
      console.log('Manual status check requested');
      checkSimulationStatus();
    },
    stop: function() {
      if (simulationInterval) {
        clearInterval(simulationInterval);
        simulationInterval = null;
      }
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
      }
      console.log('All polling stopped');
    },
    getStatus: function() {
      return {
        isRunning: currentSimulatorRunning,
        isPaused: isPaused,
        isDayTime: isDayTime,
        hasData: currentData !== null,
        blockId: config.blockId,
        flockSize: config.flockSize
      };
    },
    getData: function() {
      return currentData;
    }
  };
})();

// Auto-initialize if window.BLOCK_ID is set
document.addEventListener('DOMContentLoaded', function() {
  console.log('live_simulation.js loaded and DOM ready');
  
  // Check if we should auto-initialize
  if (window.BLOCK_ID && window.PGLiveSim) {
    console.log('Auto-initializing with window variables:', {
      BLOCK_ID: window.BLOCK_ID,
      SIMULATOR_RUNNING: window.SIMULATOR_RUNNING,
      FLOCK_SIZE: window.FLOCK_SIZE
    });
    
    window.PGLiveSim.init({
      blockId: window.BLOCK_ID,
      flockSize: window.FLOCK_SIZE || 100,
      pollInterval: 2000,
      simulatorRunning: window.SIMULATOR_RUNNING || false,
      apiBaseUrl: '/api/'
    });
  }
});