import datetime

from django.http import JsonResponse
from django.utils.translation import activate
from django.utils import formats
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse
from PIL import Image, ImageOps, ImageDraw

from .models import Customer


def translate_boolean(value, language):
    if language == "es":
        return "si" if value else "no"
    else:  # default to English
        return "yes" if value else "no"


class GetCustomerData(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        language = request.GET.get("lang", "en")  # default to English
        activate(language)
        all_fields = request.GET.get("all", "false").lower() == "true"

        customer_data = Customer.objects.values()
        translated_customer_data = []

        fields_to_return = [
            "first_name",
            "last_name",
            "passport_number",
            "date_of_birth",
            "email",
            "phone_number",
            "active_membership",
            "membership_start_date",
            "weight",
            "height",
            "notes",
        ]

        if all_fields:
            fields_to_return = [field.name for field in Customer._meta.get_fields()]

        for data in customer_data:
            translated_data = {}
            for field_name in fields_to_return:
                if field_name not in data:
                    continue
                if language == "en":
                    key = field_name
                else:
                    key = str(Customer._meta.get_field(field_name).verbose_name)
                    key = key[0].upper() + key[1:]  # capitalize

                value = data[field_name]
                if isinstance(value, bool):
                    value = translate_boolean(value, language)
                elif isinstance(value, (datetime.date, datetime.datetime)):

                    date_format = "Y-m-d" if language == "en" else "d.m.Y"
                    value = formats.date_format(value, format=date_format, use_l10n=True)

                translated_data[key] = value if value else " - "

            translated_customer_data.append(translated_data)

        return JsonResponse({"customer_data": translated_customer_data})


class GetProfilePicture(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        as_thumbnail = request.GET.get("as_thumbnail", "false").lower() == "true"
        shape = request.GET.get("shape", "original")

        customer = request.user
        profile_picture_path = customer.profile_picture.path
        img = Image.open(profile_picture_path)

        if as_thumbnail:
            img.thumbnail((128, 128))

        if shape == "oval":
            img = self.make_oval_image(img)
        elif shape == "round":
            img = self.make_round_image(img)

        response = HttpResponse(content_type="image/png")  # Change the content type to image/png
        img.save(response, "PNG")  # Save the image as PNG instead of JPEG

        return response

    @staticmethod
    def make_oval_image(img):
        size = (img.width, img.height)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output

    @staticmethod
    def make_round_image(img):
        size = min(img.width, img.height)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output

