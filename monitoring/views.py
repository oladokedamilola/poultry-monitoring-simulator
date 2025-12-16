# monitoring/views.py

import json
import logging
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flock.models import FlockBlock
from monitoring.models import SensorData, Alert
from monitoring.serializers import SensorDataSerializer, AlertSerializer
from monitoring.services.block_simulator import (
    start_simulator_for_block,
    stop_simulator_for_block,
    is_running,
)

logger = logging.getLogger("monitoring.views")


# -----------------------------
# Live Simulation
# -----------------------------
# monitoring/views.py
import logging

logger = logging.getLogger(__name__)

# @login_required
# def live_simulation(request, block_id):
#     """
#     Render live simulation page for a given block.
#     """
#     print(f"DEBUG: live_simulation called with block_id={block_id}")
#     print(f"DEBUG: request.user={request.user}")
    
#     try:
#         block = FlockBlock.objects.get(id=block_id, user=request.user)
#         print(f"DEBUG: Block found: id={block.id}, name={block.name}")
#         print(f"DEBUG: Block fields:")
#         print(f"  - number_of_birds: {block.number_of_birds}")
#         print(f"  - breed: {block.breed}")
#         print(f"  - age_group: {block.age_group}")
#         print(f"  - description: {block.description}")
#         print(f"  - created_at: {block.created_at}")
#         print(f"  - updated_at: {block.updated_at}")
        
#         # Debug get_display methods
#         print(f"  - get_breed_display(): {block.get_breed_display()}")
#         print(f"  - get_age_group_display(): {block.get_age_group_display()}")
        
#     except FlockBlock.DoesNotExist:
#         print(f"DEBUG: Block {block_id} does not exist for user {request.user}")
#         messages.error(request, "Block not found or access denied.")
#         return redirect('dashboard')
#     except Exception as e:
#         print(f"DEBUG: Error getting block: {str(e)}")
#         messages.error(request, f"Error: {str(e)}")
#         return redirect('dashboard')
    
#     # Get the latest sensor data for initial display
#     latest_data = SensorData.objects.filter(block=block).order_by('-timestamp').first()
#     print(f"DEBUG: Latest data: {latest_data}")
    
#     # Get active alerts
#     active_alerts = Alert.objects.filter(block=block, resolved=False).order_by('-timestamp')[:10]
#     print(f"DEBUG: Active alerts count: {active_alerts.count()}")
    
#     # Check if simulator is running
#     simulator_running = is_running(block)
#     print(f"DEBUG: Simulator running: {simulator_running}")
    
#     context = {
#         "block": block,
#         "latest_data": latest_data,
#         "active_alerts": active_alerts,
#         "simulator_running": simulator_running,
#     }
    
#     print(f"DEBUG: Context prepared, rendering template...")
#     return render(request, "monitoring/live_simulation.html", context)


# monitoring/views.py
@login_required
def live_simulation(request, block_id):
    """
    Render live simulation page for a given block.
    """
    print(f"DEBUG: live_simulation called with block_id={block_id}")
    
    try:
        block = FlockBlock.objects.get(id=block_id, user=request.user)
        print(f"DEBUG: Block found: id={block.id}, name={block.name}")
    except FlockBlock.DoesNotExist:
        print(f"DEBUG: Block {block_id} does not exist for user {request.user}")
        messages.error(request, "Block not found or access denied.")
        return redirect('dashboard')
    except Exception as e:
        print(f"DEBUG: Error getting block: {str(e)}")
        messages.error(request, f"Error: {str(e)}")
        return redirect('dashboard')
    
    # Get the latest sensor data for initial display
    latest_data = SensorData.objects.filter(block=block).order_by('-timestamp').first()
    
    # Get active alerts
    active_alerts = Alert.objects.filter(block=block, resolved=False).order_by('-timestamp')[:10]
    
    # Check if simulator is running
    simulator_running = is_running(block)
    print(f"DEBUG: Simulator running: {simulator_running}")
    
    context = {
        "block": block,
        "latest_data": latest_data,
        "active_alerts": active_alerts,
        "simulator_running": simulator_running,
    }
    
    # Use standalone template
    return render(request, "monitoring/live_simulation_standalone.html", context)


@login_required
def start_simulation_live(request, block_id):
    """
    Start simulator from the live simulation page.
    Stays on the live page after starting.
    """
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
    
    try:
        start_simulator_for_block(block)
        messages.success(request, f"Simulation started for block: {block.name}")
    except Exception as e:
        logger.error(f"Error starting simulator for block {block_id}: {str(e)}")
        messages.error(request, f"Failed to start simulation: {str(e)}")
    
    # Always redirect back to the live simulation page
    return redirect('live', block_id=block_id)


