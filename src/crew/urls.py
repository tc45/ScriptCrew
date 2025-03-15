from django.urls import path
from .views import (
    CrewIndexView, 
    CrewListView, CrewCreateView, CrewDetailView, CrewUpdateView, CrewDeleteView,
    AgentListView, AgentCreateView, AgentDetailView, AgentUpdateView, AgentDeleteView,
    TaskListView, TaskCreateView, TaskDetailView, TaskUpdateView, TaskDeleteView,
    PipelineView, ExecuteCrewView, StopCrewExecutionView, ExecutionHistoryView
    # Include other views here
)

app_name = 'crew'

urlpatterns = [
    # Main index view
    path('', CrewIndexView.as_view(), name='index'),
    
    # Crew-related URLs
    path('crews/', CrewListView.as_view(), name='crew_list'),
    path('crews/create/', CrewCreateView.as_view(), name='crew_create'),
    path('crews/<int:pk>/', CrewDetailView.as_view(), name='crew_detail'),
    path('crews/<int:pk>/update/', CrewUpdateView.as_view(), name='crew_update'),
    path('crews/<int:pk>/delete/', CrewDeleteView.as_view(), name='crew_delete'),
    
    # Agent-related URLs
    path('agents/', AgentListView.as_view(), name='agent_list'),
    path('agents/create/', AgentCreateView.as_view(), name='agent_create'),
    path('agents/<int:pk>/', AgentDetailView.as_view(), name='agent_detail'),
    path('agents/<int:pk>/update/', AgentUpdateView.as_view(), name='agent_update'),
    path('agents/<int:pk>/delete/', AgentDeleteView.as_view(), name='agent_delete'),
    
    # Task-related URLs
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    
    # Pipeline URLs
    path('pipeline/', PipelineView.as_view(), name='pipeline_view'),
    path('crews/<int:pk>/execute/', ExecuteCrewView.as_view(), name='crew_execute'),
    path('crews/<int:pk>/stop/', StopCrewExecutionView.as_view(), name='crew_stop'),
    path('crews/<int:pk>/history/', ExecutionHistoryView.as_view(), name='execution_history'),
    
    # Include your other URL patterns here
] 