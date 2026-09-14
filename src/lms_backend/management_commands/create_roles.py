from modules.accounts.models import ROLE_GROUP_PREFIX

def create_role_groups():
    """Create role-based groups for all defined roles in UserRole.

    This function iterates over all roles defined in the UserRole
    enumeration and ensures that a corresponding Group exists for each
    role. The group names are prefixed with `ROLE_GROUP_PREFIX` to
    distinguish them from other groups.

    If a group for a role already exists, it is left unchanged. If it
    does not exist, it is created.

    Returns:
        list: A list of the created or existing Group instances.
    """
    from modules.accounts.models import UserRole
    from django.contrib.auth.models import Group

    created_groups = []
    for role in UserRole.values:
        group_name = f"{ROLE_GROUP_PREFIX}{role}"
        group, created = Group.objects.get_or_create(name=group_name)
        created_groups.append(group)

    return created_groups

create_role_groups()