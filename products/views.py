import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import ProductForm
from .models import Product




class ProductQueryMixin:
    def get_currency(self) -> str:
        return getattr(settings, "INVENTORY_CURRENCY", "UZS")

    def get_search_query(self) -> str:
        return self.request.GET.get("q", "").strip()

    def get_sort_key(self) -> str:
        value = self.request.GET.get("sort", "created")
        return value if value in {"price", "created"} else "created"

    def filter_queryset(self, queryset):
        query = self.get_search_query()
        if query:
            queryset = queryset.filter(name__icontains=query)
        sort_key = self.get_sort_key()
        if sort_key == "price":
            queryset = queryset.order_by("-price", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")
        return queryset


from django.core.paginator import Paginator

class ProductListView(ProductQueryMixin, LoginRequiredMixin, TemplateView):
    template_name = "products/list.html"
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get initial queryset
        queryset = Product.objects.all()
        queryset = self.filter_queryset(queryset)
        
        # Paginate the queryset
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        # Get stats
        total = queryset.count()
        last_product = queryset.order_by("-created_at").first()
        stats = {
            "total": total,
            "last_product": last_product,
        }

        context.update(
            {
                "page_title": "Mahsulotlar",
                "stats": stats,
                "products": page_obj.object_list,
                "page_obj": page_obj,
                "search_query": self.get_search_query(),
                "sort": self.get_sort_key(),
                "currency": self.get_currency(),
            }
        )
        return context


class HTMXFormMixin:
    htmx_template_name = None
    success_message = "Mahsulot saqlandi"
    error_message = "Xatolik yuz berdi. Qayta urinib ko‘ring."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", kwargs.get("form", context.get("form")))
        context["form_action"] = self.request.path
        context["product"] = getattr(self, "object", None)
        context["is_htmx"] = bool(self.request.headers.get("HX-Request"))
        obj = context["product"]
        context["image_preview"] = obj.image.url if obj and obj.image else ""
        return context

    def render_to_response(self, context, **response_kwargs):
        template_name = self.htmx_template_name or self.template_name
        if self.request.headers.get("HX-Request"):
            html = render_to_string(template_name, context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            context = self.get_context_data(form=form)
            template_name = self.htmx_template_name or self.template_name
            html = render_to_string(template_name, context, request=self.request)
            response = HttpResponse(html, status=400)
            response["HX-Trigger"] = json.dumps(
                {
                    "showToast": {
                        "type": "error",
                        "message": self.error_message,
                    }
                }
            )
            return response
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("HX-Request"):
            headers = {
                "HX-Trigger": json.dumps(
                    {
                        "reloadProducts": True,
                        "showToast": {
                            "type": "success",
                            "message": self.success_message,
                        },
                    }
                ),
                "HX-Trigger-After-Settle": json.dumps({"closeModal": True}),
            }
            return HttpResponse(status=204, headers=headers)
        return super().form_valid(form)


class ProductCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    form_class = ProductForm
    template_name = "products/create_modal.html"
    htmx_template_name = "products/create_modal.html"
    success_url = reverse_lazy("products-web-list")


class ProductUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/edit_modal.html"
    htmx_template_name = "products/edit_modal.html"
    success_url = reverse_lazy("products-web-list")


class ProductTablePartialView(ProductQueryMixin, LoginRequiredMixin, ListView):
    model = Product
    context_object_name = "products"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_queryset(queryset)

    def get_template_names(self):
        is_paginating = "page" in self.request.GET
        is_search = "q" in self.request.GET or "sort" in self.request.GET

        if not is_paginating and is_search:
            # For a search, we render the OOB template which updates both views
            return ["products/_product_list_oob.html"]

        if self.request.GET.get("view") == "cards":
            if is_paginating:
                return ["products/_product_cards.html"]
            return ["products/_cards_mobile.html"]
        
        if is_paginating:
            return ["products/_product_rows.html"]
        return ["products/_table.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["currency"] = self.get_currency()
        context["search_query"] = self.get_search_query()
        context["sort"] = self.get_sort_key()
        context["view"] = self.request.GET.get("view")
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if not context["page_obj"].has_next():
            response["HX-Trigger"] = json.dumps({"stopInfiniteScroll": True})
        return response




class ProductDeleteView(LoginRequiredMixin, View):
    template_name = "products/delete_modal.html"

    def get_object(self):
        return get_object_or_404(Product, pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        context = {"product": product}
        html = render_to_string(self.template_name, context, request=request)
        if request.headers.get("HX-Request"):
            return HttpResponse(html)
        return HttpResponse(html)

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        if request.headers.get("HX-Request"):
            headers = {
                "HX-Trigger": json.dumps(
                    {
                        "reloadProducts": True,
                        "showToast": {
                            "type": "success",
                            "message": "Mahsulot o‘chirildi",
                        },
                    }
                ),
                "HX-Trigger-After-Settle": json.dumps({"closeModal": True}),
            }
            return HttpResponse(status=204, headers=headers)
        return HttpResponse(status=204)
