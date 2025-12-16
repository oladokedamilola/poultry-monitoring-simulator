# monitoring/services/simulator_core.py
import random
import math

class SensorSimulatorCore:
    def __init__(self, initial_settings=None, flock=None):
        self.flock = flock
        
        # Handle None initial_settings
        if initial_settings is None:
            initial_settings = {}
        
        # Initialize with default values
        self.temperature = initial_settings.get('temperature', 30.0)
        self.humidity = initial_settings.get('humidity', 70.0)
        self.feed_level = initial_settings.get('feed_level', 100.0)
        self.water_level = initial_settings.get('water_level', 100.0)
        self.ammonia = initial_settings.get('ammonia', 10.0)
        self.activity_level = initial_settings.get('activity_level', 80.0)
        
        # Apply breed-specific adjustments if flock is provided
        if self.flock:
            self._apply_breed_adjustments()
    
    def _apply_breed_adjustments(self):
        """Adjust base values based on flock breed."""
        breed_adjustments = {
            'broiler': {'temperature': 32.0, 'humidity': 65.0},
            'layer': {'temperature': 28.0, 'humidity': 60.0},
            'kuroiler': {'temperature': 30.0, 'humidity': 68.0},
            'local': {'temperature': 29.0, 'humidity': 70.0},
        }
        
        adjustment = breed_adjustments.get(self.flock.breed, {})
        if 'temperature' in adjustment:
            self.temperature = adjustment['temperature']
        if 'humidity' in adjustment:
            self.humidity = adjustment['humidity']

    def _fluctuate(self, value, min_val, max_val, step=0.5):
        value += random.uniform(-step, step)
        return max(min(value, max_val), min_val)

    def generate_data(self):
        # Use flock to bias behaviors
        birds = getattr(self.flock, 'number_of_birds', 10)
        breed = getattr(self.flock, 'breed', 'broiler')
        age_group = getattr(self.flock, 'age_group', 'adult')

        # Base steps scaled by flock size (more birds -> faster resource consumption)
        consumption_factor = 1 + (birds / 50.0)  # simple scale

        # Temperature - slow fluctuation, but age/breed sensitivity can bias it
        temp_step = 0.15 + (0.05 if age_group == 'adult' else 0.02)
        self.temperature = self._fluctuate(self.temperature, 24, 40, step=temp_step)

        # Humidity - correlated weakly with temp
        hum_step = 0.4
        self.humidity = self._fluctuate(self.humidity, 45, 90, step=hum_step)

        # Feed & water decrease over time depending on birds and activity
        feed_decrease = (0.05 + 0.02 * (self.activity_level / 100.0)) * consumption_factor
        water_decrease = (0.06 + 0.02 * (self.activity_level / 100.0)) * consumption_factor
        self.feed_level = max(0.0, self.feed_level - random.uniform(feed_decrease * 0.5, feed_decrease * 1.5))
        self.water_level = max(0.0, self.water_level - random.uniform(water_decrease * 0.5, water_decrease * 1.5))

        # Ammonia increases as feed/water drop and humidity rises
        ammonia_delta = ( (100 - self.feed_level)/500.0 + (self.humidity - 60)/200.0 ) + random.uniform(-0.2, 0.6)
        self.ammonia = max(0.0, min(100.0, self.ammonia + ammonia_delta))

        # Activity level responds to temperature (too hot -> lower activity) and age/breed
        base_activity = 60 + (10 if breed in ['kuroiler', 'local'] else 0)
        temp_penalty = 0
        if self.temperature > 34:
            temp_penalty = (self.temperature - 34) * 2.5  # larger penalty for high temp
        self.activity_level = max(5.0, min(100.0, self.activity_level + random.uniform(-4, 4) + (base_activity - self.activity_level)*0.02 - temp_penalty*0.2))

        data = {
            "temperature": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "feed_level": round(self.feed_level, 1),
            "water_level": round(self.water_level, 1),
            "ammonia": round(self.ammonia, 1),
            "activity_level": round(self.activity_level, 1),
        }
        return data