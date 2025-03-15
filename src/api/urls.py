from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'crews', views.CrewInstanceViewSet)
router.register(r'agents', views.AgentViewSet)
router.register(r'tasks', views.TaskViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
] 