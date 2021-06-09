from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('blog.urls')),
    path('account/', include('django.contrib.auth.urls')),
    path('account/', include('account.urls')),
    path('about/', TemplateView.as_view(template_name="about.html"), name='about'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
