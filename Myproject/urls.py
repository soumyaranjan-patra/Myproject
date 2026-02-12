from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Django is working!")

urlpatterns = [
    path('', home),  # homepage
    path('admin/', admin.site.urls),
    path('api/auth/', include('multi_role_auth.urls')),
]
