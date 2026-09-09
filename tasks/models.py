from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Task(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 1, "Низкий"
        MEDIUM = 2, "Средний"
        HIGH = 3, "Высокий"

    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    deadline = models.DateTimeField("Срок")
    priority = models.IntegerField("Приоритет", choices=Priority.choices, default=Priority.MEDIUM)
    completed = models.BooleanField("Выполнено", default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["completed", "deadline", "-priority"]

    @property
    def is_overdue(self):
        return not self.completed and self.deadline < timezone.now()

    def __str__(self):
        return self.title
