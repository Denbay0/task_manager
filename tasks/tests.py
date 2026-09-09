from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Task

class TaskManagerTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="StrongPass123")
        self.other = User.objects.create_user("other", password="StrongPass123")
        self.task = Task.objects.create(title="Private", deadline=timezone.now() + timedelta(days=1), priority=Task.Priority.HIGH, owner=self.owner)

    def test_list_contains_only_owned_tasks(self):
        Task.objects.create(title="Other task", deadline=timezone.now(), owner=self.other)
        self.client.force_login(self.owner)
        response = self.client.get(reverse("tasks:list"))
        self.assertContains(response, "Private")
        self.assertNotContains(response, "Other task")

    def test_foreign_mutations_return_404(self):
        self.client.force_login(self.other)
        for name in ("edit", "delete"):
            self.assertEqual(self.client.get(reverse(f"tasks:{name}", args=[self.task.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("tasks:toggle", args=[self.task.pk])).status_code, 404)

    def test_toggle_is_post_only(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse("tasks:toggle", args=[self.task.pk])).status_code, 405)
        self.client.post(reverse("tasks:toggle", args=[self.task.pk]))
        self.task.refresh_from_db(); self.assertTrue(self.task.completed)

    def test_delete_confirmation_and_post(self):
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(reverse("tasks:delete", args=[self.task.pk])), "Удалить задачу")
        self.client.post(reverse("tasks:delete", args=[self.task.pk]))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_overdue_property(self):
        self.task.deadline = timezone.now() - timedelta(minutes=1); self.task.save()
        self.assertTrue(self.task.is_overdue)
