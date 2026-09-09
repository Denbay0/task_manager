from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from .forms import TaskForm
from .models import Task

def index(request):
    return render(request, "tasks/index.html")

@login_required
def task_list(request):
    return render(request, "tasks/list.html", {"tasks": Task.objects.filter(owner=request.user)})

@login_required
def create(request):
    form = TaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False); task.owner = request.user; task.save()
        return redirect("tasks:list")
    return render(request, "tasks/form.html", {"form": form, "title": "Новая задача"})

@login_required
def edit(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save(); return redirect("tasks:list")
    return render(request, "tasks/form.html", {"form": form, "title": "Редактирование"})

@login_required
def delete(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == "POST":
        task.delete(); return redirect("tasks:list")
    return render(request, "tasks/confirm_delete.html", {"task": task})

@login_required
def toggle(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.completed = not task.completed
    task.save(update_fields=["completed", "updated_at"])
    return redirect("tasks:list")
