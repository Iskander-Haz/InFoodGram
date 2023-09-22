from django.contrib.auth.models import AbstractUser

from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """Можель пользователя"""

    class Role(models.TextChoices):
        USER = "user", "Пользователь"
        ADMIN = "admin", "Администратор"

    role = models.CharField(
        max_length=10,
        default=Role.USER,
        choices=Role.choices,
        verbose_name="Роль",
    )
    password = models.CharField(max_length=150, verbose_name="Пароль")

    email = models.EmailField(
        max_length=254, unique=True, verbose_name="Адрес электронной почты"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "first_name", "last_name")

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def str(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписок"""

    user = models.ForeignKey(
        User,
        related_name="subscriber",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )

    author = models.ForeignKey(
        User,
        related_name="subscribing",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        ordering = ("-id",)
        constraints = (
            UniqueConstraint(
                fields=("user", "author"), name="unique_subscription"
            ),
        )
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
