from .models import UserActionLog


def log_user_action(user, action, target_model=None, target_id=None, details='', request=None):
    """Fonction utilitaire pour enregistrer les actions des utilisateurs"""
    ip_address = None
    user_agent = ''

    if request:
        # Récupérer l'adresse IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Récupérer le user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    UserActionLog.objects.create(
        user=user,
        action=action,
        target_model=target_model,
        target_id=target_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