# monitoring/views.py - Update the AJAX views

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt  # Temporarily disable CSRF for testing
@require_POST  # Only allow POST requests
@login_required
def start_simulation_live(request, block_id):
    """
    Start simulator from the live simulation page via AJAX.
    """
    try:
        block = FlockBlock.objects.get(id=block_id, user=request.user)
    except FlockBlock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Block not found or access denied'
        }, status=404)
    
    try:
        start_simulator_for_block(block)
        return JsonResponse({
            'success': True,
            'message': f"Simulation started for block: {block.name}",
            'block_id': block_id,
            'is_running': True
        })
    except Exception as e:
        logger.error(f"Error starting simulator for block {block_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f"Failed to start simulation: {str(e)}"
        }, status=500)


@csrf_exempt  # Temporarily disable CSRF for testing
@require_POST  # Only allow POST requests
@login_required
def stop_simulation_live(request, block_id):
    """
    Stop simulator from the live simulation page via AJAX.
    """
    try:
        block = FlockBlock.objects.get(id=block_id, user=request.user)
    except FlockBlock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Block not found or access denied'
        }, status=404)
    
    try:
        stop_simulator_for_block(block)
        return JsonResponse({
            'success': True,
            'message': f"Simulation stopped for block: {block.name}",
            'block_id': block_id,
            'is_running': False
        })
    except Exception as e:
        logger.error(f"Error stopping simulator for block {block_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f"Failed to stop simulation: {str(e)}"
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def simulation_status(request, block_id):
    """
    API endpoint to check if simulation is running for a block.
    """
    try:
        block = FlockBlock.objects.get(id=block_id, user=request.user)
        is_running_status = is_running(block)
        
        # Get latest data if simulation is running
        latest_data = None
        if is_running_status:
            latest_data = SensorData.objects.filter(block=block).order_by('-timestamp').first()
        
        return Response({
            'is_running': is_running_status,
            'block_id': block_id,
            'block_name': block.name,
            'latest_data': SensorDataSerializer(latest_data).data if latest_data else None
        })
    except FlockBlock.DoesNotExist:
        return Response({'error': 'Block not found'}, status=404)


# -----------------------------
# Simulator Controls
# -----------------------------
@login_required
def start_block_sim(request, block_id):
    """
    Start simulator for a specific block.
    """
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
    start_simulator_for_block(block)
    messages.success(request, f"Simulation started for block: {block.name}")
    return redirect(request.META.get("HTTP_REFERER", "monitoring:dashboard"))


@login_required
def stop_block_sim(request, block_id):
    """
    Stop simulator for a specific block.
    """
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
    stop_simulator_for_block(block)
    messages.success(request, f"Simulation stopped for block: {block.name}")
    return redirect(request.META.get("HTTP_REFERER", "monitoring:dashboard"))


# -----------------------------
# API Endpoints (DRF)
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_data(request):
    """
    Return the latest sensor reading for the logged-in user.
    """
    latest = SensorData.objects.filter(user=request.user).first()
    serializer = SensorDataSerializer(latest)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data_history(request):
    """
    Return the last 200 sensor readings for the logged-in user.
    """
    qs = SensorData.objects.filter(user=request.user).order_by('-timestamp')[:200]
    serializer = SensorDataSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alerts(request):
    """
    Return the latest unresolved alerts for the logged-in user.
    """
    qs = Alert.objects.filter(user=request.user, resolved=False).order_by('-timestamp')[:50]
    serializer = AlertSerializer(qs, many=True)
    return Response(serializer.data)

# -----------------------------
# History Pages
# -----------------------------
@login_required
def history_blocks(request):
    """
    Show all blocks for the user with links to their history pages.
    """
    blocks = FlockBlock.objects.filter(user=request.user)
    return render(request, "monitoring/history_blocks.html", {"blocks": blocks})

from datetime import datetime, timedelta
from django.utils import timezone

def calculate_time_range(range_option):
    """
    Calculate start and end datetimes based on a range option string.
    
    Args:
        range_option (str): One of '1h', '6h', '12h', '24h', '7d', '30d'
        
    Returns:
        dict: {'start': datetime, 'end': datetime}
    """
    now = timezone.now()
    end = now
    
    if range_option == '1h':
        start = now - timedelta(hours=1)
    elif range_option == '6h':
        start = now - timedelta(hours=6)
    elif range_option == '12h':
        start = now - timedelta(hours=12)
    elif range_option == '24h':
        start = now - timedelta(hours=24)
    elif range_option == '7d':
        start = now - timedelta(days=7)
    elif range_option == '30d':
        start = now - timedelta(days=30)
    else:
        # Default to 24 hours if invalid option
        start = now - timedelta(hours=24)
    
    return {'start': start, 'end': end}


@login_required
def history_detail(request, block_id):
    """
    Detailed history charts for a specific block.
    Supports time-range filtering (1h, 6h, 12h, 24h, 7d).
    """
   
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
    
    # Get time range from request
    range_option = request.GET.get('range', '24h')
    
    # Calculate time range
    time_range = calculate_time_range(range_option)  # Implement this function
    
    # Get historical data
    history = SensorData.objects.filter(
        block=block,
        timestamp__gte=time_range['start'],
        timestamp__lte=time_range['end']
    ).order_by('timestamp')
    
    # Prepare data
    history_data = [{
        'timestamp': h.timestamp.isoformat(),
        'temperature': float(h.temperature) if h.temperature else 0,
        'humidity': float(h.humidity) if h.humidity else 0,
        'ammonia': float(h.ammonia) if h.ammonia else 0,
        'feed_level': float(h.feed_level) if h.feed_level else 0,
        'water_level': float(h.water_level) if h.water_level else 0,
        'activity_level': float(h.activity_level) if h.activity_level else 0,
    } for h in history]
    
    # Calculate averages
    if history_data:
        avg_temperature = sum(h['temperature'] for h in history_data) / len(history_data)
        avg_humidity = sum(h['humidity'] for h in history_data) / len(history_data)
        avg_ammonia = sum(h['ammonia'] for h in history_data) / len(history_data)
        avg_feed = sum(h['feed_level'] for h in history_data) / len(history_data)
        avg_water = sum(h['water_level'] for h in history_data) / len(history_data)
        avg_activity = sum(h['activity_level'] for h in history_data) / len(history_data)
    else:
        avg_temperature = avg_humidity = avg_ammonia = avg_feed = avg_water = avg_activity = 0
    
    # Range options for template
    range_options = [
        {'value': '1h', 'label': '1 Hour'},
        {'value': '6h', 'label': '6 Hours'},
        {'value': '12h', 'label': '12 Hours'},
        {'value': '24h', 'label': '24 Hours'},
        {'value': '7d', 'label': '7 Days'},
    ]
    
    return render(request, "monitoring/history_detail.html", {
        'block': block,
        'history_json': json.dumps(history_data),
        'range_option': range_option,
        'range_options': range_options,
        'data_points': len(history_data),
        'avg_temperature': avg_temperature,
        'avg_humidity': avg_humidity,
        'avg_ammonia': avg_ammonia,
        'avg_feed': avg_feed,
        'avg_water': avg_water,
        'avg_activity': avg_activity,
    })





from django.http import HttpResponse
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

@login_required
def export_history_csv(request, block_id):
    """Export historical data as CSV"""
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
    
    # Get time range from request
    range_option = request.GET.get('range', '24h')
    time_range = calculate_time_range(range_option)
    
    # Get historical data
    history = SensorData.objects.filter(
        block=block,
        timestamp__gte=time_range['start'],
        timestamp__lte=time_range['end']
    ).order_by('timestamp')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="history_block_{block_id}_{range_option}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Temperature (°C)', 'Humidity (%)', 'Ammonia (ppm)', 
                     'Feed Level (%)', 'Water Level (%)', 'Activity (%)'])
    
    for data in history:
        writer.writerow([
            data.timestamp,
            data.temperature or 0,
            data.humidity or 0,
            data.ammonia or 0,
            data.feed_level or 0,
            data.water_level or 0,
            data.activity_level or 0,
        ])
    
    return response

