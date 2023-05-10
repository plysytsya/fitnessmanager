import datetime

from django.http import JsonResponse
from django.utils.translation import activate
from django.utils import formats
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse
from PIL import Image, ImageOps, ImageDraw
from django.db.models.fields.reverse_related import ManyToOneRel


from .models import Customer


def translate_boolean(value, language):
    if language == "es":
        return "si" if value else "no"
    else:  # default to English
        return "yes" if value else "no"


class CustomerData(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        language = request.GET.get("lang", "en")  # default to English
        activate(language)
        all_fields = request.GET.get("all", "false").lower() == "true"

        customer_data = Customer.objects.values()
        translated_customer_data = []

        fields_to_return = _get_fields_to_return(all_fields)

        for data in customer_data:
            translated_data = {}
            for field_name in fields_to_return:
                if field_name not in data:
                    continue

                key = _get_translated_key(field_name, language)
                value, value_type = _get_value_and_type(
                    data[field_name], language
                )

                translated_data[key] = {
                    "value": value if value else " - ",
                    "_type": value_type,
                    "editable": _is_key_editable(field_name),
                }

            translated_customer_data.append(translated_data)

        return JsonResponse({"customer_data": translated_customer_data})

    def put(self, request, *args, **kwargs):
        language = self._get_language(request)
        customer_data = request.data
        customer = request.user

        for key, value in customer_data.items():
            print("updating", key, "to be",  value)
            field_name = _get_field_name_from_key(key, language)

            if not _is_key_editable(field_name):
                continue

            if hasattr(customer, field_name):
                setattr(customer, field_name, value)

        customer.save()

        return JsonResponse({"message": "Customer data updated successfully"})

    def _get_language(self, request):
        language = request.GET.get("lang", "en")
        activate(language)
        return language


def _get_fields_to_return(all_fields):
    fields = [
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
        fields = [field.name for field in Customer._meta.get_fields()]

    return fields


def _get_translated_key(field_name, language):
    if language == "en":
        key = field_name
    else:
        key = str(Customer._meta.get_field(field_name).verbose_name)
        key = key[0].upper() + key[1:]  # capitalize

    return key


def _get_field_name_from_key(key, language):
    if language == "en":
        return key

    for field in Customer._meta.get_fields():
        if isinstance(field, ManyToOneRel):
            continue

        translated_key = str(field.verbose_name)
        translated_key = translated_key[0].upper() + translated_key[1:]
        if translated_key == key:
            return field.name
    return None



def _get_value_and_type(value, language):
    value_type = type(value).__name__
    value_type = "date" if value_type == "datetime" else value_type

    if isinstance(value, bool):
        value = translate_boolean(value, language)
    elif isinstance(value, (datetime.date, datetime.datetime)):
        date_format = "Y-m-d" if language == "en" else "d.m.Y"
        value = formats.date_format(value, format=date_format, use_l10n=True)

    return value, value_type


def _is_key_editable(key: str) -> bool:
    uneditable_fields = [
        "id",
        "active_membership",
        "passport_number",
        "membership_start_date",
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
        "membership_start_date",
        "membership_end_date",
        "profile_picture",
    ]
    return key not in uneditable_fields


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

        response = HttpResponse(
            content_type="image/png"
        )  # Change the content type to image/png
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
