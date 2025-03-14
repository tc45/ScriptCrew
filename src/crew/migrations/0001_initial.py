# Generated by Django 4.2.11 on 2025-03-12 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('researcher', 'Researcher'), ('writer', 'Writer'), ('editor', 'Editor'), ('reviewer', 'Reviewer'), ('custom', 'Custom')], max_length=50)),
                ('custom_role', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField()),
                ('goals', models.JSONField(default=list)),
                ('backstory', models.TextField(blank=True)),
                ('tools', models.JSONField(default=list, help_text='List of tools available to this agent')),
                ('allow_delegation', models.BooleanField(default=True)),
                ('verbose', models.BooleanField(default=False)),
                ('llm_config', models.JSONField(default=dict, help_text='Configuration for the LLM used by this agent')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Agent',
                'verbose_name_plural': 'Agents',
                'ordering': ['crew', 'role', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CrewInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('is_flow', models.BooleanField(default=False, help_text='Whether this instance represents a flow coordinating multiple crews')),
                ('config', models.JSONField(default=dict, help_text='Configuration including routing and state management for flows')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crews', to=settings.AUTH_USER_MODEL)),
                ('parent_crew', models.ForeignKey(blank=True, help_text='Parent crew if this is part of a larger workflow', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_crews', to='crew.crewinstance')),
            ],
            options={
                'verbose_name': 'Crew Instance',
                'verbose_name_plural': 'Crew Instances',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('expected_output', models.TextField(help_text='Description of what this task should produce')),
                ('context', models.JSONField(default=list, help_text='List of related tasks that provide context')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('input_data', models.JSONField(default=dict)),
                ('output_data', models.JSONField(blank=True, default=dict)),
                ('error_message', models.TextField(blank=True)),
                ('output_file', models.CharField(blank=True, help_text='Path to file where task output should be saved', max_length=255)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='crew.agent')),
                ('crew', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='crew.crewinstance')),
                ('depends_on', models.ManyToManyField(blank=True, help_text='Tasks that must be completed before this one can start', related_name='dependent_tasks', to='crew.task')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='agent',
            name='crew',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agents', to='crew.crewinstance'),
        ),
    ]
