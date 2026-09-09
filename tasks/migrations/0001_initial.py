import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Task", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("title", models.CharField(max_length=200, verbose_name="Название")), ("description", models.TextField(blank=True, verbose_name="Описание")), ("deadline", models.DateTimeField(verbose_name="Срок")), ("priority", models.IntegerField(choices=[(1, "Низкий"), (2, "Средний"), (3, "Высокий")], default=2, verbose_name="Приоритет")), ("completed", models.BooleanField(default=False, verbose_name="Выполнено")), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)), ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to=settings.AUTH_USER_MODEL))], options={"ordering": ["completed", "deadline", "-priority"]})]
