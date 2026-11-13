from django.db import migrations, models


def convert_priority(apps, schema_editor):
    Task = apps.get_model('tasks', 'Task')
    mapping = {'1': 'low', '2': 'normal', '3': 'high'}
    for task in Task.objects.order_by('pk').iterator():
        value = str(task.priority)
        if value not in mapping:
            raise ValueError(f'Unknown priority {value} for Task {task.pk}')
        Task.objects.filter(pk=task.pk).update(priority=mapping[value])


def reverse_priority(apps, schema_editor):
    Task = apps.get_model('tasks', 'Task')
    mapping = {'low': 1, 'normal': 2, 'high': 3}
    for task in Task.objects.order_by('pk').iterator():
        Task.objects.filter(pk=task.pk).update(priority=mapping[task.priority])


class Migration(migrations.Migration):
    dependencies = [('tasks', '0001_initial')]
    operations = [
        migrations.RenameField('task', 'created_at', 'date_added'),
        migrations.RenameField('task', 'deadline', 'due_date'),
        migrations.AlterField('task', 'due_date', models.DateTimeField('Срок', null=True, blank=True)),
        migrations.AlterField('task', 'priority', models.CharField('Приоритет', max_length=6, default='normal', choices=[('low', 'Низкий'), ('normal', 'Обычный'), ('high', 'Высокий')])),
        migrations.RunPython(convert_priority, reverse_priority),
        migrations.AlterModelOptions('task', options={'ordering': ['completed', '-priority', 'due_date', 'id']}),
    ]
