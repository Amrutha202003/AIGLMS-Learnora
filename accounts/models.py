from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email        = models.EmailField(unique=True)
    is_student   = models.BooleanField(default=True)
    is_admin     = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = 'users'
        verbose_name        = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.is_student:
        from students.models import StudentProfile

        # FIX: only pass fields that actually exist on StudentProfile.
        # We removed 'email' because StudentProfile has no email field.
        # Add only 'full_name' — the one field confirmed present.
        StudentProfile.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.get_full_name() or instance.username,
            }
        )