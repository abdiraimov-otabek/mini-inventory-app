from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from products.views import (
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductTablePartialView,
    ProductUpdateView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", ProductListView.as_view(), name="products-web-list"),
    path("new/", ProductCreateView.as_view(), name="products-web-new"),
    path("<uuid:pk>/edit/", ProductUpdateView.as_view(), name="products-web-edit"),
    path("<uuid:pk>/delete/", ProductDeleteView.as_view(), name="products-web-delete"),
    path("table/", ProductTablePartialView.as_view(), name="products-web-table"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
