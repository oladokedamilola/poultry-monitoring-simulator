from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        # IMPORTANT:
        # Do NOT start simulators here.
        # Block simulators are controlled explicitly from views.
        pass






















# # monitoring/apps.py
# from django.apps import AppConfig
# import sys
# import logging

# logger = logging.getLogger("monitoring.apps")

# class MonitoringConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'monitoring'

#     def ready(self):
#         # Avoid starting threads during migrations, tests or management commands
#         try:
#             argv = sys.argv
#             unsafe_commands = {'migrate', 'makemigrations', 'collectstatic', 'shell', 'test'}
#             if any(cmd in argv for cmd in unsafe_commands):
#                 logger.info("Monitoring app ready: skipping simulators during management command.")
#                 return

#             # Import here to avoid AppRegistryNotReady errors during migrate
#             from .models import FlockProfile
#             from .services.user_simulator import start_simulator_for_user, is_running
#             # Start simulators for existing flock profiles (dev convenience)
#             for fp in FlockProfile.objects.select_related('user').all():
#                 user = fp.user
#                 if not is_running(user):
#                     try:
#                         start_simulator_for_user(user, fp, interval=3)
#                         logger.info("Started simulator for existing user: %s", user.username)
#                     except Exception:
#                         logger.exception("Failed to start simulator for user: %s", user.username)
#         except Exception:
#             # swallow exceptions to not break manage.py commands
#             logger.exception("MonitoringConfig.ready() failed (ignored).")
