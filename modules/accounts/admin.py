from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class AccountAdmin(admin.ModelAdmin):
    """Admin configuration for the custom User (Account) model.

    Provides a list view with key user attributes, search and filter
    capabilities, and bulk actions for activating/deactivating users.
    Sensitive/auto-managed fields (timestamps, password reset tokens)
    are exposed as read-only.
    """

    list_display = ('id', 'email', 'full_name', 'mobile', 'is_active', 'is_staff', 'is_superuser', 'role')
    list_filter = ('is_active', 'is_superuser', 'role')
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    readonly_fields = ('created_at', 'updated_at', 'reset_password_token', 'reset_password_expire')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'mobile', 'profession', 'profile_image')}),
        ('Roles & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_blocked', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    actions = ('activate_users', 'deactivate_users')
    # helps to display the many-to-many fields in a more user-friendly way in the admin interface while viewing or editing a User instance. It provides a dual list box interface where you can select and move items between the available and selected lists.
    filter_horizontal = ('groups', 'user_permissions')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        """Admin action to mark selected users as active.

        Args:
            request: The current HttpRequest.
            queryset: QuerySet of User instances selected in the admin list view.
        """
        queryset.update(is_active=True)
        self.message_user(request, 'Selected users were activated.')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        """Admin action to mark selected users as inactive.

        Args:
            request: The current HttpRequest.
            queryset: QuerySet of User instances selected in the admin list view.
        """
        queryset.update(is_active=False)
        self.message_user(request, 'Selected users were deactivated.')

    @admin.display(description='Full Name')
    def full_name(self, obj):
        """Return the user's full name for display in the admin list view.

        Args:
            obj (User): The user instance being rendered.

        Returns:
            str: The value of `obj.full_name`.
        """
        return obj.full_name

    def save_model(self, request, obj, form, change):
        raw_password = form.cleaned_data.get('password')

        if not change and not raw_password:
            # Blocking create-without-password
            form.add_error('password', "Password is required when creating a new user.")
            raise ValidationError("Password is required when creating a new user.")

        if raw_password:
            obj.set_password(raw_password)
        elif change:
            # Blank on edit = keep existing hash; reload it so we don't overwrite with plaintext
            obj.password = User.objects.get(pk=obj.pk).password

        super().save_model(request, obj, form, change)