@login_required
def export_history_pdf(request, block_id):
    """Export historical data as PDF report"""
    block = get_object_or_404(FlockBlock, id=block_id, user=request.user)
    
    # Get time range from request
    range_option = request.GET.get('range', '24h')
    time_range = calculate_time_range(range_option)
    
    # Get historical data
    history = SensorData.objects.filter(
        block=block,
        timestamp__gte=time_range['start'],
        timestamp__lte=time_range['end']
    ).order_by('timestamp')
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"History Report - {block.name}", styles['Title'])
    elements.append(title)
    
    # Metadata
    metadata = [
        f"Time Range: {range_option}",
        f"Birds: {block.number_of_birds}",
        f"Breed: {block.get_breed_display()}",
        f"Age Group: {block.get_age_group_display()}",
        f"Data Points: {len(history)}"
    ]
    for meta in metadata:
        elements.append(Paragraph(meta, styles['Normal']))
    
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Create table data
    table_data = [['Timestamp', 'Temp (°C)', 'Humidity (%)', 'Ammonia (ppm)', 
                   'Feed (%)', 'Water (%)', 'Activity (%)']]
    
    for data in history:
        table_data.append([
            data.timestamp.strftime('%Y-%m-%d %H:%M'),
            f"{data.temperature or 0:.1f}",
            f"{data.humidity or 0:.1f}",
            f"{data.ammonia or 0:.1f}",
            f"{data.feed_level or 0:.1f}",
            f"{data.water_level or 0:.1f}",
            f"{data.activity_level or 0:.1f}",
        ])
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value from buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_block_{block_id}_{range_option}.pdf"'
    response.write(pdf)
    
    return response