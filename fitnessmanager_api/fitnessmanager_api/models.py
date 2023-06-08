import calendar
import uuid
import datetime

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"), null=True)
    address = models.CharField(max_length=255, verbose_name=_("Address"), null=True)
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), null=True)
    registration_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Registration Date"), null=True
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(Customer, related_name='sent_messages', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(Customer, related_name='received_messages', on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=2048, null=True, blank=True)
    is_draft = models.BooleanField(default=True)
    sent_at = models.DateTimeField(null=True, auto_now_add=False, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_impression = models.BooleanField(default=False)
    is_deleted_by_recepient = models.BooleanField(default=False)
    is_deleted_by_sender = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


class MessageContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    text = models.TextField()
    is_html = models.BooleanField(default=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)


class Gym(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, verbose_name=_("Gym Name"))
    address = models.CharField(max_length=255, verbose_name=_("Gym Address"))
    group = models.ForeignKey('auth.Group', on_delete=models.SET_NULL, null=True, related_name='gyms')
    customers = models.ManyToManyField('Customer', through='GymMembership', related_name='gyms')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Gym")
        verbose_name_plural = _("Gyms")


class GymMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    gym = models.ForeignKey('Gym', on_delete=models.CASCADE)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer} membership at {self.gym}"

    class Meta:
        verbose_name = _("Gym Membership")
        verbose_name_plural = _("Gym Memberships")


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.DurationField()
    max_participants = models.PositiveIntegerField()
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    trainer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")


class CourseSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[(i, calendar.day_name[i]) for i in range(7)]) # 0-Monday, 6-Sunday
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Course Schedule")
        verbose_name_plural = _("Course Schedules")


class CourseInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Course Instance")
        verbose_name_plural = _("Course Instances")


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")
        constraints = [
            models.CheckConstraint(
                check=models.Q(date__gte=datetime.date.today()),
                name='date_not_in_past'
            )
        ]
