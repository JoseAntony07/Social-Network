import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class AbstractBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class BaseModel(AbstractBaseModel):
    created_on = models.DateTimeField('Created on', auto_now_add=True)
    modified_on = models.DateTimeField('Modified on', auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, is_staff=False, is_superuser=False, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        if not password:
            raise ValueError('Password is not provided')

        user = self.model(email=self.normalize_email(email),
                          password=password,
                          first_name=first_name,
                          last_name=last_name,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          **extra_fields
                          )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name):
        return self._create_user(email, password, first_name, last_name)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class User(BaseModel, AbstractBaseUser):
    GENDERS = (('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'))

    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    gender = models.CharField(_('Gender'), choices=GENDERS, max_length=12, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    friends = models.ManyToManyField("User", blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Unselect this instead of deleting accounts.'))
    is_superuser = models.BooleanField(_('superuser status'), default=False, help_text=_('Designates that this user has all permissions'))

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    class Meta:
        db_table = 'user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('-created_on',)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def send_friend_request(self, to_user):
        if self != to_user:
            existing_request = FriendRequest.objects.filter(sent_from=self, sent_to=to_user, is_active=True).exists()
            if not existing_request:
                FriendRequest.objects.create(sent_from=self, sent_to=to_user)
                return True  # Request sent successfully
        return False

    def accept_friend_request(self, friend_request):
        if friend_request.sent_to == self and friend_request.status == 1:  # Pending request
            friend_request.status = 2  # Set status to Accepted
            friend_request.save()
            self.friends.add(friend_request.sent_from)
            friend_request.sent_from.friends.add(self)
            return True  # Request accepted successfully
        return False

    def reject_friend_request(self, friend_request):
        if friend_request.sent_to == self and friend_request.status == 1:  # Pending request
            friend_request.status = 3  # Set status to Rejected
            friend_request.is_active = False
            friend_request.save()
            return True  # Request rejected successfully
        return False


class FriendRequest(BaseModel):
    STATUS_CHOICES = (
        (1, 'Pending'),
        (2, 'Accepted'),
        (3, 'Rejected'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    sent_from = models.ForeignKey(User, related_name="requests_sent", on_delete=models.CASCADE)
    sent_to = models.ForeignKey(User, related_name="requests_received", on_delete=models.CASCADE)
