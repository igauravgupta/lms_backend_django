from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """App configuration for the 'accounts' module.

    Registers the app with Django and ensures signal handlers are
    connected when the app is ready.
    """

    name = 'modules.accounts'

    def ready(self):
        """Import the signals module to register signal handlers.

        Django calls this method once the app registry is fully populated.
        Importing `signals` here (rather than at module load time) ensures
        the `pre_save`/`post_save` receivers in `signals.py` are connected
        without risking issues from apps not yet being loaded.
        """
        from . import signals