from django.urls import path, include

urlpatterns = [
    # ... existing URL patterns ...
    path('crew/', include('crew.urls', namespace='crew')),
    # ... other URL patterns ...
] 