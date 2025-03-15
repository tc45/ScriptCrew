from django.test import TestCase
from django.contrib.auth import get_user_model
from crew.models import CrewInstance, Agent, Task
from crew.utils import (
    validate_configuration,
    format_task_context,
    resolve_dependencies,
    calculate_task_metrics
)

User = get_user_model()


class ConfigurationValidationTest(TestCase):
    def test_valid_configuration(self):
        config = {
            'temperature': 0.7,
            'model': 'gpt-4',
            'max_tokens': 1000
        }
        result = validate_configuration(config)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)

    def test_invalid_configuration(self):
        config = {
            'temperature': 'invalid',
            'model': None,
            'max_tokens': -1
        }
        result = validate_configuration(config)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)

    def test_missing_required_fields(self):
        config = {
            'temperature': 0.7
        }
        result = validate_configuration(config, required_fields=['model'])
        self.assertFalse(result['valid'])
        self.assertIn('model', result['errors'])


class TaskContextFormattingTest(TestCase):
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

    def test_format_task_context(self):
        task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Test Task',
            description='A test task',
            context=['Context 1', 'Context 2']
        )
        formatted_context = format_task_context(task)
        self.assertIn('Context 1', formatted_context)
        self.assertIn('Context 2', formatted_context)
        self.assertIn(task.description, formatted_context)

    def test_format_task_context_with_dependencies(self):
        parent_task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Parent Task',
            description='Parent task',
            actual_output='Parent result'
        )
        child_task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Child Task',
            description='Child task',
            depends_on=[parent_task]
        )
        formatted_context = format_task_context(child_task)
        self.assertIn('Parent result', formatted_context)
        self.assertIn(child_task.description, formatted_context)


class DependencyResolutionTest(TestCase):
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

    def test_resolve_dependencies(self):
        task1 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 1',
            description='First task'
        )
        task2 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 2',
            description='Second task',
            depends_on=[task1]
        )
        task3 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 3',
            description='Third task',
            depends_on=[task2]
        )

        order = resolve_dependencies([task1, task2, task3])
        self.assertEqual(len(order), 3)
        self.assertEqual(order[0], task1)
        self.assertEqual(order[1], task2)
        self.assertEqual(order[2], task3)

    def test_circular_dependency_detection(self):
        task1 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 1',
            description='First task'
        )
        task2 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 2',
            description='Second task',
            depends_on=[task1]
        )
        task1.depends_on.add(task2)

        with self.assertRaises(ValueError):
            resolve_dependencies([task1, task2])


class TaskMetricsTest(TestCase):
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

    def test_calculate_task_metrics(self):
        task1 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 1',
            description='First task',
            status='completed'
        )
        task2 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 2',
            description='Second task',
            status='failed'
        )
        task3 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 3',
            description='Third task',
            status='pending'
        )

        metrics = calculate_task_metrics(self.crew)
        self.assertEqual(metrics['total_tasks'], 3)
        self.assertEqual(metrics['completed_tasks'], 1)
        self.assertEqual(metrics['failed_tasks'], 1)
        self.assertEqual(metrics['pending_tasks'], 1)
        self.assertAlmostEqual(metrics['success_rate'], 0.5) 