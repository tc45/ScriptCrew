from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from crew.models import CrewInstance, Agent, Task

User = get_user_model()


class CrewAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user
        )
        self.flow = CrewInstance.objects.create(
            name='Test Flow',
            description='A test flow',
            owner=self.user,
            is_flow=True
        )

    def test_list_crews(self):
        url = reverse('api:crewinstance-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_crew(self):
        url = reverse('api:crewinstance-list')
        data = {
            'name': 'New Crew',
            'description': 'A new test crew'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CrewInstance.objects.count(), 3)
        self.assertEqual(response.data['name'], 'New Crew')

    def test_create_subcrew(self):
        url = reverse('api:crewinstance-list')
        data = {
            'name': 'New Subcrew',
            'description': 'A new test subcrew',
            'parent_crew': self.flow.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CrewInstance.objects.get(id=response.data['id']).is_subcrew)


class AgentAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user
        )
        self.agent = Agent.objects.create(
            crew=self.crew,
            name='Test Agent',
            role='researcher',
            description='A test agent'
        )

    def test_list_agents(self):
        url = reverse('api:agent-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_agent(self):
        url = reverse('api:agent-list')
        data = {
            'crew': self.crew.id,
            'name': 'New Agent',
            'role': 'writer',
            'description': 'A new test agent',
            'goals': ['Write content'],
            'backstory': 'Expert writer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agent.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Agent')


class TaskAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user
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

    def test_list_tasks(self):
        url = reverse('api:task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_task(self):
        url = reverse('api:task-list')
        data = {
            'crew': self.crew.id,
            'agent': self.agent.id,
            'name': 'New Task',
            'description': 'A new test task',
            'expected_output': 'Expected result',
            'context': ['Some context']
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Task')

    def test_task_dependencies(self):
        url = reverse('api:task-list')
        data = {
            'crew': self.crew.id,
            'agent': self.agent.id,
            'name': 'Dependent Task',
            'description': 'A dependent task',
            'expected_output': 'Expected result',
            'depends_on': [self.task.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(self.task.id, response.data['depends_on']) 