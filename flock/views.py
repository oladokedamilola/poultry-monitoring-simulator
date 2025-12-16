# flock/views.py

import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator 
from .models import FlockBlock
from .forms import BlockForm
from monitoring.models import SensorData, Alert
from monitoring.services.block_simulator import is_running

logger = logging.getLogger("flock.views")


@login_required
def flock_setup(request):
    """
    Initial flock setup view - guides user through creating their first block.
    """
    existing_blocks = FlockBlock.objects.filter(user=request.user).count()
    
    if existing_blocks > 0:
        messages.info(request, "✅ You already have flock blocks set up. You can create additional blocks here.")
        return redirect("flock:blocks")
    
    # Check if user came here via middleware redirect
    if request.META.get('HTTP_REFERER', ''):
        if 'dashboard' in request.META.get('HTTP_REFERER', ''):
            messages.info(request, "📋 Welcome to your dashboard! First, let's create your poultry block to start monitoring.")
        elif 'flock' in request.META.get('HTTP_REFERER', ''):
            messages.info(request, "📋 You need to complete setup first before accessing flock pages.")
        else:
            messages.info(request, "👋 Hello! Let's set up your poultry monitoring system by creating your first flock block.")
    else:
        messages.info(request, "📋 Complete this one-time setup to start using PoultryGuard.")
        messages.info(request, "🐣 Create your first flock block to begin monitoring and simulations.")
    
    if request.method == "POST":
        return redirect("flock:create")
    
    return render(request, "flock/setup.html", {
        "has_blocks": existing_blocks > 0,
        "max_blocks": 3,
    })


@login_required
def blocks_list(request):
    """
    List all poultry blocks for the logged-in user.
    """
    blocks = FlockBlock.objects.filter(user=request.user)
    
    if not blocks.exists():
        messages.info(request, "📋 You don't have any flock blocks yet. Create your first one to get started!")
        return redirect("flock:flock_setup")
    
    total_birds_result = blocks.aggregate(total=Sum('number_of_birds'))
    total_birds = total_birds_result['total'] or 0
    
    active_simulations = 0
    for block in blocks:
        if is_running(block):
            active_simulations += 1
    
    data_points = SensorData.objects.filter(block__in=blocks).count()
    
    for block in blocks:
        block.is_running = is_running(block)
        block.recent_alerts = Alert.objects.filter(
            block=block, 
            resolved=False
        ).count()
    
    context = {
        'blocks': blocks,
        'total_birds': total_birds,
        'active_simulations': active_simulations,
        'data_points': data_points,
    }
    return render(request, "flock/blocks_list.html", context)


@login_required
def choose_block(request):
    """
    Allow user to choose one of their existing blocks.
    """
    blocks = FlockBlock.objects.filter(user=request.user)
    
    if not blocks.exists():
        messages.info(request, "📋 You need to create a flock block first before choosing one for simulation.")
        return redirect("flock:flock_setup")
    
    messages.info(request, "🔍 Select a flock block to start live monitoring simulation.")
    return render(request, "flock/block_select.html", {"blocks": blocks})


@login_required
def block_create(request):
    """
    Create a new poultry block.
    Limit: max 3 blocks per user.
    """
    if FlockBlock.objects.filter(user=request.user).count() >= 3:
        messages.warning(request, "⚠️ Maximum limit reached. You can only create up to 3 flock blocks.")
        return render(request, "flock/max_limit.html")

    if request.method == "POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            block = form.save(commit=False)
            block.user = request.user
            block.save()

            # Set session flag for completed setup
            request.session['just_completed_setup'] = True
            
            messages.success(request, f"✅ Flock block '{block.name}' created successfully!")
            
            # If this was their first block, redirect to dashboard
            if FlockBlock.objects.filter(user=request.user).count() == 1:
                messages.info(request, "🎉 Great! Now you can start monitoring your flock from the dashboard.")
                return redirect("dashboard")
            else:
                messages.info(request, "📊 You can now view all your blocks or start a simulation.")
                return redirect("flock:blocks")
    else:
        form = BlockForm()
        # Check if user came from setup page
        if request.META.get('HTTP_REFERER', '') and 'setup' in request.META.get('HTTP_REFERER', ''):
            messages.info(request, "📝 Fill in your flock details below to complete setup.")
        else:
            messages.info(request, "📝 Fill in your flock details below. You can update this information anytime.")

    return render(request, "flock/block_create.html", {"form": form})


