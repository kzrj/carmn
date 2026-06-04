from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone: str, password: str | None = None, **extra):
        if not phone:
            raise ValueError("Phone is required")
        phone = self.normalize_phone(phone)
        user = self.model(phone=phone, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra)

    @staticmethod
    def normalize_phone(phone: str) -> str:
        return phone.strip().replace(" ", "").replace("-", "")


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.phone


class SellerType(models.TextChoices):
    OWNER = "owner", "Owner"
    PRIVATE = "private", "Private"
    COMPANY = "company", "Company"


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    seller_type = models.CharField(
        max_length=20,
        choices=SellerType.choices,
        default=SellerType.PRIVATE,
    )
    display_name = models.CharField(max_length=120, blank=True, default="")
    company_name = models.CharField(max_length=200, blank=True, default="")

    def __str__(self) -> str:
        return self.display_name or self.company_name or str(self.user.phone)
