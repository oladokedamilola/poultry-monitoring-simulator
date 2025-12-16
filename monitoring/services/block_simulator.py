# poultry_monitoring/monitoring/services/block_simulator.py
import threading
import time
import logging
import random

from django.utils import timezone

from .simulator_core import SensorSimulatorCore
from monitoring.models import SensorData, Alert
from flock.models import FlockBlock

logger = logging.getLogger("monitoring.block_simulator")

# Global dictionary to track running simulators
running_simulators = {}

class BlockSimulatorThread:
    def __init__(self, block: FlockBlock, interval=3):
        self.block = block
        self.user = block.user
        self.interval = interval

        self._stop = threading.Event()

        self.thread = threading.Thread(
            target=self.run,
            daemon=True,
            name=f"Sim-Block-{block.id}"
        )

        # Provide default settings or handle None in SensorSimulatorCore
        self.core = SensorSimulatorCore(initial_settings={}, flock=block)

    def start(self):
        if not self.thread.is_alive():
            logger.info("Starting block simulator for block=%s", self.block.id)
            self.thread.start()

    def stop(self):
        logger.info("Stopping block simulator for block=%s", self.block.id)
        self._stop.set()

    def run(self):
        try:
            while not self._stop.is_set():
                data = self.core.generate_data()

                # Save reading
                try:
                    SensorData.objects.create(
                        user=self.user,
                        block=self.block,
                        **data
                    )
                except Exception:
                    logger.exception("Failed to save SensorData for block %s", self.block.id)

                # Cleanup old data
                try:
                    SensorData.cleanup_old_data(self.user, days=30)
                except Exception:
                    logger.exception("Cleanup failed for block %s", self.block.id)

                # Check for alerts
                try:
                    self._create_alerts(data)
                except Exception:
                    logger.exception("Alert error for block %s", self.block.id)

                # Sleep with some randomness
                sleep_time = self.interval + (0.1 * (random.random() - 0.5))
                time.sleep(max(0.5, sleep_time))

        except Exception:
            logger.exception("Thread crashed for block %s", self.block.id)

        finally:
            logger.info("Block simulator exiting for block=%s", self.block.id)
            # Remove from running simulators
            if str(self.block.id) in running_simulators:
                del running_simulators[str(self.block.id)]

    def _create_alerts(self, data):
        THRESHOLDS = {
            "temperature": (28, 34),
            "humidity": (None, 85),
            "ammonia": (None, 25),
            "feed_level": (20, None),
            "water_level": (20, None),
            "activity_level": (30, None),
        }

        for key, (min_val, max_val) in THRESHOLDS.items():
            value = data.get(key)

            if min_val is not None and value < min_val:
                Alert.objects.create(
                    user=self.user,
                    block=self.block,
                    alert_type=f"{key.capitalize()} Alert",
                    message=f"{key.capitalize()} too low: {value}",
                )

            if max_val is not None and value > max_val:
                Alert.objects.create(
                    user=self.user,
                    block=self.block,
                    alert_type=f"{key.capitalize()} Alert",
                    message=f"{key.capitalize()} too high: {value}",
                )

def start_simulator_for_block(block: FlockBlock, interval=3):
    block_key = str(block.id)
    
    if block_key in running_simulators and running_simulators[block_key].thread.is_alive():
        logger.info(f"Simulator already running for block {block.name}")
        return running_simulators[block_key]

    sim = BlockSimulatorThread(block, interval)
    running_simulators[block_key] = sim
    sim.start()
    logger.info(f"Started simulator for block {block.name} (ID: {block.id})")
    return sim

def stop_simulator_for_block(block: FlockBlock):
    block_key = str(block.id)
    
    if block_key in running_simulators:
        sim = running_simulators[block_key]
        sim.stop()
        del running_simulators[block_key]
        logger.info(f"Stopped simulator for block {block.name}")
        return True
    else:
        logger.info(f"No running simulator found for block {block.name}")
        return False

def is_running(block: FlockBlock):
    block_key = str(block.id)
    return block_key in running_simulators and running_simulators[block_key].thread.is_alive()