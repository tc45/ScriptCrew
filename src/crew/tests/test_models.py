from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from crew.models import CrewInstance, Agent, Task
import json

User = get_user_model()


class CrewInstanceModelTest(TestCase):
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
        self.flow = CrewInstance.objects.create(
            name='Test Flow',
            description='A test flow',
            owner=self.user,
            is_flow=True
        )
        self.subcrew = CrewInstance.objects.create(
            name='Test Subcrew',
            description='A test subcrew',
            owner=self.user,
            parent_crew=self.flow
        )

    def test_crew_creation(self):
        self.assertEqual(self.crew.name, 'Test Crew')
        self.assertEqual(self.crew.owner, self.user)
        self.assertFalse(self.crew.is_flow)
        self.assertFalse(self.crew.is_subcrew)

    def test_flow_creation(self):
        self.assertEqual(self.flow.name, 'Test Flow')
        self.assertTrue(self.flow.is_flow)

    def test_subcrew_creation(self):
        self.assertEqual(self.subcrew.name, 'Test Subcrew')
        self.assertEqual(self.subcrew.parent_crew, self.flow)
        self.assertTrue(self.subcrew.is_subcrew)
        
    def test_string_representation(self):
        self.assertEqual(str(self.crew), 'Test Crew (Crew)')
        self.assertEqual(str(self.flow), 'Test Flow (Flow)')
        self.assertEqual(str(self.subcrew), 'Test Subcrew (Crew) (Part of: Test Flow)')
        
    def test_invalid_config_json(self):
        with self.assertRaises(ValidationError):
            crew = CrewInstance(
                name='Invalid JSON Crew',
                description='A crew with invalid JSON config',
                owner=self.user,
                config='{"invalid": json}'
            )
            crew.clean()
            
    def test_circular_parent_reference(self):
        with self.assertRaises(ValidationError):
            # Try to set a crew as its own parent
            self.crew.parent_crew = self.crew
            self.crew.clean()
        
        # Reset and test deep circular reference
        self.crew.parent_crew = None
        self.crew.save()
        
        with self.assertRaises(ValidationError):
            # Create circular reference through intermediary
            self.flow.parent_crew = self.subcrew
            self.flow.clean()


class AgentModelTest(TestCase):
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
            goals=['Research AI topics', 'Summarize findings'],
            backstory='An advanced AI researcher',
            llm_config={'model': 'gpt-4'}
        )
        self.custom_agent = Agent.objects.create(
            crew=self.crew,
            name='Custom Agent',
            role='custom',
            custom_role='Special Analyst',
            description='A custom agent with special role',
            goals=['Analyze data', 'Create visualizations'],
            backstory='Experienced data analyst',
            llm_config={'model': 'gpt-4'}
        )

    def test_agent_creation(self):
        self.assertEqual(self.agent.name, 'Test Agent')
        self.assertEqual(self.agent.crew, self.crew)
        self.assertEqual(self.agent.role, 'researcher')
        self.assertEqual(self.agent.goals, ['Research AI topics', 'Summarize findings'])

    def test_agent_effective_role(self):
        # Standard role should return the display name
        self.assertEqual(self.agent.effective_role, 'Researcher')
        
        # Custom role should return the custom_role field
        self.assertEqual(self.custom_agent.effective_role, 'Special Analyst')
        
    def test_string_representation(self):
        self.assertEqual(str(self.agent), 'Test Agent (Researcher in Test Crew)')
        self.assertEqual(str(self.custom_agent), 'Custom Agent (Custom in Test Crew)')
        
    def test_missing_custom_role(self):
        with self.assertRaises(ValidationError):
            agent = Agent(
                crew=self.crew,
                name='Invalid Custom Agent',
                role='custom',  # Custom role but no custom_role provided
                description='An agent with invalid role config',
                goals=['Goal 1'],
                llm_config={'model': 'gpt-4'}
            )
            agent.clean()
            
    def test_invalid_goals_format(self):
        with self.assertRaises(ValidationError):
            agent = Agent(
                crew=self.crew,
                name='Invalid Goals Agent',
                role='researcher',
                description='An agent with invalid goals format',
                goals='Not a list',  # Should be a list
                llm_config={'model': 'gpt-4'}
            )
            agent.clean()
            
    def test_invalid_llm_config(self):
        with self.assertRaises(ValidationError):
            agent = Agent(
                crew=self.crew,
                name='Invalid LLM Config Agent',
                role='researcher',
                description='An agent with invalid LLM config',
                goals=['Goal 1'],
                llm_config=[]  # Should be a dict
            )
            agent.clean()
            
        with self.assertRaises(ValidationError):
            agent = Agent(
                crew=self.crew,
                name='Missing Model Agent',
                role='researcher',
                description='An agent with missing model in LLM config',
                goals=['Goal 1'],
                llm_config={}  # Missing required 'model' key
            )
            agent.clean()


