from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def welcome(request):
    return JsonResponse({"message": "Welcome to MiniPay API! Visit /api/ to get started."})

urlpatterns = [
    path('', welcome, name='welcome'),
    path('admin/', admin.site.urls),
    path('api/', include('payments.urls')),
]
