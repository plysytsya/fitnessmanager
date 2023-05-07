from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .models import Customer, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class CustomerAdmin(admin.ModelAdmin):
    model = Customer

    inlines = [PaymentInline]
    exclude = ("password", "is_active", "groups", "user_permissions")

    list_display = (
        "first_name",
        "last_name",
        "passport_number",
        "address",
        "email",
        "phone_number",
        "date_of_birth",
        "membership_start_date",
        "notes",
        "payment_link",
        "active_membership",
        "thumbnail",
    )

    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" />'.format(obj.profile_picture.url)
            )
        else:
            return ""

    thumbnail.short_description = "Foto"

    search_fields = ('first_name', 'last_name', 'email', 'phone_number')

    def payment_link(self, obj):
        url = reverse('admin:fitnessmanager_api_payment_changelist')
        link_text = _('View payments')
        return format_html('<a href="{}?customer__id={}">{}</a>', url, obj.id, link_text)
    payment_link.short_description = _('Payments')


class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "date",
        "amount",
        "discount_percent",
        "payment_method",
        "paid_month",
        "paid_year",
    )


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Payment, PaymentAdmin)
