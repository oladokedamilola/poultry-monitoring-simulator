# flock/urls.py
from django.urls import path
from . import views

app_name = "flock"

urlpatterns = [
    path("", views.blocks_list, name="blocks"),
    path("setup/", views.flock_setup, name="flock_setup"), 
    path("choose/", views.choose_block, name="choose"),
    path("create/", views.block_create, name="create"),
    path("<int:block_id>/", views.block_detail, name="detail"),
    path("<int:block_id>/edit/", views.block_update, name="update"),
    path("<int:block_id>/delete/", views.block_delete, name="delete"), 
]