from django.conf import settings
from django.db import models
from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        NORMAL = 'normal', 'Обычный'
        HIGH = 'high', 'Высокий'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField('Срок', null=True, blank=True)
    priority = models.CharField('Приоритет', max_length=6, choices=Priority.choices, default=Priority.NORMAL)
    completed = models.BooleanField('Выполнено', default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', '-priority', 'due_date', 'id']

    @property
    def is_overdue(self):
        return not self.completed and self.due_date is not None and self.due_date < timezone.now()

    @classmethod
    def ordered(cls, owner):
        return cls.objects.filter(owner=owner).annotate(
            priority_order=Case(When(priority='high', then=Value(0)), When(priority='normal', then=Value(1)), default=Value(2), output_field=IntegerField()),
            no_due_date=Case(When(due_date__isnull=True, then=Value(1)), default=Value(0), output_field=IntegerField()),
        ).order_by('completed', 'priority_order', 'no_due_date', 'due_date', 'id')

    def __str__(self):
        return self.title
