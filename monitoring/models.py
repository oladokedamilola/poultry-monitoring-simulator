# monitoring/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta


class SensorData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sensor_data')
    block = models.ForeignKey("flock.FlockBlock", on_delete=models.CASCADE, related_name='sensor_data')

    timestamp = models.DateTimeField(default=timezone.now)

    temperature = models.FloatField()
    humidity = models.FloatField()
    ammonia = models.FloatField()
    feed_level = models.FloatField()
    water_level = models.FloatField()
    activity_level = models.FloatField()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['block', 'timestamp']),
        ]


    @staticmethod
    def cleanup_old_data(user, days=30):
        threshold = timezone.now() - timedelta(days=days)
        SensorData.objects.filter(user=user, timestamp__lt=threshold).delete()

    def __str__(self):
        return f"{self.user.username} reading @ {self.timestamp:%Y-%m-%d %H:%M:%S}"


class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    block = models.ForeignKey("flock.FlockBlock", on_delete=models.CASCADE, related_name='alerts')

    timestamp = models.DateTimeField(default=timezone.now)
    alert_type = models.CharField(max_length=100)
    message = models.TextField()
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.alert_type} at {self.timestamp:%Y-%m-%d %H:%M:%S}"
