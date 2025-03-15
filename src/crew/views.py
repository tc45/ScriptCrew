from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
import json
from django.core.exceptions import ValidationError
from .models import CrewInstance, Agent, Task


class JSONFormMixin:
    """Mixin for handling JSON fields in forms."""
    
    def get_form(self, form_class=None):
        """Process JSON fields in forms."""
        form = super().get_form(form_class)
        
        # Define JSON fields for each model
        json_fields = {
            'CrewInstance': ['config'],
            'Agent': ['goals', 'tools', 'llm_config'],
            'Task': ['context', 'input_data', 'output_data']
        }
        
        # Get model name
        model_name = self.model.__name__
        
        if model_name in json_fields:
            for field_name in json_fields[model_name]:
                if field_name in form.fields:
                    form.fields[field_name].widget.attrs.update({
                        'class': 'json-editor',
                        'rows': 10,
                    })
        
        return form
    
    def form_valid(self, form):
        """Validate and process JSON fields before saving."""
        # Define JSON fields for each model
        json_fields = {
            'CrewInstance': ['config'],
            'Agent': ['goals', 'tools', 'llm_config'],
            'Task': ['context', 'input_data', 'output_data']
        }
        
        # Get model name
        model_name = self.model.__name__
        
        if model_name in json_fields:
            for field_name in json_fields[model_name]:
                if field_name in form.cleaned_data and isinstance(form.cleaned_data[field_name], str):
                    try:
                        # Convert string to Python object
                        form.instance.__dict__[field_name] = json.loads(form.cleaned_data[field_name])
                    except json.JSONDecodeError:
                        form.add_error(field_name, 'Invalid JSON format')
                        return self.form_invalid(form)
        
        return super().form_valid(form)


class CrewListView(LoginRequiredMixin, ListView):
    model = CrewInstance
    template_name = 'crew/crew_list.html'
    context_object_name = 'crew_list'

    def get_queryset(self):
        return CrewInstance.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'crew'
        context['title'] = 'Crews'
        context['list_display'] = ['name', 'is_flow', 'created_at']
        context['create_url'] = reverse_lazy('crew:crew_create')
        context['detail_url_name'] = 'crew:crew_detail'
        context['update_url_name'] = 'crew:crew_update'
        context['delete_url_name'] = 'crew:crew_delete'
        return context


class CrewDetailView(LoginRequiredMixin, DetailView):
    model = CrewInstance
    template_name = 'crew/crew_detail.html'
    context_object_name = 'crew'

    def get_queryset(self):
        return CrewInstance.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'crew'
        context['title'] = f"Crew: {self.object.name}"
        context['update_url'] = reverse_lazy('crew:crew_update', kwargs={'pk': self.object.pk})
        context['delete_url'] = reverse_lazy('crew:crew_delete', kwargs={'pk': self.object.pk})
        context['list_url'] = reverse_lazy('crew:crew_list')
        
        # Add related objects
        context['agents'] = self.object.agents.all()
        context['tasks'] = self.object.tasks.all()
        context['sub_crews'] = self.object.sub_crews.all() if self.object.is_flow else None
        
        return context


