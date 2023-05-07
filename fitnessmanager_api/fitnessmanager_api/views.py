# views.py

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Customer


class GetCustomerData(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        customer_data = Customer.objects.values()
        return JsonResponse({'customer_data': list(customer_data)})
