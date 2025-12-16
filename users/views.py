# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
import json
import logging

from users.forms import RegisterForm, LoginForm, ProfileUpdateForm
from monitoring.models import SensorData
from flock.models import FlockBlock
from .tokens import account_activation_token

logger = logging.getLogger(__name__)


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            messages.success(request, "🎉 Account created successfully! You can now log in to set up your poultry monitoring system.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username_or_email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username_or_email, password=password)

            if user is not None:
                login(request, user)
                
                # Check if user has any flock blocks
                has_blocks = FlockBlock.objects.filter(user=user).exists()
                
                if not has_blocks:
                    # New user or user without blocks
                    messages.info(request, "👋 Welcome to PoultryGuard! Let's set up your first flock block to start monitoring your poultry.")
                    messages.info(request, "📋 You'll need to create at least one poultry block to access all features.")
                    return redirect("flock:flock_setup")
                else:
                    # Existing user with blocks
                    messages.success(request, f"✅ Welcome back, {user.username}! Ready to monitor your flock?")
                    return redirect("dashboard")
            else:
                messages.error(request, "❌ Invalid login credentials. Please check your username and password.")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "👋 You have been successfully logged out. See you again soon!")
    return redirect("login")


# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm
from .models import Profile

@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Handle profile image
            if 'profile_image' in request.FILES:
                # Get or create profile for the user
                profile, created = Profile.objects.get_or_create(user=user)
                profile.profile_image = request.FILES['profile_image']
                profile.save()
            
            messages.success(request, "✅ Profile updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "users/profile.html", {"form": form})


@login_required
def dashboard(request):
    try:
        # Get all flock blocks for the user
        blocks = FlockBlock.objects.filter(user=request.user)
        
        # Check if user has any blocks
        blocks_exist = blocks.exists()
        
        if not blocks_exist:
            # No blocks at all - show empty state
            return render(request, "users/dashboard.html", {
                "blocks_exist": False,
                "block_data": [],
            })
        
        # User has blocks - prepare data for each block
        block_data = []
        for block in blocks:
            # Get latest sensor data for this block
            latest = SensorData.objects.filter(block=block).order_by('-timestamp').first()
            
            # Prepare history data for chart (last 20 readings)
            history_data = []
            if latest:
                history = SensorData.objects.filter(block=block).order_by('-timestamp')[:20]
                for h in reversed(history):  # Reverse to show chronological order
                    history_data.append({
                        "timestamp": h.timestamp.isoformat() if h.timestamp else "",
                        "temperature": float(h.temperature) if h.temperature else 0.0
                    })
            
            block_data.append({
                "block": block,
                "latest": latest,
                "history_json": json.dumps(history_data),
            })
        
        return render(request, "users/dashboard.html", {
            "blocks_exist": True,
            "block_data": block_data,
        })
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        messages.error(request, "⚠️ Unable to load dashboard data. Please try again or contact support if the issue persists.")
        return render(request, "users/dashboard.html", {
            "blocks_exist": False,
            "block_data": [],
            "error": "Unable to load dashboard data. Please try again."
        })


@login_required
def check_flock_setup_required(request):
    """
    Utility function to check if user needs to set up flock blocks.
    Can be used as a decorator or in middleware if needed.
    """
    has_blocks = FlockBlock.objects.filter(user=request.user).exists()
    return not has_blocks


# def register_view(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  
#             user.save()

#             # Send verification email
#             current_site = get_current_site(request)
#             subject = "Activate Your PoultraGuard Account"
#             message = render_to_string("users/email_verification.html", {
#                 "user": user,
#                 "domain": current_site.domain,
#                 "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#                 "token": account_activation_token.make_token(user),
#             })

#             send_mail(subject, message, "noreply@poultraguard.com", [user.email])

#             messages.success(request, "Account created! Check your email to verify.")
#             return redirect("users:login")
#     else:
#         form = RegisterForm()

#     return render(request, "users/register.html", {"form": form})

# from django.utils.http import urlsafe_base64_decode

# def activate_account(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = User.objects.get(pk=uid)
#     except Exception:
#         user = None

#     if user and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         messages.success(request, "Your account has been activated. Please log in.")
#         return redirect("users:login")

#     return render(request, "users/activation_failed.html")