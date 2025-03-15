from rest_framework import serializers
from crew.models import CrewInstance, Agent, Task


class CrewInstanceSerializer(serializers.ModelSerializer):
    is_subcrew = serializers.BooleanField(read_only=True)
    agent_count = serializers.SerializerMethodField()
    subcrew_count = serializers.SerializerMethodField()

    class Meta:
        model = CrewInstance
        fields = [
            'id', 'name', 'description', 'owner', 'is_flow',
            'parent_crew', 'config', 'is_subcrew', 'agent_count',
            'subcrew_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def get_agent_count(self, obj):
        return obj.agents.count()

    def get_subcrew_count(self, obj):
        return obj.sub_crews.count()


class AgentSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    effective_role = serializers.CharField(read_only=True)

    class Meta:
        model = Agent
        fields = [
            'id', 'crew', 'name', 'role', 'custom_role',
            'description', 'goals', 'backstory', 'tools',
            'allow_delegation', 'verbose', 'llm_config',
            'effective_role', 'task_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    dependent_tasks = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'crew', 'agent', 'name', 'description',
            'expected_output', 'context', 'depends_on',
            'dependent_tasks', 'status', 'input_data',
            'output_data', 'error_message', 'output_file',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'dependent_tasks', 'started_at', 'completed_at',
            'created_at', 'updated_at'
        ] 