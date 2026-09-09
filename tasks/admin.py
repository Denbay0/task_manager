from django.contrib import admin
from .models import Task
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "deadline", "priority", "completed")
    list_filter = ("completed", "priority", "deadline")
    search_fields = ("title", "description", "owner__username")
