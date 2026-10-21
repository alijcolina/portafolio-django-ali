from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Señal que se dispara al guardar un User.
    - Si el usuario es nuevo (created=True), crea su Profile.
    - Si el usuario ya existía, actualiza los datos básicos en su Profile.
    """
    if created:
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email
        )
        print(f"✅ Perfil creado para: {instance.username}")
    else:
        # Usamos get_or_create por si el usuario se creó antes de existir esta señal
        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.first_name = instance.first_name
        profile.last_name = instance.last_name
        profile.email = instance.email
        profile.save()