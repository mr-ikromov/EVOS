from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
