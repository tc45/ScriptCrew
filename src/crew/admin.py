from django.contrib import admin
from django.utils.html import format_html
from .models import CrewInstance, Agent, Task


@admin.register(CrewInstance)
class CrewInstanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_flow', 'subcrew_count', 'agent_count', 'created_at')
    list_filter = ('owner', 'is_flow', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner')
        }),
        ('Crew Configuration', {
            'fields': ('is_flow', 'parent_crew', 'config')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def subcrew_count(self, obj):
        return obj.sub_crews.count()
    subcrew_count.short_description = 'Number of Sub-crews'

    def agent_count(self, obj):
        return obj.agents.count()
    agent_count.short_description = 'Number of Agents'


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'crew_link', 'role', 'custom_role', 'task_count', 'allow_delegation', 'verbose')
    list_filter = ('crew', 'role', 'allow_delegation', 'verbose', 'created_at')
    search_fields = ('name', 'description', 'custom_role', 'crew__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('crew',)

    fieldsets = (
        (None, {
            'fields': ('name', 'crew', 'role', 'custom_role', 'description')
        }),
        ('Agent Configuration', {
            'fields': ('goals', 'backstory', 'tools', 'allow_delegation', 'verbose')
        }),
        ('LLM Settings', {
            'fields': ('llm_config',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def crew_link(self, obj):
        url = f"/admin/crew/crewinstance/{obj.crew.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.crew.name)
    crew_link.short_description = 'Crew'
    crew_link.admin_order_field = 'crew__name'

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Number of Tasks'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'crew_link', 'agent_link', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'crew', 'agent', 'created_at')
    search_fields = ('name', 'description', 'error_message', 'crew__name', 'agent__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('crew', 'agent')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'crew', 'agent', 'status')
        }),
        ('Task Details', {
            'fields': ('expected_output', 'context', 'output_file')
        }),
        ('Dependencies', {
            'fields': ('depends_on',),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at')
        }),
        ('Data', {
            'fields': ('input_data', 'output_data', 'error_message'),
            'classes': ('collapse',)
        }),
    )

    def crew_link(self, obj):
        url = f"/admin/crew/crewinstance/{obj.crew.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.crew.name)
    crew_link.short_description = 'Crew'
    crew_link.admin_order_field = 'crew__name'

    def agent_link(self, obj):
        url = f"/admin/crew/agent/{obj.agent.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.agent.name)
    agent_link.short_description = 'Agent'
    agent_link.admin_order_field = 'agent__name'
