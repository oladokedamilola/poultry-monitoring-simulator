# users/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from flock.models import FlockBlock

class FlockSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None
        
        # Define paths that don't require flock setup
        allowed_paths = [
            '/flock/setup/',  # Setup page itself
            '/flock/create/',  # Create block page
            '/logout/',        # Logout
            '/profile/',       # Profile page
            '/api/',           # API endpoints (if any)
        ]
        
        # Check if current path is allowed
        if any(request.path.startswith(path) for path in allowed_paths):
            return None
        
        # Check if user has flock blocks
        has_blocks = FlockBlock.objects.filter(user=request.user).exists()
        
        if not has_blocks:
            # If user is already on setup page, don't redirect again
            if request.path == reverse('flock:flock_setup'):
                return None
            
            # Show appropriate message based on where they're trying to go
            if request.path == reverse('dashboard'):
                messages.info(request, "🎯 Welcome! To get started, please create your first poultry block.")
            elif 'flock' in request.path:
                messages.warning(request, "📋 You need to complete setup first before accessing flock pages.")
            else:
                messages.info(request, "👋 Hello! Let's set up your poultry monitoring system by creating your first flock block.")
            
            # Redirect to setup page
            return redirect('flock:flock_setup')
        
        return None