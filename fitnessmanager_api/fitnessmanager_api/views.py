# views.py

from django.http import JsonResponse
from django.utils.translation import activate
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Customer


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
                translated_data[key] = data[field_name]

            translated_customer_data.append(translated_data)

        return JsonResponse({"customer_data": translated_customer_data})
