from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json
from django.conf import settings

User = get_user_model()


class CrewInstance(models.Model):
    """
    A CrewAI instance that can represent:
    - A single crew with agents and tasks
    - A flow coordinating multiple crews
    - Multiple independent crews
    - Multiple flows coordinating multiple crews
    """
    STATUS_CHOICES = (
        ('idle', 'Idle'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('stopped', 'Stopped'),
    )
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='crews')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_flow = models.BooleanField(
        default=False,
        help_text="Whether this instance represents a flow coordinating multiple crews"
    )
    parent_crew = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='sub_crews',
        help_text="Parent crew if this is part of a larger workflow"
    )
    config = models.JSONField(
        default=dict,
        help_text="Configuration including routing and state management for flows",
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_executed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Crew Instance'
        verbose_name_plural = 'Crew Instances'

    def __str__(self) -> str:
        base_str = f"{self.name} ({'Flow' if self.is_flow else 'Crew'})"
        if self.parent_crew:
            return f"{base_str} (Part of: {self.parent_crew.name})"
        return base_str

    @property
    def is_subcrew(self) -> bool:
        """Whether this crew is part of a larger workflow."""
        return self.parent_crew is not None

    @property
    def is_running(self):
        return self.status == 'running'
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    @property
    def status_class(self):
        status_classes = {
            'idle': 'secondary',
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'stopped': 'warning',
        }
        return status_classes.get(self.status, 'secondary')

    def clean(self):
        """Validate model data."""
        # Validate config is proper JSON
        if self.config:
            try:
                if isinstance(self.config, str):
                    json.loads(self.config)
            except json.JSONDecodeError:
                raise ValidationError({'config': 'Invalid JSON format'})
                
        # Prevent circular parent-child relationships
        if self.parent_crew and self.parent_crew.id == self.id:
            raise ValidationError({'parent_crew': 'A crew cannot be its own parent'})
            
        # Check for circular references in the hierarchy
        if self.parent_crew:
            parent = self.parent_crew
            while parent:
                if parent.parent_crew and parent.parent_crew.id == self.id:
                    raise ValidationError({'parent_crew': 'Circular crew hierarchy detected'})
                parent = parent.parent_crew
                
    def save(self, *args, **kwargs):
        """Override save to perform validation."""
        self.clean()
        super().save(*args, **kwargs)
        
    def execute(self):
        """
        Execute this crew instance using CrewAI.
        For flows, execute sub-crews in the defined order.
        """
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting execution of crew: {self.name}")
        
        try:
            if self.is_flow:
                # For flows, execute sub-crews in sequence or as defined in config
                logger.info(f"Executing flow: {self.name}")
                
                # Get all sub-crews
                sub_crews = self.sub_crews.all()
                if not sub_crews.exists():
                    logger.warning(f"Flow {self.name} has no sub-crews to execute.")
                    return
                
                # Check if execution order is specified in config
                execution_order = self.config.get('execution_order', [])
                if execution_order:
                    # Execute in specified order
                    for subcrew_id in execution_order:
                        try:
                            subcrew = self.sub_crews.get(id=subcrew_id)
                            subcrew.execute()
                        except CrewInstance.DoesNotExist:
                            logger.error(f"Could not find sub-crew with ID {subcrew_id}")
                        except Exception as e:
                            logger.error(f"Error executing sub-crew {subcrew_id}: {str(e)}")
                else:
                    # Execute all sub-crews in sequence
                    for subcrew in sub_crews:
                        try:
                            subcrew.execute()
                        except Exception as e:
                            logger.error(f"Error executing sub-crew {subcrew.id}: {str(e)}")
            else:
                # For regular crews, create a CrewAI instance
                try:
                    # Placeholder for CrewAI integration
                    # This is where we would create a CrewAI Crew instance
                    # and execute it with the configured agents and tasks
                    
                    # Import CrewAI (assuming it's installed)
                    from crewai import Crew, Agent, Task as CrewAITask
                    
                    # Create CrewAI agents from our Agent models
                    agents = []
                    for agent_model in self.agents.all():
                        agent = agent_model.create_crewai_agent()
                        if agent:
                            agents.append(agent)
                    
                    if not agents:
                        logger.warning(f"Crew {self.name} has no agents to execute.")
                        return
                    
                    # Create CrewAI tasks from our Task models
                    tasks = []
                    task_mapping = {}  # Map our Task models to CrewAI Task objects
                    
                    for task_model in self.tasks.all():
                        if task_model.status != 'pending':
                            continue
                            
                        # Update status to in_progress
                        task_model.status = 'in_progress'
                        task_model.started_at = timezone.now()
                        task_model.save()
                        
                        # Create CrewAI task
                        crewai_task = task_model.create_crewai_task()
                        if crewai_task:
                            tasks.append(crewai_task)
                            task_mapping[crewai_task] = task_model
                    
                    if not tasks:
                        logger.warning(f"Crew {self.name} has no tasks to execute.")
                        return
                    
                    # Create and run the CrewAI Crew
                    crew = Crew(
                        agents=agents,
                        tasks=tasks,
                        verbose=self.config.get('verbose', True)
                    )
                    
                    # Execute the crew
                    results = crew.kickoff()
                    
                    # Process results and update task models
                    for i, result in enumerate(results):
                        if i < len(tasks):
                            crewai_task = tasks[i]
                            task_model = task_mapping.get(crewai_task)
                            if task_model:
                                task_model.status = 'completed'
                                task_model.output_data = {'result': result}
                                task_model.completed_at = timezone.now()
                                task_model.save()
                                
                    logger.info(f"Successfully executed crew: {self.name}")
                    
                except ImportError:
                    logger.error("CrewAI library not installed")
                except Exception as e:
                    logger.error(f"Error executing crew {self.name}: {str(e)}")
                    raise
                
        except Exception as e:
            logger.error(f"Failed to execute crew {self.name}: {str(e)}")
            raise


class Agent(models.Model):
    """An AI agent with specific role and capabilities within a crew."""
    ROLE_CHOICES = [
        ('researcher', 'Researcher'),
        ('writer', 'Writer'),
        ('editor', 'Editor'),
        ('reviewer', 'Reviewer'),
        ('custom', 'Custom'),
    ]

    crew = models.ForeignKey(CrewInstance, on_delete=models.CASCADE, related_name='agents')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    custom_role = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    goals = models.JSONField(default=list)
    backstory = models.TextField(blank=True)
    tools = models.JSONField(
        default=list,
        help_text="List of tools available to this agent"
    )
    allow_delegation = models.BooleanField(default=True)
    verbose = models.BooleanField(default=False)
    llm_config = models.JSONField(
        default=dict,
        help_text="Configuration for the LLM used by this agent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['crew', 'role', 'name']
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self) -> str:
        return f"{self.name} ({self.get_role_display()} in {self.crew.name})"

    @property
    def effective_role(self) -> str:
        """Returns the custom role if set, otherwise returns the standard role."""
        return self.custom_role if self.role == 'custom' else self.get_role_display()
        
    def clean(self):
        """Validate model data."""
        from django.core.exceptions import ValidationError
        
        # Validate custom_role is provided when role is 'custom'
        if self.role == 'custom' and not self.custom_role:
            raise ValidationError({'custom_role': 'Custom role name is required when role is set to custom'})
            
        # Validate goals is a list
        if not isinstance(self.goals, list):
            raise ValidationError({'goals': 'Goals must be a list'})
            
        # Validate tools is a list
        if not isinstance(self.tools, list):
            raise ValidationError({'tools': 'Tools must be a list'})
            
        # Validate llm_config is a dict
        if not isinstance(self.llm_config, dict):
            raise ValidationError({'llm_config': 'LLM configuration must be a dictionary'})
            
        # Check if required LLM config properties are present
        if self.llm_config and not self.llm_config.get('model'):
            raise ValidationError({'llm_config': 'LLM configuration must include a model name'})
            
    def save(self, *args, **kwargs):
        """Override save to perform validation."""
        self.clean()
        super().save(*args, **kwargs)
        
    def create_crewai_agent(self):
        """
        Create a CrewAI Agent instance from this model.
        
        Returns:
            crewai.Agent: A CrewAI Agent instance
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Import CrewAI (assuming it's installed)
            from crewai import Agent as CrewAIAgent
            
            # Create and return a CrewAI Agent instance
            agent = CrewAIAgent(
                role=self.effective_role,
                goal=self.goals[0] if self.goals else "Complete assigned tasks",
                backstory=self.backstory,
                verbose=self.verbose,
                allow_delegation=self.allow_delegation,
                # Convert JSON config to proper kwargs
                **self.llm_config
            )
            
            # If additional goals exist, add them as secondary goals
            if len(self.goals) > 1:
                agent.secondary_goals = self.goals[1:]
            
            # If tools are specified, add them
            if self.tools:
                # Note: This assumes tools are properly formatted for CrewAI
                agent.tools = self.tools
                
            return agent
            
        except ImportError:
            logger.error("CrewAI library not installed")
            return None
        except Exception as e:
            logger.error(f"Error creating CrewAI agent for {self.name}: {str(e)}")
            return None


class Task(models.Model):
    """A task assigned to an agent within a crew."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    crew = models.ForeignKey(CrewInstance, on_delete=models.CASCADE, related_name='tasks')
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    expected_output = models.TextField(
        help_text="Description of what this task should produce"
    )
    context = models.JSONField(
        default=list,
        help_text="List of related tasks that provide context"
    )
    depends_on = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_tasks',
        help_text="Tasks that must be completed before this one can start"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    output_file = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path to file where task output should be saved"
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self) -> str:
        return f"{self.name} ({self.status} - {self.agent.name})"
        
    def clean(self):
        """Validate model data."""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # Validate agent belongs to the same crew
        if self.agent and self.crew and self.agent.crew.id != self.crew.id:
            raise ValidationError({'agent': 'Agent must belong to the same crew as the task'})
            
        # Validate context is a list
        if not isinstance(self.context, list):
            raise ValidationError({'context': 'Context must be a list'})
            
        # Validate input_data and output_data are dictionaries
        if not isinstance(self.input_data, dict):
            raise ValidationError({'input_data': 'Input data must be a dictionary'})
            
        if not isinstance(self.output_data, dict):
            raise ValidationError({'output_data': 'Output data must be a dictionary'})
            
        # Validate timestamps make sense
        if self.started_at and self.completed_at and self.started_at > self.completed_at:
            raise ValidationError({'completed_at': 'Completion time cannot be earlier than start time'})
            
        # Completed tasks must have output_data or output_file
        if self.status == 'completed' and not (self.output_data or self.output_file):
            raise ValidationError({'status': 'Completed tasks must have output data or an output file'})
            
        # Failed tasks must have an error message
        if self.status == 'failed' and not self.error_message:
            raise ValidationError({'error_message': 'Failed tasks must have an error message'})
            
    def save(self, *args, **kwargs):
        """Override save to perform validation and update timestamps."""
        from django.utils import timezone
        
        # Set started_at if status changing to in_progress
        if self.status == 'in_progress' and not self.started_at:
            self.started_at = timezone.now()
            
        # Set completed_at if status changing to completed or failed
        if self.status in ['completed', 'failed'] and not self.completed_at:
            self.completed_at = timezone.now()
            
        self.clean()
        super().save(*args, **kwargs)
        
    def create_crewai_task(self):
        """
        Create a CrewAI Task instance from this model.
        
        Returns:
            crewai.Task: A CrewAI Task instance
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Import CrewAI (assuming it's installed)
            from crewai import Task as CrewAITask
            
            # Find the CrewAI Agent object for our agent
            crewai_agent = self.agent.create_crewai_agent()
            if not crewai_agent:
                logger.error(f"Could not create CrewAI agent for task {self.name}")
                return None
                
            # Create the task
            task = CrewAITask(
                description=self.description,
                expected_output=self.expected_output,
                agent=crewai_agent,
                context=self.context,
                async_execution=False
            )
            
            return task
            
        except ImportError:
            logger.error("CrewAI library not installed")
            return None
        except Exception as e:
            logger.error(f"Error creating CrewAI task for {self.name}: {str(e)}")
            return None
        
    def execute(self):
        """
        Execute this task using CrewAI.
        Updates the status, output_data, and error_message.
        """
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting execution of task: {self.name}")
        
        # Validate dependencies
        if not self.check_dependencies_complete():
            msg = f"Cannot execute task {self.name} because dependencies are not complete."
            logger.error(msg)
            self.status = 'failed'
            self.error_message = msg
            self.completed_at = timezone.now()
            self.save()
            return
            
        try:
            # Update status to in_progress
            self.status = 'in_progress'
            self.started_at = timezone.now()
            self.save()
            
            # Import CrewAI (assuming it's installed)
            from crewai import Crew, Task as CrewAITask
            
            # Create CrewAI agent
            agent = self.agent.create_crewai_agent()
            if not agent:
                raise ValueError(f"Failed to create CrewAI agent for {self.agent.name}")
                
            # Create CrewAI task
            task = self.create_crewai_task()
            if not task:
                raise ValueError(f"Failed to create CrewAI task for {self.name}")
                
            # Create a simple Crew with just this task
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )
            
            # Execute the crew to run the task
            results = crew.kickoff()
            
            # Process results
            if results and len(results) > 0:
                result = results[0]
                
                # Update task status
                self.status = 'completed'
                self.output_data = {'result': result}
                self.completed_at = timezone.now()
                self.save()
                
                logger.info(f"Successfully executed task: {self.name}")
            else:
                raise ValueError("No results returned from CrewAI execution")
                
        except ImportError:
            msg = "CrewAI library not installed"
            logger.error(msg)
            self.status = 'failed'
            self.error_message = msg
            self.completed_at = timezone.now()
            self.save()
        except Exception as e:
            msg = f"Error executing task: {str(e)}"
            logger.error(msg)
            self.status = 'failed'
            self.error_message = msg
            self.completed_at = timezone.now()
            self.save()
            raise
        
    def check_dependencies_complete(self):
        """
        Check if all dependencies are complete.
        
        Returns:
            bool: True if all dependencies are complete, False otherwise
        """
        return all(task.status == 'completed' for task in self.depends_on.all())


class Execution(models.Model):
    """
    Records details of a specific crew execution
    """
    STATUS_CHOICES = (
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('stopped', 'Stopped'),
    )
    
    crew = models.ForeignKey(CrewInstance, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    results = models.JSONField(default=dict, blank=True)
    
    @property
    def duration(self):
        if self.ended_at and self.started_at:
            return self.ended_at - self.started_at
        return None
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    @property
    def status_class(self):
        status_classes = {
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'stopped': 'warning',
        }
        return status_classes.get(self.status, 'secondary')
    
    def __str__(self):
        return f"Execution {self.id} of {self.crew.name}"
