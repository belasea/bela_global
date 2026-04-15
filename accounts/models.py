from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractUser
)

class UserManager(BaseUserManager):
    def create_user(
            self, email, 
            password=None, 
            first_name=None, 
            last_name=None, 
            contact_number=None, 
            date_of_birth=None,
            gender=None,
        ):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            contact_number=contact_number,
            date_of_birth=date_of_birth,
            gender=gender,
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_staff_user(
        self, email, password, first_name, last_name, contact_number, date_of_birth, gender):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            contact_number=contact_number,
            date_of_birth=date_of_birth,
            gender=gender,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name, last_name, contact_number):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            contact_number=contact_number,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name='Email Address', max_length=255, unique=True)
    GENDER = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    date_of_birth = models.DateField(auto_now_add=False, blank=True, null=True)
    profile = models.FileField(upload_to="account/", blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER, blank=True, null=True)
    is_moderator = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'contact_number']

    objects = UserManager()
    
    def __str__(self):
        return self.email

