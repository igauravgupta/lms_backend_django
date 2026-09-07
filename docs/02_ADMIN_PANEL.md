# Django Admin: Complete Guide

## 1. What Is Django Admin?

Django Admin is Django's built-in web-based management interface. It inspects
your models and automatically generates forms, list views, search, filters,
and CRUD operations.

Authorized users can use the admin site to:

- View, create, update, and delete database records
- Search, filter, and sort records
- Manage users, groups, and permissions
- Manage model relationships
- Perform bulk actions
- Customize how models are displayed

## 2. Basic Setup

1. Add `django.contrib.admin` to `INSTALLED_APPS`.
2. Add the admin URL in `config/urls.py`.
3. Register your models in an app's `admin.py`.
4. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

## 3. Registering Models

### Basic Registration

Basic registration provides the default list and detail views:

```python
from django.contrib import admin

from .models import Product

admin.site.register(Product)
```

### Custom `ModelAdmin`

`ModelAdmin` is the standard way to customize the admin interface:

```python
from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    list_editable = ('price',)
    prepopulated_fields = {'slug': ('name',)}
```

## 4. Useful `ModelAdmin` Options

| Option | Purpose |
| --- | --- |
| `list_display` | Columns shown in the list view |
| `list_filter` | Filters shown in the sidebar |
| `search_fields` | Enables the search box |
| `list_editable` | Fields editable directly in the list view |
| `readonly_fields` | Fields that cannot be edited in the detail form |
| `fieldsets` | Groups and organizes fields in the detail form |
| `autocomplete_fields` | Searchable foreign key and many-to-many fields |
| `date_hierarchy` | Date-based drill-down navigation |
| `raw_id_fields` | ID inputs for large foreign key tables |

## 5. Permissions and Access Control

Django Admin uses the built-in `add`, `change`, `delete`, and `view`
permissions associated with users and groups. You can further restrict access
by overriding methods such as `has_add_permission()` and
`has_change_permission()` in `ModelAdmin`.

### Who Can Log In?

The user must be active and have `is_staff=True` to log in to `/admin/`:

```python
user.is_active = True
user.is_staff = True
user.save()
```

- Regular users (`is_staff=False`) cannot log in.
- Staff users (`is_staff=True`, `is_superuser=False`) can log in and can only
  access models for which they have permission.
- Superusers bypass model permission checks, but still need to be active and
  staff users to log in.

### Model-Level Permissions

Each model receives default permissions for adding, changing, deleting, and
viewing records. Permissions can be assigned in the admin UI or in code:

```python
from django.contrib.auth.models import Permission

user.user_permissions.add(permission)
```

### Groups

Groups bundle permissions and assign them to multiple users:

```python
from django.contrib.auth.models import Group

editors = Group.objects.create(name='Editors')
editors.permissions.add(can_change_post_permission)
user.groups.add(editors)
```

### Object-Level Permissions

Object-level permissions are not included in Django by default. They can be
implemented with a package such as `django-guardian`, or with custom
`ModelAdmin` permission methods. For example, only superusers can delete:

```python
class ProductAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
```

### Permissions Summary

| User type | Can log in | Sees all models | Can modify anything |
| --- | --- | --- | --- |
| Regular user (`is_staff=False`) | No | No | No |
| Staff user (`is_staff=True`) | Yes | Only permitted models | Only permitted actions |
| Superuser | Yes | Yes | Yes |

In short, staff status allows access to the admin site. Permissions determine
what a staff user can manage, while superusers bypass model permission checks.

## 6. Custom Filters

`SimpleListFilter` allows custom filtering beyond plain model fields:

```python
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Under $50'),
            ('high', '$50+'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(price__lt=50)
        if self.value() == 'high':
            return queryset.filter(price__gte=50)
        return queryset


class ProductAdmin(admin.ModelAdmin):
    list_filter = (PriceRangeFilter,)
```

## 7. Custom Admin Actions

Admin actions operate on selected records. Use `queryset.update()` for simple
database updates when no model save logic or signals are required:

```python
@admin.action(description='Activate selected users')
def activate_users(self, request, queryset):
    queryset.update(is_active=True)
    self.message_user(request, 'Selected users were activated.')
```

Use per-object `save()` instead when custom save logic or signals must run.
Remember that `queryset.update()` does not call `save()` or trigger save
signals.

## 8. Computed Fields in `list_display`

Admin list views can display values that are not direct model fields:

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_display', 'item_count')

    @admin.display(description='Total ($)')
    def total_display(self, obj):
        return f'${obj.total:.2f}'

    @admin.display(description='Items')
    def item_count(self, obj):
        return obj.items.count()
```
## 9. `ModelAdmin` Methods

`ModelAdmin` provides hook methods for saving, deleting, and performing bulk
operations. The main difference is whether the method receives one model
instance or a `QuerySet`.

### Admin Hook Summary

| Method | Triggered by | Operates on | Underlying call |
| --- | --- | --- | --- |
| `save_model(request, obj, form, change)` | Saving one object through an add or change form | One instance | `obj.save()` |
| `delete_model(request, obj)` | Deleting one object from its detail or confirmation page | One instance | `obj.delete()` |
| `delete_queryset(request, queryset)` | The bulk **Delete selected** action | `QuerySet` | `queryset.delete()` |
| Custom actions | Any custom bulk action you define | `QuerySet` | Whatever implementation you provide |

### `save_model`

`save_model()` handles saving one object through the admin form. Django's
default implementation calls the model instance's `save()` method:

```python
def save_model(self, request, obj, form, change):
    """Save a model instance to the database."""
    obj.save()
```

`obj` is one model instance, not a queryset. Override this method when you need
to set additional values, such as the user who created the object:

```python
def save_model(self, request, obj, form, change):
    obj.created_by = request.user
    super().save_model(request, obj, form, change)
```

### `delete_model`

`delete_model()` handles deleting one object from the detail or confirmation
page. Django's default implementation calls `obj.delete()`:

```python
def delete_model(self, request, obj):
    """Delete one model instance from the database."""
    obj.delete()
```

Override it when you need additional cleanup or auditing for an individual
deletion. Otherwise, the default implementation is sufficient.

### `delete_queryset`

`delete_queryset()` handles the bulk **Delete selected** action. It receives a
`QuerySet`, so the default implementation deletes all selected records at
once:

```python
def delete_queryset(self, request, queryset):
    """Delete the selected records from the database."""
    queryset.delete()
```

Override it when bulk deletion needs custom per-object behavior:

```python
def delete_queryset(self, request, queryset):
    for obj in queryset:
        obj.delete()
```

### Custom Admin Actions

Custom actions also receive a `QuerySet`. Use `queryset.update()` for simple
database updates when model `save()` logic and save signals are not required:

```python
@admin.action(description='Activate selected users')
def activate_users(self, request, queryset):
    queryset.update(is_active=True)
```

Use a loop with `obj.save()` instead when each object must run custom save
logic or save signals. `queryset.update()` does not call `save()` or trigger
`pre_save` and `post_save` signals.