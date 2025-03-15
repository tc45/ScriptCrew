from django.test import TestCase
from django.contrib.auth import get_user_model
from crew.models import CrewInstance, Agent, Task
from api.serializers import CrewInstanceSerializer, AgentSerializer, TaskSerializer

User = get_user_model()


class CrewInstanceSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.crew_data = {
            'name': 'Test Crew',
            'description': 'A test crew',
            'owner': self.user.id,
            'is_flow': False,
            'configuration': {'key': 'value'},
            'goals': ['Goal 1', 'Goal 2']
        }
        self.crew = CrewInstance.objects.create(
            name='Existing Crew',
            description='An existing crew',
            owner=self.user
        )
        self.serializer = CrewInstanceSerializer()

    def test_contains_expected_fields(self):
        data = self.serializer.to_representation(self.crew)
        expected_fields = {
            'id', 'name', 'description', 'owner', 'is_flow',
            'is_subcrew', 'parent_crew', 'configuration', 'goals',
            'agent_count', 'subcrew_count', 'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_validate_crew_data(self):
        serializer = CrewInstanceSerializer(data=self.crew_data)
        self.assertTrue(serializer.is_valid())

    def test_validate_invalid_crew_data(self):
        invalid_data = self.crew_data.copy()
        invalid_data['name'] = ''  # Name is required
        serializer = CrewInstanceSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class AgentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user
        )
        self.agent_data = {
            'crew': self.crew.id,
            'name': 'Test Agent',
            'role': 'researcher',
            'description': 'A test agent',
            'goals': ['Research topics'],
            'backstory': 'Expert researcher',
            'configuration': {'temperature': 0.7}
        }
        self.agent = Agent.objects.create(
            crew=self.crew,
            name='Existing Agent',
            role='writer',
            description='An existing agent'
        )
        self.serializer = AgentSerializer()

    def test_contains_expected_fields(self):
        data = self.serializer.to_representation(self.agent)
        expected_fields = {
            'id', 'crew', 'name', 'role', 'description',
            'goals', 'backstory', 'configuration',
            'task_count', 'effective_role', 'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_validate_agent_data(self):
        serializer = AgentSerializer(data=self.agent_data)
        self.assertTrue(serializer.is_valid())

    def test_validate_invalid_agent_data(self):
        invalid_data = self.agent_data.copy()
        invalid_data['role'] = ''  # Role is required
        serializer = AgentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)


class TaskSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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
        self.task_data = {
            'crew': self.crew.id,
            'agent': self.agent.id,
            'name': 'Test Task',
            'description': 'A test task',
            'expected_output': 'Expected result',
            'context': ['Context 1'],
            'status': 'pending'
        }
        self.task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Existing Task',
            description='An existing task',
            expected_output='Expected result'
        )
        self.serializer = TaskSerializer()

    def test_contains_expected_fields(self):
        data = self.serializer.to_representation(self.task)
        expected_fields = {
            'id', 'crew', 'agent', 'name', 'description',
            'expected_output', 'actual_output', 'context',
            'status', 'depends_on', 'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_validate_task_data(self):
        serializer = TaskSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())

    def test_validate_invalid_task_data(self):
        invalid_data = self.task_data.copy()
        invalid_data['agent'] = None  # Agent is required
        serializer = TaskSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('agent', serializer.errors)

    def test_validate_task_dependencies(self):
        dependent_task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Dependent Task',
            description='A dependent task',
            expected_output='Expected result',
            depends_on=[self.task]
        )
        data = self.serializer.to_representation(dependent_task)
        self.assertIn(self.task.id, data['depends_on']) 