class TaskModelTest(TestCase):
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
            goals=['Research topics'],
            llm_config={'model': 'gpt-4'}
        )
        self.task1 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 1',
            description='First task',
            expected_output='Research report',
            input_data={'query': 'AI trends'}
        )
        self.task2 = Task.objects.create(
            crew=self.crew,
            agent=self.agent,
            name='Task 2',
            description='Second task',
            expected_output='Summary of research',
            input_data={'source': 'Task 1 output'}
        )
        self.task2.depends_on.add(self.task1)

    def test_task_creation(self):
        self.assertEqual(self.task1.name, 'Task 1')
        self.assertEqual(self.task1.crew, self.crew)
        self.assertEqual(self.task1.agent, self.agent)
        self.assertEqual(self.task1.status, 'pending')

    def test_task_dependencies(self):
        self.assertIn(self.task1, self.task2.depends_on.all())
        self.assertIn(self.task2, self.task1.dependent_tasks.all())
        
    def test_string_representation(self):
        self.assertEqual(str(self.task1), 'Task 1 (pending - Test Agent)')
        
    def test_check_dependencies_complete(self):
        # Initially, dependencies are not complete
        self.assertFalse(self.task2.check_dependencies_complete())
        
        # Mark dependency as complete
        self.task1.status = 'completed'
        self.task1.output_data = {'result': 'AI research findings'}
        self.task1.save()
        
        # Now dependencies should be complete
        self.assertTrue(self.task2.check_dependencies_complete())
        
    def test_status_transition_timestamps(self):
        # Start task
        self.task1.status = 'in_progress'
        self.task1.save()
        
        # Should have a started_at timestamp now
        self.assertIsNotNone(self.task1.started_at)
        self.assertIsNone(self.task1.completed_at)
        
        # Complete task
        self.task1.status = 'completed'
        self.task1.output_data = {'result': 'Research completed'}
        self.task1.save()
        
        # Should have a completed_at timestamp now
        self.assertIsNotNone(self.task1.completed_at)
        
    def test_status_validation(self):
        # Cannot mark task as completed without output
        with self.assertRaises(ValidationError):
            self.task1.status = 'completed'
            self.task1.clean()
            
        # Cannot mark task as failed without error message
        with self.assertRaises(ValidationError):
            self.task1.status = 'failed'
            self.task1.clean()
            
    def test_agent_crew_validation(self):
        # Create a new crew
        other_crew = CrewInstance.objects.create(
            name='Other Crew',
            description='Another crew',
            owner=self.user
        )
        
        # Try to create a task with agent from different crew
        with self.assertRaises(ValidationError):
            task = Task(
                crew=other_crew,  # Different crew
                agent=self.agent,  # Agent belongs to self.crew
                name='Invalid Task',
                description='Task with mismatched crew/agent',
                expected_output='Should fail validation',
                input_data={'data': 'test'}
            )
            task.clean() 