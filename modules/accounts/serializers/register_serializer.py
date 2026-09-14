from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from ..models import UserRole

User = get_user_model()

# Single source of truth for which fields this endpoint accepts. Used both in Meta.fields and in the extra-fields check below.
ALLOWED_FIELDS = ["email", "password", "first_name", "last_name", "role"]
ALLOWED_ROLE_CHOICES = [UserRole.USER, UserRole.INSTRUCTOR, UserRole.COMPANY]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles both validation AND persistence for user registration (no separate service layer -- create() does the DB write directly).
    """

    # Declared explicitly (instead of relying on the model field alone) so we can restrict which roles are self-registrable. ADMIN is deliberately excluded -- admin accounts should never be creatable through a public endpoint.
    role = serializers.ChoiceField(choices=ALLOWED_ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["id"] + ALLOWED_FIELDS  # DRF accepts a list here 
        extra_kwargs = {
            "password": {"write_only": True}  # never echoed back in the API response
        }
        read_only_fields = ["id"] 

    def validate_email(self, value):
        """
        Field-level validator -- DRF calls this automatically for the 'email' field during is_valid(). Runs before object-level validate().
        """
        # Check for uniqueness of email. The User model itself has a unique constraint on email, but we want to catch this at the serializer level so we can return a clear error.
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_password(self, value):
        """
        Runs Django's built-in password validators (AUTH_PASSWORD_VALIDATORS in settings.py -- e.g. min length, common-password check, similarity to user attributes).

        IMPORTANT: validate_password() returns None on success and raises django.core.exceptions.ValidationError (NOT DRF's ValidationError) on failure. We must:
          1. NOT assign its return value to anything (it's always None -- an earlier version of this code did `password = validate_password(...)` which silently set the password to None for every user).
          2. Catch Django's ValidationError and re-raise as DRF's ValidationError, otherwise this bubbles up as an unhandled 500 instead of a clean 400.
        """
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """
        Object-level validation -- runs after all field-level validators pass.

        NOTE on extra fields: by the time we're inside validate(), `attrs` only ever contains keys DRF already knows about (declared serializer fields). Unknown keys sent by the client are dropped before attrs is built -- they never make it in, so checking `attrs.keys()` here can never catch them.
        To detect fields the client sent that we don't accept (e.g. a typo like `role_name` instead of `role`, or a client trying to sneak in something like `is_staff`), we must check `self.initial_data` instead -- this holds the raw, unfiltered input exactly as the client sent it.
        This is NOT a security fix (DRF already silently ignores unknown fields, so nothing unsafe can leak into validated_data regardless). It's purely about giving the client a clear error instead of silently ignoring a typo.
        """
        extra_fields = set(self.initial_data.keys()) - set(ALLOWED_FIELDS)
        if extra_fields:
            raise serializers.ValidationError(
                f"Extra fields are not allowed: {', '.join(extra_fields)}"
            )
        return attrs

    def create(self, validated_data):
        """
        Goes through User.objects.create_user() (from your UserManager), NOT User.objects.create(**validated_data) or User(**validated_data).save().

        This matters because create_user() calls set_password(), which hashes the password before saving. The default ModelSerializer.create() / plain model instantiation would store the password in plain text.
        """
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # Registration should never update an existing user -- if this is ever
        # called, something upstream is misusing this serializer.
        raise NotImplementedError("Update method is not implemented for RegisterSerializer.")