from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext as _


# define the choices for the paid_month field
PAID_MONTH_CHOICES = [(i, str(i)) for i in range(1, 13)]

# define the choices for the paid_year field
PAID_YEAR_CHOICES = [(i, str(i)) for i in range(2023, 2043)]


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


def generate_password():
    return "legacy"


class Customer(AbstractUser):
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"), null=True)
    address = models.CharField(max_length=255, verbose_name=_("Address"), null=True)
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), null=True)
    registration_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Registration Date"), null=True
    )
    active_membership = models.BooleanField(
        default=False, verbose_name=_("Active Membership"), null=True
    )
    membership_start_date = models.DateField(
        null=True, blank=True, verbose_name=_("Membership Start Date"),
    )
    membership_end_date = models.DateField(
        null=True, blank=True, verbose_name=_("Membership End Date")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"), null=True)
    profile_picture = models.ImageField(
        upload_to="customer_profile_pictures",
        null=True,
        blank=True,
        verbose_name=_("Profile Picture")
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
    username = None
    email = models.EmailField(_('email address'), unique=True, max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomerManager()

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
        return f"Pago {self.user.first_name} {self.user.last_name} - {self.date}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class Message(models.Model):
    sender = models.ForeignKey(Customer, related_name='sent_messages', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(Customer, related_name='received_messages', on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=2048, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=True)
    sent_at = models.DateTimeField(null=True, auto_now_add=False, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_impression = models.BooleanField(default=False)
    is_deleted_by_recepient = models.BooleanField(default=False)
    is_deleted_by_sender = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']


class MessageContent(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_html = models.BooleanField(default=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
