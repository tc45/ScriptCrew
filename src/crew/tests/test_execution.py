from django.test import TestCase
from django.contrib.auth import get_user_model
from crew.models import CrewInstance, Agent, Task
from crew.execution import CrewExecutor, TaskExecutor

User = get_user_model()


class CrewExecutorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.crew = CrewInstance.objects.create(
            name='Test Crew',
            description='A test crew',
            owner=self.user,
            configuration={'temperature': 0.7}
        )
        self.agent = Agent.objects.create(
            crew=self.crew,
            name='Test Agent',
            role='researcher',
            description='A test agent',
            goals=['Research topics'],
            configuration={'model': 'gpt-4'}
        )
        self.task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Test Task',
            description='A test task',
            expected_output='Expected result'
        )
        self.executor = CrewExecutor(self.crew)

    def test_crew_initialization(self):
        self.assertEqual(self.executor.crew, self.crew)
        self.assertEqual(len(self.executor.get_agents()), 1)
        self.assertEqual(len(self.executor.get_tasks()), 1)

    def test_task_dependency_resolution(self):
        dependent_task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Dependent Task',
            description='A dependent task',
            expected_output='Expected result',
            depends_on=[self.task]
        )
        task_order = self.executor.get_execution_order()
        self.assertEqual(len(task_order), 2)
        self.assertEqual(task_order[0], self.task)
        self.assertEqual(task_order[1], dependent_task)

    def test_crew_execution_flow(self):
        self.executor.initialize()
        status = self.executor.execute()
        self.assertTrue(status['success'])
        self.assertEqual(len(status['completed_tasks']), 1)
        self.assertEqual(len(status['failed_tasks']), 0)

    def test_crew_context_sharing(self):
        task_output = 'Research findings'
        self.task.actual_output = task_output
        self.task.status = 'completed'
        self.task.save()

        dependent_task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Dependent Task',
            description='Use research findings',
            expected_output='Analysis',
            depends_on=[self.task]
        )
        context = self.executor.get_task_context(dependent_task)
        self.assertIn(task_output, str(context))


class TaskExecutorTest(TestCase):
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
            description='A test agent',
            goals=['Research topics']
        )
        self.task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Test Task',
            description='A test task',
            expected_output='Expected result',
            context=['Initial context']
        )
        self.executor = TaskExecutor(self.task)

    def test_task_initialization(self):
        self.assertEqual(self.executor.task, self.task)
        self.assertEqual(self.executor.agent, self.agent)

    def test_task_execution(self):
        result = self.executor.execute()
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['output'])
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_task_failure_handling(self):
        self.task.description = ''  # Invalid task description
        self.task.save()
        result = self.executor.execute()
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'failed')

    def test_task_context_processing(self):
        context = self.executor.get_context()
        self.assertIn('Initial context', context)
        
        # Test context from dependent tasks
        dependent_task = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Parent Task',
            description='Parent task',
            expected_output='Parent result',
            actual_output='Parent output'
        )
        self.task.depends_on.add(dependent_task)
        
        context = self.executor.get_context()
        self.assertIn('Parent output', context) 