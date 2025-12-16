# flock/admin.py
from django.contrib import admin
from .models import FlockBlock
from django.contrib.auth.models import User

@admin.register(FlockBlock)
class FlockBlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'breed', 'age_group', 'number_of_birds', 'created_at', 'description_preview')
    list_filter = ('breed', 'age_group', 'created_at', 'user')
    search_fields = ('name', 'user__username', 'description', 'breed')
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'number_of_birds')
        }),
        ('Bird Details', {
            'fields': ('breed', 'age_group')
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
    )
    
    def description_preview(self, obj):
        """Display a shortened version of the description"""
        if obj.description:
            if len(obj.description) > 50:
                return f"{obj.description[:50]}..."
            return obj.description
        return "-"
    description_preview.short_description = 'Description Preview'
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter user field for non-superusers"""
        if db_field.name == "user":
            if not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
                kwargs["initial"] = request.user.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Auto-assign current user if not superuser"""
        if not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['export_flocks_csv']
    
    def export_flocks_csv(self, request, queryset):
        """Admin action to export selected flocks as CSV"""
        import csv
        from django.http import HttpResponse
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'ID', 'Name', 'Username', 'Breed', 'Age Group',
            'Number of Birds', 'Created At', 'Description'
        ])
        
        # Write data
        for flock in queryset:
            writer.writerow([
                flock.id,
                flock.name,
                flock.user.username,
                flock.breed,
                flock.age_group,
                flock.number_of_birds,
                flock.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                flock.description or ''
            ])
        
        output.seek(0)
        response = HttpResponse(output, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="flock_blocks.csv"'
        return response
    
    export_flocks_csv.short_description = "Export selected flocks to CSV"