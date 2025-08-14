from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

class TaskAPITestCase(APITestCase):

    def setUp(self):
        # Create a normal user
        self.user = User.objects.create_user(
            username="dulal",
            email="dulal.ahmed@gmail.com",
            password="Dulal12@"
        )
        # Create an admin user
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="AdminPass123"
        )

        # URLs
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.task_list_url = reverse('task-list')  # DRF router name

    def authenticate(self):
        """Helper method to authenticate a normal user."""
        response = self.client.post(self.token_url, {
            "username": "dulal",
            "password": "Dulal12@"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Extract token from the wrapped response
        token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_register_user(self):
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123",
            "password2": "TestPass123"  # added for serializer validation
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertEqual(response.data["status"], "success")
        self.assertIn("data", response.data)

    def test_login_and_get_token(self):
        response = self.client.post(self.token_url, {
            "username": "dulal",
            "password": "Dulal12@"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Tokens are inside data now
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data.get("status"), "success")

    def test_create_task_authenticated(self):
        self.authenticate()
        payload = {
            "title": "Test Task",
            "description": "This is a test task",
            "completed": False
        }
        response = self.client.post(self.task_list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().owner, self.user)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Task created successfully")

    def test_list_tasks_authenticated(self):
        self.authenticate()
        Task.objects.create(
            title="Sample Task",
            description="Sample description",
            completed=False,
            owner=self.user
        )
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertIsInstance(response.data["data"], list)
        self.assertEqual(len(response.data["data"]), 1)

    def test_retrieve_specific_task(self):
        self.authenticate()
        task = Task.objects.create(
            title="Specific Task",
            description="Details",
            completed=False,
            owner=self.user
        )
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["data"]["title"], "Specific Task")

    def test_delete_task_returns_message(self):
        self.authenticate()
        task = Task.objects.create(
            title="Delete Me",
            description="Delete this task",
            completed=False,
            owner=self.user
        )
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Task deleted successfully")
        self.assertFalse(Task.objects.filter(id=task.id).exists())