@login_required
def block_detail(request, block_id):
    """
    View details of a single poultry block with pagination.
    """
    try:
        # Get the block
        block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
        
        # --- Pagination for Sensor Data ---
        data_page = request.GET.get('data_page', 1)
        data_paginator = Paginator(SensorData.objects.filter(block=block).order_by('-timestamp'), 10)
        recent_data = data_paginator.get_page(data_page)
        
        # --- Pagination for Alerts ---
        alerts_page = request.GET.get('alerts_page', 1)
        alerts_paginator = Paginator(Alert.objects.filter(block=block, resolved=False).order_by('-timestamp'), 5)
        active_alerts = alerts_paginator.get_page(alerts_page)
        
        # Data for charts (last 50 data points for a smooth line)
        chart_data = SensorData.objects.filter(block=block).order_by('timestamp')[:50]
        
        # Prepare data lists for the chart labels and datasets
        timestamps = [data.timestamp.strftime('%H:%M') for data in chart_data]
        temperatures = [float(data.temperature) for data in chart_data]
        humidities = [float(data.humidity) for data in chart_data]
        ammonia_levels = [float(data.ammonia) for data in chart_data]
        
        context = {
            "block": block,
            "block_id": block.id,
            "is_running": is_running(block),
            "recent_data": recent_data,  # This is now a paginated Page object
            "active_alerts": active_alerts,  # This is now a paginated Page object
            "data_points_count": SensorData.objects.filter(block=block).count(),
            "chart_labels": timestamps,
            "chart_temperatures": temperatures,
            "chart_humidities": humidities,
            "chart_ammonia": ammonia_levels,
        }
        
        return render(request, "flock/block_detail.html", context)
        
    except Exception as e:
        logger.error(f"Error in block_detail view: {str(e)}", exc_info=True)
        messages.error(request, "⚠️ Error loading block details.")
        return redirect("flock:blocks")

@login_required
def block_update(request, block_id):
    """
    Update block details (birds, breed, age group, etc).
    """
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)

    if request.method == "POST":
        form = BlockForm(request.POST, instance=block)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Flock block '{block.name}' updated successfully!")
            
            # Warn if simulation is running
            try:
                if is_running(block):
                    messages.warning(request, "⚠️ Note: Changes may not affect an active simulation until it's restarted.")
            except:
                pass
            
            return redirect("flock:detail", block_id=block.id)
    else:
        form = BlockForm(instance=block)
        messages.info(request, f"✏️ Update the details for your '{block.name}' flock block.")

    # Get display values for the template
    breed_display = block.get_breed_display()
    age_group_display = block.get_age_group_display()
    
    return render(
        request,
        "flock/block_update.html",
        {
            "form": form, 
            "block": block,
            "block_id": block.id,
            "is_running": is_running(block) if callable(is_running) else False,
            "breed_display": breed_display,
            "age_group_display": age_group_display,
        },
    )


@login_required
def block_delete(request, block_id):
    """
    Delete a poultry block.
    """
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
    
    if request.method == "POST":
        block_name = block.name
        
        # Check if simulation is running
        if is_running(block):
            messages.warning(request, f"⏸️ Stopping active simulation for '{block_name}' before deletion.")
        
        block.delete()
        messages.success(request, f"🗑️ Flock block '{block_name}' deleted successfully.")
        
        # Check if user still has blocks
        remaining_blocks = FlockBlock.objects.filter(user=request.user).count()
        if remaining_blocks == 0:
            messages.info(request, "📋 You have no flock blocks remaining. Create a new one to continue monitoring.")
            return redirect("flock:flock_setup")
        else:
            messages.info(request, f"📊 You have {remaining_blocks} block(s) remaining.")
        
        return redirect("flock:blocks")
    
    # Display warning for GET request
    messages.warning(request, f"⚠️ You are about to delete the flock block '{block.name}'.")
    messages.warning(request, "⚠️ This will also delete all associated monitoring data and alerts.")
    messages.warning(request, "⚠️ This action cannot be undone.")
    
    if is_running(block):
        messages.warning(request, "⚠️ Note: An active simulation for this block will be stopped.")
    
    return render(request, "flock/block_delete.html", {"block": block})