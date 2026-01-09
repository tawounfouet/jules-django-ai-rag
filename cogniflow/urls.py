from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ai_core.urls')),
    # We could add other apps urls here (commerce, etc.) but strictly asked for chat endpoint
]
