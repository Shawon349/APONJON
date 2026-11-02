from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User & Role Management'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(ensure_default_admin, sender=self)


def ensure_default_admin(sender, **kwargs):
    """
    Guarantees default Super Admin Shawon / 47K3RWJ6 exists with full permissions,
    and demo users have generic display names rather than personal team names.
    """
    from accounts.models import User
    try:
        admin_user, created = User.objects.get_or_create(username='Shawon')
        admin_user.first_name = 'Sumsodduha'
        admin_user.last_name = 'Shawon'
        admin_user.email = 'shawon@aponjon.org'
        admin_user.role = 'ADMIN'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('47K3RWJ6')
        admin_user.save()

        # Sanitize demo test users
        User.objects.filter(username='shawon_reporter').update(
            first_name='পরিবার',
            last_name='রিপোর্টার',
            email='reporter@example.com'
        )
        User.objects.filter(username='junayed_citizen').update(
            first_name='সচেতন',
            last_name='নাগরিক',
            email='citizen@example.com'
        )
        User.objects.filter(username='sufal_reporter').update(
            first_name='পরিবার',
            last_name='রিপোর্টার ২',
            email='reporter2@example.com'
        )
    except Exception:
        pass
