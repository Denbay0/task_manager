from django.urls import path
from . import views
app_name = "tasks"
urlpatterns = [path("", views.index, name="index"), path("tasks/", views.task_list, name="list"), path("tasks/new/", views.create, name="create"), path("tasks/<int:pk>/edit/", views.edit, name="edit"), path("tasks/<int:pk>/delete/", views.delete, name="delete"), path("tasks/<int:pk>/toggle/", views.toggle, name="toggle")]
