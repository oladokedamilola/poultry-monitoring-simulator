# monitoring/admin.py
from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import SensorData, Alert
from django.contrib.auth.models import User

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'block', 'timestamp', 'temperature', 'humidity', 'ammonia', 'feed_level', 'water_level', 'activity_level', 'is_recent')
    list_filter = ('user', 'block', 'timestamp', 'temperature', 'humidity')
    search_fields = ('user__username', 'block__name', 'block__flock__name')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'block', 'timestamp')
        }),
        ('Sensor Readings', {
            'fields': (
                ('temperature', 'humidity', 'ammonia'),
                ('feed_level', 'water_level', 'activity_level')
            )
        }),
    )
    
    def is_recent(self, obj):
        """Check if data is from last 24 hours"""
        return obj.timestamp >= timezone.now() - timedelta(hours=24)
    is_recent.boolean = True
    is_recent.short_description = 'Recent (<24h)'
    
    actions = ['delete_old_data', 'export_as_csv']
    
    def delete_old_data(self, request, queryset):
        """Admin action to delete data older than 30 days"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old_data = queryset.filter(timestamp__lt=thirty_days_ago)
        count = old_data.count()
        old_data.delete()
        self.message_user(request, f"Successfully deleted {count} records older than 30 days.")
    delete_old_data.short_description = "Delete selected data older than 30 days"
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'block', 'alert_type', 'timestamp', 'resolved', 'truncated_message')
    list_filter = ('user', 'block', 'alert_type', 'resolved', 'timestamp')
    search_fields = ('user__username', 'block__name', 'alert_type', 'message')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 50
    actions = ['mark_as_resolved', 'mark_as_unresolved', 'export_alerts']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('user', 'block', 'timestamp', 'alert_type', 'resolved')
        }),
        ('Details', {
            'fields': ('message',)
        }),
    )
    
    def truncated_message(self, obj):
        """Display shortened version of message"""
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    truncated_message.short_description = 'Message'
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(resolved=True)
        self.message_user(request, f"Marked {updated} alerts as resolved.")
    mark_as_resolved.short_description = "Mark selected alerts as resolved"
    
    def mark_as_unresolved(self, request, queryset):
        updated = queryset.update(resolved=False)
        self.message_user(request, f"Marked {updated} alerts as unresolved.")
    mark_as_unresolved.short_description = "Mark selected alerts as unresolved"
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_add_permission(self, request):
        """Only allow superusers to add alerts manually"""
        return request.user.is_superuser