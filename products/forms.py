from django import forms
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "image"]

    def clean_image(self):
        image = self.cleaned_data.get("image", False)
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(_("Rasm hajmi 5MB dan oshmasligi kerak."))
            if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise ValidationError(_("Faqat jpeg, png, yoki webp rasm yuklang."))
        return image
