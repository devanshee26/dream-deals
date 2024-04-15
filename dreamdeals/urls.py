from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
     # Define a simple URL pattern for the root path
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('home/', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('welcome/', views.welcome, name='welcome'),
    path('store/',  include('store.urls'))
]
