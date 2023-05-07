import random
import string

from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.translation import gettext as _


# define the choices for the paid_month field
PAID_MONTH_CHOICES = [(i, str(i)) for i in range(1, 13)]

# define the choices for the paid_year field
PAID_YEAR_CHOICES = [(i, str(i)) for i in range(2023, 2043)]


def generate_password():
    chars = string.ascii_letters + string.digits
    plain_password = ''.join(random.choice(chars) for _ in range(6))
    # todo Implement sending temp password via email and asking for new one
    print(plain_password)
    return hash_password(plain_password)


def hash_password(plain_password):
    hashed_password = make_password(plain_password)
    return hashed_password


class Customer(models.Model):
    first_name = models.CharField(max_length=255, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=255, verbose_name=_("Last Name"))
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"))
    email = models.EmailField(max_length=255, verbose_name=_("Email"))
    registration_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Registration Date")
    )
    active_membership = models.BooleanField(
        default=False, verbose_name=_("Active Membership")
    )
    membership_start_date = models.DateField(
        null=True, blank=True, verbose_name=_("Membership Start Date")
    )
    membership_end_date = models.DateField(
        null=True, blank=True, verbose_name=_("Membership End Date")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    profile_picture = models.ImageField(
        upload_to="customer_profile_pictures",
        null=True,
        blank=True,
        verbose_name=_("Profile Picture"),
    )
    passport_number = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Passport Number")
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Weight")
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Height")
    )
    password = models.CharField(max_length=128, null=False, default=generate_password)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")


class Payment(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="payments", verbose_name=_("Customer")
    )
    date = models.DateField(null=True, blank=True, verbose_name=_("Payment Date"))
    amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Amount Paid"),
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Discount Percent"),
    )
    payment_method = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Payment Method'))
    paid_month = models.PositiveIntegerField(verbose_name=_('Paid Month'), choices=PAID_MONTH_CHOICES)
    paid_year = models.PositiveIntegerField(verbose_name=_('Paid Year'), choices=PAID_YEAR_CHOICES)

    def __str__(self):
        return f"Pago {self.customer.first_name} {self.customer.last_name} - {self.date}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
