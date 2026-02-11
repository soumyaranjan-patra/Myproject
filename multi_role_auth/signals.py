# """
# Signals for multi-role auth:
# - Professor signup: set is_active=False, verification_status=PENDING
# - (Student login recording is done in the login view, not signal)
# """
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from .models import CustomUser, Role, VerificationStatus


# @receiver(post_save, sender=CustomUser)
# def set_professor_verification_on_create(sender, instance, created, **kwargs):
#     """
#     When a Professor signs up, set is_active=False and verification_status=PENDING.
#     Runs only on create (created=True).
#     """
#     if created and instance.role == Role.PROFESSOR:
#         CustomUser.objects.filter(pk=instance.pk).update(
#             is_active=False,
#             verification_status=VerificationStatus.PENDING,
#         )

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def handle_professor_signup(sender, instance, created, **kwargs):
    if created and instance.role == 'PROFESSOR':
        instance.is_active = False # Not active until Admin approves
        instance.verification_status = 'PENDING'
        instance.save()