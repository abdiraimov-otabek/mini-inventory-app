import io
import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product


class ProductAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.media_root = tempfile.mkdtemp()
        override = self.settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)
        self.user = get_user_model().objects.create_user(
            phone_number="+15555550300",
            username="tester",
            password="strong-password",
        )
        self.product = Product.objects.create(
            name="Sample Product",
            price=Decimal("19.99"),
        )

    def test_list_products(self):
        url = reverse("product-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["name"], self.product.name)

    def test_list_requires_authentication(self):
        url = reverse("product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product(self):
        url = reverse("product-list")
        payload = {
            "name": "Created Product",
            "price": "25.50",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name=payload["name"]).exists())

    def test_upload_image_success(self):
        url = reverse("product-upload-image", args=[self.product.id])
        self.client.force_authenticate(user=self.user)
        image_file = self._generate_image_file("test.png", "PNG", "image/png")
        response = self.client.post(url, {"image": image_file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertTrue(self.product.image)
        self.assertIn("image", response.data)

    def test_upload_image_rejects_large_file(self):
        url = reverse("product-upload-image", args=[self.product.id])
        self.client.force_authenticate(user=self.user)
        large_content = b"a" * (5 * 1024 * 1024 + 1)
        file_obj = SimpleUploadedFile(
            "big.jpg",
            large_content,
            content_type="image/jpeg",
        )
        response = self.client.post(url, {"image": file_obj}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_upload_image_rejects_invalid_type(self):
        url = reverse("product-upload-image", args=[self.product.id])
        self.client.force_authenticate(user=self.user)
        file_obj = SimpleUploadedFile(
            "not-image.txt",
            b"data",
            content_type="text/plain",
        )
        response = self.client.post(url, {"image": file_obj}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def _generate_image_file(self, name: str, format: str, content_type: str):
        buffer = io.BytesIO()
        image = Image.new("RGB", (1, 1), color="white")
        image.save(buffer, format=format)
        buffer.seek(0)
        return SimpleUploadedFile(name, buffer.read(), content_type=content_type)


class ProductHTMLViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            phone_number="+15555550400",
            username="admin",
            password="strong-password",
        )
        self.product = Product.objects.create(name="Web Product", price=Decimal("5.00"))

    def test_list_requires_login(self):
        response = self.client.get(reverse("products-web-list"))
        self.assertEqual(response.status_code, 302)

    def test_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("products-web-list"))
        self.assertContains(response, "products-table")

    def test_create_product_form(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("products-web-new"),
            {"name": "Form Product", "price": "9.99"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Product.objects.filter(name="Form Product").exists())

    def test_table_partial_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("products-web-table"))
        self.assertContains(response, self.product.name)

    def test_htmx_create_returns_204(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("products-web-new"),
            {"name": "HTMX Product", "price": "12.00"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 204)
        self.assertIn("HX-Trigger", response.headers)
