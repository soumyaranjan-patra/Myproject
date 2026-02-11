
from django.apps import AppConfig


class MultiRoleAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "multi_role_auth"
    verbose_name = "Multi-Role Auth"

    def ready(self):
        import multi_role_auth.signals  # noqa: F401
