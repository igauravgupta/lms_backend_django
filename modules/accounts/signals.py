from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import ROLE_GROUP_PREFIX


@receiver(pre_save, sender=User)
def detect_role_change(sender, instance, update_fields=None, **kwargs):
    """Detect whether a User's `role` field is changing, before it is saved.

    Sets a transient `_role_changed` flag on the instance so that the
    `post_save` handler (`sync_role_group`) knows whether it needs to
    resync the user's role-based group membership. This avoids an
    unnecessary DB query/update on every save when the role hasn't changed.

    Behavior:
        - New instances (not yet in the DB) are always treated as changed.
        - If `update_fields` is provided and doesn't include 'role',
          the role is assumed unchanged.
        - Otherwise, the current DB value of `role` is fetched and compared
          against the in-memory value to determine if it changed.

    Args:
        sender (type): The model class (User).
        instance (User): The User instance about to be saved.
        update_fields (frozenset | None): Fields passed to `save(update_fields=...)`,
            if any.
        **kwargs: Additional signal arguments (unused).
    """
    if instance._state.adding:
        instance._role_changed = True
        return

    if update_fields is not None and "role" not in update_fields:
        instance._role_changed = False
        return

    old_role = sender.objects.only("role").get(pk=instance.pk).role
    instance._role_changed = old_role != instance.role


@receiver(post_save, sender=User)
def sync_role_group(sender, instance, **kwargs):
    """Sync a User's group membership to match their current role, if it changed.

    Runs after save and checks the `_role_changed` flag set by
    `detect_role_change`. If the role changed (or the user is newly created),
    it ensures a Group named `f"{ROLE_GROUP_PREFIX}{instance.role}"` exists
    and sets it as the user's *only* group, replacing any previous
    role-based group membership.

    Args:
        sender (type): The model class (User).
        instance (User): The User instance that was just saved.
        **kwargs: Additional signal arguments (unused).
    """
    if not getattr(instance, "_role_changed", False):
        return

    role_group, _ = Group.objects.get_or_create(
        name=f"{ROLE_GROUP_PREFIX}{instance.role}"
    )
    instance.groups.set([role_group])