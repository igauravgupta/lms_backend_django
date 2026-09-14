# Understanding Django Accounts

This guide explains how a custom user model works in Django and why the
accounts code is structured this way.

## 1. Why not use Django's default `User`?

Django's built-in user model already includes common fields such as:

- username
- first name
- last name
- email
- password

However, an application often needs additional fields such as a mobile number,
profession, profile image, or application-specific role. You cannot safely add
fields directly to Django's built-in model because it belongs to Django's
`auth` application.

Instead, you create a custom user model and tell Django to use it everywhere:

```python
AUTH_USER_MODEL = "accounts.User"
```

This setting means: use this model for authentication, the admin site,
permissions, groups, and `request.user`.

Set `AUTH_USER_MODEL` before creating the first migration. Changing the user
model later is difficult because many Django models reference it.

## 2. `AbstractBaseUser` versus `AbstractUser`

Django provides two common base classes for custom users:

| Base class | What it provides | Use it when |
| --- | --- | --- |
| `AbstractUser` | Django's normal username-based user fields and authentication behavior. | You want to keep most of Django's default user model and add a few fields. |
| `AbstractBaseUser` | Password handling and `last_login`. | You want complete control, such as logging in with email instead of username. |

This project uses `AbstractBaseUser` because email is the login identifier. The
custom model must define its own fields, manager, `USERNAME_FIELD`, and
`REQUIRED_FIELDS`.

## 3. Why a custom manager?

A manager provides methods such as `User.objects.create_user()` and
`User.objects.filter()`. Django's default user manager expects the standard
username setup, so a custom manager is used for an email-based user model.

Connect the manager to the model like this:

```python
class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
```

### `create_user()`

This method creates a normal user:

```python
user = User.objects.create_user(
    email="user@example.com",
    password="strong-password",
    first_name="Jane",
    last_name="Doe",
)
```

The manager normalizes the email and calls `set_password()`. `set_password()`
hashes the password, so raw passwords are never stored in the database.

### `create_superuser()`

This method is used by:

```powershell
uv run python manage.py createsuperuser
```

It sets the flags needed for Django admin access:

```python
is_staff = True
is_superuser = True
```

It also assigns the application's admin role. The method validates the admin
flags before saving the user.

## 4. `USERNAME_FIELD` and `REQUIRED_FIELDS`

```python
USERNAME_FIELD = "email"
REQUIRED_FIELDS = ["first_name", "last_name"]
```

`USERNAME_FIELD` tells Django which field identifies the user during login.
Here, email replaces username and must be unique.

`REQUIRED_FIELDS` is used only by the terminal `createsuperuser` command. Django
asks for these fields in addition to the email and password prompts. Do not put
`email` in this list because it is already `USERNAME_FIELD`.

## 5. `is_staff`, `is_superuser`, and application roles

These values have different purposes:

- `is_staff=True`: allows the user to enter the Django admin site.
- `is_superuser=True`: gives the user all Django permissions automatically.
- `role`: represents the application's business role, such as user, instructor,
  company, or admin.

A user can have `is_staff=True` without being a superuser. In that case, the
user can access the admin site only when they have the required permissions.

The application role and Django permissions are related concepts, but they are
not the same thing. A role is application data; groups and permissions control
Django authorization.

## 6. What is `PermissionsMixin`?

`PermissionsMixin` adds Django's permission system to a custom user model.
`AbstractUser` already includes it, but a model based on `AbstractBaseUser`
must add it explicitly:

```python
class User(AbstractBaseUser, PermissionsMixin):
```

Without it, features such as groups, permission checks, and superuser
permission handling would not be available.

### Fields added by `PermissionsMixin`

- `is_superuser`: when `True`, the user automatically has all permissions.
- `groups`: the groups to which the user belongs. A user receives permissions
  assigned to those groups.
- `user_permissions`: permissions assigned directly to the user.

### Methods added by `PermissionsMixin`

- `get_user_permissions()`: returns permissions assigned directly to the user.
- `get_group_permissions()`: returns permissions received through groups.
- `get_all_permissions()`: returns the combined direct and group permissions.
- `has_perm("app.permission")`: checks one permission.
- `has_perms([...])`: checks multiple permissions.
- `has_module_perms("app")`: checks whether the user has permissions for an app.

For example:

```python
user.has_perm("courses.add_course")
```

Django groups are useful for assigning the same permissions to many users. For
example, an `Instructors` group could receive permissions to create and update
courses.

## 7. Why use `UserRole(models.TextChoices)`?

`TextChoices` defines a fixed set of valid role values and gives each value a
machine-readable value and a human-readable label:

```python
class UserRole(models.TextChoices):
    USER = "user", "User"
    INSTRUCTOR = "instructor", "Instructor"
    ADMIN = "admin", "Admin"
    COMPANY = "company", "Company"
```

The database stores values such as `"instructor"`, while forms and admin pages
can display labels such as `"Instructor"`. Using choices prevents arbitrary
role strings from being used throughout the application.

## 8. Mapping a role to a group

The model maps each role to a Django group:

| Role | Group |
| --- | --- |
| `user` | `role:user` |
| `instructor` | `role:instructor` |
| `admin` | `role:admin` |
| `company` | `role:company` |

The model's `save()` method gets or creates the group for the current role and
uses:

```python
self.groups.set([role_group])
```

`set()` replaces the user's existing groups, so the user belongs only to the
group matching their current role. This is simple, but it removes any separate
permission or department groups whenever the user is saved.

The mapping runs when `save()` is called, including through
`User.objects.create_user()`. It does not run for bulk operations such as
`QuerySet.update()` or `bulk_update()` because those bypass `save()`.

## 9. Useful commands

Create and apply migrations after changing the model:

```powershell
uv run python manage.py makemigrations accounts
uv run python manage.py migrate
```

Check the Django project:

```powershell
uv run python manage.py check
```

Run account tests:

```powershell
uv run python manage.py test modules.accounts
```
