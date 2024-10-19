from django.apps import AppConfig


class ViewerConfig(AppConfig):
    """
    Konfigurace aplikace 'viewer'.

    Tato třída definuje základní nastavení aplikace,
    včetně výchozího typu automatického pole pro ID.
    """
    default_auto_field = 'django.db.models.BigAutoField' # Výchozí typ auto-pole pro modely
    name = 'viewer' # Název aplikace
