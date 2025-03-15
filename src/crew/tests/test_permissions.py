from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from crew.models import CrewInstance, Agent, Task

User = get_user_model()


class CrewPermissionsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user1
        )

    def test_unauthenticated_access(self):
        url = reverse('api:crewinstance-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_crew_access(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('api:crewinstance-detail', args=[self.crew.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_crew_access(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('api:crewinstance-detail', args=[self.crew.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AgentPermissionsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user1
        )
        self.agent = Agent.objects.create(
            crew=self.crew,
            name='Test Agent',
            role='researcher',
            description='A test agent'
        )

    def test_unauthenticated_access(self):
        url = reverse('api:agent-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_agent_access(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('api:agent-detail', args=[self.agent.id])
        response = self.client.put(url, {
            'name': 'Modified Agent',
            'role': 'writer'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_agent_access(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('api:agent-detail', args=[self.agent.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskPermissionsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user1
        )
        self.agent = Agent.objects.create(
            crew=self.crew,
            name='Test Agent',
            role='researcher',
            description='A test agent'
        )
        self.task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Test Task',
            description='A test task',
            expected_output='Expected result'
        )

    def test_unauthenticated_access(self):
        url = reverse('api:task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_task_access(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('api:task-detail', args=[self.task.id])
        response = self.client.patch(url, {
            'status': 'completed'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_task_access(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('api:task-detail', args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_completion_permission(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('api:task-complete', args=[self.task.id])
        response = self.client.post(url, {
            'output': 'Task completed successfully'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK) 