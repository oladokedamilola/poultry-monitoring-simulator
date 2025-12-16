# monitoring/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('data/latest/', views.latest_data, name='latest-data'),
    path('data/history/', views.data_history, name='data-history'),
    path('alerts/', views.alerts, name='alerts'),
    path('sim/status/<int:block_id>/', views.simulation_status, name='simulation_status'),
    
    # Live simulation page
    path("live/<int:block_id>/", views.live_simulation, name="live"),
    
    # AJAX simulation controls for live page (no page reload)
    path("live/start/<int:block_id>/", views.start_simulation_live, name="start_sim_live"),
    path("live/stop/<int:block_id>/", views.stop_simulation_live, name="stop_sim_live"),
    
    # Original simulation controls (redirects to referrer)
    path("sim/start/<int:block_id>/", views.start_block_sim, name="start_sim"),
    path("sim/stop/<int:block_id>/", views.stop_block_sim, name="stop_sim"),
    
    # History views
    path("history/", views.history_blocks, name="history_blocks"),
    path("history/<int:block_id>/", views.history_detail, name="history_detail"),
    path('history/<int:block_id>/export/csv/', views.export_history_csv, name='export_history_csv'),
    path('history/<int:block_id>/export/pdf/', views.export_history_pdf, name='export_history_pdf'),
]