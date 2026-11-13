from datetime import timedelta
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Task

class TaskManagerTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="StrongPass123")
        self.other = User.objects.create_user("other", password="StrongPass123")
        self.task = Task.objects.create(title="Private", due_date=timezone.now() + timedelta(days=1), priority=Task.Priority.HIGH, owner=self.owner)

    def test_list_contains_only_owned_tasks(self):
        Task.objects.create(title="Other task", due_date=timezone.now(), owner=self.other)
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
        self.task.due_date = timezone.now() - timedelta(minutes=1); self.task.save()
        self.assertTrue(self.task.is_overdue)

    def test_auth_and_missing_ids(self):
        self.assertEqual(self.client.get(reverse('tasks:list')).status_code, 302)
        self.assertEqual(self.client.get(reverse('tasks:create')).status_code, 302)
        self.client.force_login(self.owner)
        for name in ('edit', 'delete', 'toggle'):
            url = reverse(f'tasks:{name}', args=[999999])
            self.assertEqual((self.client.post if name == 'toggle' else self.client.get)(url).status_code, 404)

    def test_create_and_owner_spoof(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('tasks:create'), {'title': 'Created', 'description': 'Details', 'due_date': '', 'priority': 'normal', 'owner': self.other.pk})
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Created')
        self.assertEqual(task.owner, self.owner)
        self.assertIsNone(task.due_date)

    def test_edit_and_invalid_date(self):
        self.client.force_login(self.owner)
        url = reverse('tasks:edit', args=[self.task.pk])
        response = self.client.post(url, {'title': 'Private', 'due_date': 'not-a-date', 'priority': 'low'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        response = self.client.post(url, {'title': 'Edited', 'due_date': '2030-02-01T12:30', 'priority': 'low', 'owner': self.other.pk})
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual((self.task.title, self.task.priority, self.task.owner), ('Edited', 'low', self.owner))

    def test_toggle_both_directions_and_get_delete(self):
        self.client.force_login(self.owner)
        toggle = reverse('tasks:toggle', args=[self.task.pk])
        delete = reverse('tasks:delete', args=[self.task.pk])
        self.client.get(delete)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
        self.client.post(toggle)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        self.client.post(toggle)
        self.task.refresh_from_db()
        self.assertFalse(self.task.completed)

    def test_csrf_and_post_logout(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(reverse('tasks:toggle', args=[self.task.pk])).status_code, 403)
        self.assertEqual(client.post(reverse('tasks:delete', args=[self.task.pk])).status_code, 403)
        self.assertEqual(client.post(reverse('users:logout')).status_code, 403)
        self.assertEqual(client.get(reverse('users:logout')).status_code, 405)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(reverse('users:logout')).status_code, 302)

    def test_sorting(self):
        Task.objects.create(title='Normal', priority='normal', owner=self.owner)
        Task.objects.create(title='Low', priority='low', owner=self.owner)
        Task.objects.create(title='High no date', priority='high', owner=self.owner)
        self.client.force_login(self.owner)
        titles = list(self.client.get(reverse('tasks:list')).context['tasks'].values_list('title', flat=True))
        self.assertEqual(titles, ['Private', 'High no date', 'Normal', 'Low'])
