from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from crew.models import CrewInstance, Agent, Task
from .serializers import CrewInstanceSerializer, AgentSerializer, TaskSerializer


class CrewInstanceFilter(filters.FilterSet):
    is_flow = filters.BooleanFilter()
    is_subcrew = filters.BooleanFilter(method='filter_is_subcrew')
    has_parent = filters.BooleanFilter(field_name='parent_crew', lookup_expr='isnull', exclude=True)

    class Meta:
        model = CrewInstance
        fields = ['is_flow', 'is_subcrew', 'has_parent', 'owner']

    def filter_is_subcrew(self, queryset, name, value):
        if value:
            return queryset.filter(parent_crew__isnull=False)
        return queryset.filter(parent_crew__isnull=True)


class AgentFilter(filters.FilterSet):
    role = filters.CharFilter()
    has_tools = filters.BooleanFilter(method='filter_has_tools')
    crew_type = filters.CharFilter(field_name='crew__is_flow')

    class Meta:
        model = Agent
        fields = ['role', 'has_tools', 'crew_type', 'crew', 'allow_delegation', 'verbose']

    def filter_has_tools(self, queryset, name, value):
        if value:
            return queryset.exclude(tools=[])
        return queryset.filter(tools=[])


class TaskFilter(filters.FilterSet):
    status = filters.CharFilter()
    has_dependencies = filters.BooleanFilter(method='filter_has_dependencies')
    has_output = filters.BooleanFilter(method='filter_has_output')

    class Meta:
        model = Task
        fields = ['status', 'has_dependencies', 'has_output', 'crew', 'agent']

    def filter_has_dependencies(self, queryset, name, value):
        if value:
            return queryset.filter(depends_on__isnull=False).distinct()
        return queryset.filter(depends_on__isnull=True)

    def filter_has_output(self, queryset, name, value):
        if value:
            return queryset.exclude(output_data={})
        return queryset.filter(output_data={})


class CrewInstanceViewSet(viewsets.ModelViewSet):
    queryset = CrewInstance.objects.all()
    serializer_class = CrewInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CrewInstanceFilter

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def agents(self, request, pk=None):
        crew = self.get_object()
        agents = Agent.objects.filter(crew=crew)
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        crew = self.get_object()
        tasks = Task.objects.filter(crew=crew)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subcrews(self, request, pk=None):
        crew = self.get_object()
        subcrews = CrewInstance.objects.filter(parent_crew=crew)
        serializer = CrewInstanceSerializer(subcrews, many=True)
        return Response(serializer.data)


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AgentFilter

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        agent = self.get_object()
        tasks = Task.objects.filter(agent=agent)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = TaskFilter

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        task = self.get_object()
        # Task execution logic will be implemented here
        return Response({'status': 'task started'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        # Task completion logic will be implemented here
        return Response({'status': 'task completed'})