class CrewCreateView(LoginRequiredMixin, JSONFormMixin, CreateView):
    model = CrewInstance
    template_name = 'crew/crew_form.html'
    fields = ['name', 'description', 'config', 'is_flow', 'parent_crew']
    success_url = reverse_lazy('crew:crew_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'crew'
        context['title'] = 'Create Crew'
        context['submit_text'] = 'Create'
        context['cancel_url'] = reverse_lazy('crew:crew_list')
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Crew created successfully!')
        return super().form_valid(form)


class CrewUpdateView(LoginRequiredMixin, JSONFormMixin, UpdateView):
    model = CrewInstance
    template_name = 'crew/crew_form.html'
    fields = ['name', 'description', 'config', 'is_flow', 'parent_crew']

    def get_queryset(self):
        return CrewInstance.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'crew'
        context['title'] = f"Edit Crew: {self.object.name}"
        context['submit_text'] = 'Update'
        context['cancel_url'] = reverse_lazy('crew:crew_detail', kwargs={'pk': self.object.pk})
        return context

    def get_success_url(self):
        return reverse_lazy('crew:crew_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Crew updated successfully!')
        return super().form_valid(form)


class CrewDeleteView(LoginRequiredMixin, DeleteView):
    model = CrewInstance
    template_name = 'crew/crew_confirm_delete.html'
    success_url = reverse_lazy('crew:crew_list')

    def get_queryset(self):
        return CrewInstance.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'crew'
        context['title'] = f"Delete Crew: {self.object.name}"
        context['cancel_url'] = reverse_lazy('crew:crew_detail', kwargs={'pk': self.object.pk})
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Crew deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AgentListView(LoginRequiredMixin, ListView):
    model = Agent
    template_name = 'crew/agent_list.html'
    context_object_name = 'agent_list'

    def get_queryset(self):
        # Get agents associated with the user's crews
        return Agent.objects.filter(crew__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'agent'
        context['title'] = 'Agents'
        context['list_display'] = ['name', 'crew', 'role', 'created_at']
        context['create_url'] = reverse_lazy('crew:agent_create')
        context['detail_url_name'] = 'crew:agent_detail'
        context['update_url_name'] = 'crew:agent_update'
        context['delete_url_name'] = 'crew:agent_delete'
        return context


class AgentDetailView(LoginRequiredMixin, DetailView):
    model = Agent
    template_name = 'crew/agent_detail.html'
    context_object_name = 'agent'

    def get_queryset(self):
        return Agent.objects.filter(crew__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'agent'
        context['title'] = f"Agent: {self.object.name}"
        context['update_url'] = reverse_lazy('crew:agent_update', kwargs={'pk': self.object.pk})
        context['delete_url'] = reverse_lazy('crew:agent_delete', kwargs={'pk': self.object.pk})
        context['list_url'] = reverse_lazy('crew:agent_list')
        
        # Add related objects
        context['tasks'] = self.object.tasks.all()
        
        return context


class AgentCreateView(LoginRequiredMixin, JSONFormMixin, CreateView):
    model = Agent
    template_name = 'crew/agent_form.html'
    fields = ['name', 'crew', 'role', 'custom_role', 'description', 'backstory', 
              'goals', 'tools', 'llm_config', 'allow_delegation', 'verbose']
    success_url = reverse_lazy('crew:agent_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit crew choices to those owned by the user
        form.fields['crew'].queryset = CrewInstance.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Agent created successfully!')
        return super().form_valid(form)


class AgentUpdateView(LoginRequiredMixin, JSONFormMixin, UpdateView):
    model = Agent
    template_name = 'crew/agent_form.html'
    fields = ['name', 'crew', 'role', 'custom_role', 'description', 'backstory', 
              'goals', 'tools', 'llm_config', 'allow_delegation', 'verbose']

    def get_queryset(self):
        return Agent.objects.filter(crew__owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit crew choices to those owned by the user
        form.fields['crew'].queryset = CrewInstance.objects.filter(owner=self.request.user)
        return form

    def get_success_url(self):
        return reverse_lazy('crew:agent_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Agent updated successfully!')
        return super().form_valid(form)


class AgentDeleteView(LoginRequiredMixin, DeleteView):
    model = Agent
    template_name = 'crew/agent_confirm_delete.html'
    success_url = reverse_lazy('crew:agent_list')

    def get_queryset(self):
        return Agent.objects.filter(crew__owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Agent deleted successfully!')
        return super().delete(request, *args, **kwargs)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'crew/task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.filter(crew__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'task'
        context['title'] = 'Tasks'
        context['list_display'] = ['name', 'crew', 'agent', 'status', 'created_at']
        context['create_url'] = reverse_lazy('crew:task_create')
        context['detail_url_name'] = 'crew:task_detail'
        context['update_url_name'] = 'crew:task_update'
        context['delete_url_name'] = 'crew:task_delete'
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'crew/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(crew__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'task'
        context['title'] = f"Task: {self.object.name}"
        context['update_url'] = reverse_lazy('crew:task_update', kwargs={'pk': self.object.pk})
        context['delete_url'] = reverse_lazy('crew:task_delete', kwargs={'pk': self.object.pk})
        context['list_url'] = reverse_lazy('crew:task_list')
        
        # Add related objects
        context['dependent_tasks'] = self.object.dependent_tasks.all()
        context['dependencies'] = self.object.depends_on.all()
        
        return context


class TaskCreateView(LoginRequiredMixin, JSONFormMixin, CreateView):
    model = Task
    template_name = 'crew/task_form.html'
    fields = ['crew', 'agent', 'name', 'description', 'expected_output',
              'context', 'input_data', 'output_file']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'task'
        context['title'] = 'Create Task'
        context['submit_text'] = 'Create'
        context['cancel_url'] = reverse_lazy('crew:task_list')
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit crew choices to those owned by the current user
        form.fields['crew'].queryset = CrewInstance.objects.filter(owner=self.request.user)
        
        # Initially disable agent field - will be populated via AJAX when crew is selected
        form.fields['agent'].queryset = Agent.objects.none()
        
        # If crew is already selected, populate agent choices
        if form.instance.crew_id:
            form.fields['agent'].queryset = Agent.objects.filter(crew_id=form.instance.crew_id)
            
        return form

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Task created successfully.')
            return response
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    form.add_error(field, error)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('crew:task_detail', kwargs={'pk': self.object.pk})


class TaskUpdateView(LoginRequiredMixin, JSONFormMixin, UpdateView):
    model = Task
    template_name = 'crew/task_form.html'
    fields = ['crew', 'agent', 'name', 'description', 'expected_output',
              'context', 'depends_on', 'status', 'input_data', 'output_data',
              'error_message', 'output_file']

    def get_queryset(self):
        return Task.objects.filter(crew__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'task'
        context['title'] = f"Edit Task: {self.object.name}"
        context['submit_text'] = 'Update'
        context['cancel_url'] = reverse_lazy('crew:task_detail', kwargs={'pk': self.object.pk})
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit crew choices to those owned by the current user
        form.fields['crew'].queryset = CrewInstance.objects.filter(owner=self.request.user)
        
        # Limit agent choices to those in the selected crew
        if form.instance.crew_id:
            form.fields['agent'].queryset = Agent.objects.filter(crew_id=form.instance.crew_id)
        else:
            form.fields['agent'].queryset = Agent.objects.none()
            
        # Limit dependency choices to avoid circular dependencies
        if form.instance.pk:
            form.fields['depends_on'].queryset = Task.objects.filter(
                crew__owner=self.request.user
            ).exclude(pk=form.instance.pk)
        
        return form

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Task updated successfully.')
            return response
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    form.add_error(field, error)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('crew:task_detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'crew/task_confirm_delete.html'
    success_url = reverse_lazy('crew:task_list')

    def get_queryset(self):
        return Task.objects.filter(crew__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'task'
        context['title'] = f"Delete Task: {self.object.name}"
        context['cancel_url'] = reverse_lazy('crew:task_detail', kwargs={'pk': self.object.pk})
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully.')
        return super().delete(request, *args, **kwargs)


# CrewAI Execution Views

class ExecuteCrewView(LoginRequiredMixin, DetailView):
    """Execute a CrewInstance and all its tasks using CrewAI."""
    model = CrewInstance
    template_name = 'crew/execute.html'
    context_object_name = 'crew'
    
    def get_queryset(self):
        return CrewInstance.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'crew'
        context['title'] = f"Execute Crew: {self.object.name}"
        context['crew_detail_url'] = reverse_lazy('crew:crew_detail', kwargs={'pk': self.object.pk})
        
        # Get all tasks for this crew
        context['tasks'] = self.object.tasks.all().order_by('created_at')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle POST request to execute the crew."""
        self.object = self.get_object()
        
        try:
            # Execute the crew (will be implemented in CrewAI integration)
            self.object.execute()
            messages.success(request, f"Crew '{self.object.name}' executed successfully.")
        except Exception as e:
            messages.error(request, f"Error executing crew: {str(e)}")
        
        return redirect('crew:crew_detail', pk=self.object.pk)


class ExecuteTaskView(LoginRequiredMixin, DetailView):
    """Execute a single Task using CrewAI."""
    model = Task
    template_name = 'crew/execute_task.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.filter(crew__owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'task'
        context['title'] = f"Execute Task: {self.object.name}"
        context['task_detail_url'] = reverse_lazy('crew:task_detail', kwargs={'pk': self.object.pk})
        
        # Check if dependencies are complete
        context['dependencies_complete'] = self.object.check_dependencies_complete()
        context['dependencies'] = self.object.depends_on.all()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle POST request to execute the task."""
        self.object = self.get_object()
        
        # Check if dependencies are complete
        if not self.object.check_dependencies_complete():
            messages.error(request, "Cannot execute task because dependencies are not complete.")
            return redirect('crew:execute_task', pk=self.object.pk)
        
        try:
            # Update task status
            self.object.status = 'in_progress'
            self.object.save()
            
            # Execute the task (will be implemented in CrewAI integration)
            self.object.execute()
            
            messages.success(request, f"Task '{self.object.name}' executed successfully.")
        except Exception as e:
            # Update task status and error message
            self.object.status = 'failed'
            self.object.error_message = str(e)
            self.object.save()
            
            messages.error(request, f"Error executing task: {str(e)}")
        
        return redirect('crew:task_detail', pk=self.object.pk)


class CrewIndexView(TemplateView):
    """
    Main landing page for the Crew app.
    Shows different content based on authentication status.
    """
    template_name = 'crew/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # First, find the user's crews
            user_crews = CrewInstance.objects.filter(owner=self.request.user)
            context['crew_count'] = user_crews.count()
            
            # Get agents belonging to those crews
            context['agent_count'] = Agent.objects.filter(crew__in=user_crews).count()
            
            # Get tasks - adjust this query based on your actual model relationship
            # If tasks are linked to crews:
            context['task_count'] = Task.objects.filter(crew__in=user_crews).count()
            # If tasks are linked to agents:
            # context['task_count'] = Task.objects.filter(agent__crew__in=user_crews).count()
        return context


class PipelineView(LoginRequiredMixin, ListView):
    """
    View for displaying and managing crew executions.
    Shows a list of all crews with execution status and controls.
    """
    model = CrewInstance
    template_name = 'crew/pipeline.html'
    context_object_name = 'crews'
    
    def get_queryset(self):
        # Return only crews owned by the current user
        return CrewInstance.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context


class ExecuteCrewView(LoginRequiredMixin, DetailView):
    """
    View for executing a specific crew.
    """
    model = CrewInstance
    template_name = 'crew/execute_crew.html'
    context_object_name = 'crew'
    
    def post(self, request, *args, **kwargs):
        # Handle the POST request to execute the crew
        crew = self.get_object()
        # Add logic to start crew execution
        # This would integrate with your CrewAI logic
        
        messages.success(request, f"Crew '{crew.name}' execution started.")
        return redirect('crew:pipeline_view')


class StopCrewExecutionView(LoginRequiredMixin, DetailView):
    """
    View for stopping a running crew execution.
    """
    model = CrewInstance
    template_name = 'crew/stop_execution.html'
    context_object_name = 'crew'
    
    def post(self, request, *args, **kwargs):
        # Handle the POST request to stop the crew execution
        crew = self.get_object()
        # Add logic to stop crew execution
        
        messages.success(request, f"Crew '{crew.name}' execution stopped.")
        return redirect('crew:pipeline_view')


class ExecutionHistoryView(LoginRequiredMixin, DetailView):
    """
    View for displaying execution history of a specific crew.
    """
    model = CrewInstance
    template_name = 'crew/execution_history.html'
    context_object_name = 'crew'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crew = self.get_object()
        context['executions'] = crew.executions.all().order_by('-started_at')
        return context
