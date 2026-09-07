from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.utils import timezone
from modules.accounts.constants import Constants

class UserRole(models.TextChoices):
    USER = "user", "User"
    INSTRUCTOR = "instructor", "Instructor"
    ADMIN = "admin", "Admin"
    COMPANY = "company", "Company"


ROLE_GROUP_PREFIX = "role:"

class UserManager(BaseUserManager):
    """
    AbstractUser already comes with objects = UserManager() from Django itself, fully wired to work with a username field.
    But AbstractBaseUser gives you no manager, no username, no assumptions about how login works — it's intentionally a blank slate. Django's createsuperuser command and create_user() calls need some manager to know:
    1. which field is the "username" (login identifier) - use USERNAME_FIELD
    2. how to hash the password
    3. what counts as a valid superuser
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with a normalized email address."""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a user with the permissions required for admin access."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # upload profile image to temp/profile_images/ directory
    profile_image = models.ImageField(upload_to=Constants.IMAGE_UPLOAD_PATH, null=True, blank=True)

    # roles
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.USER)

    # password, last_login are provided by AbstractBaseUser
    # Password reset fields
    reset_password_token = models.CharField(max_length=255, null=True, blank=True)
    reset_password_expire = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Define a property to get the full name of the user
    @property
    def full_name(self):
        """Return the user's first and last names joined with a space."""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        """Return the user's email address as the display string."""
        return self.email

    def save(self, *args, **kwargs):
        """Save the user and assign the group matching the user's role."""
        super().save(*args, **kwargs)
        role_group, _ = Group.objects.get_or_create(
            name=f"{ROLE_GROUP_PREFIX}{self.role}"
        )
        # Assign the user to the group corresponding to their role, remove them from other role groups if they exist
        self.groups.set([role_group])

