from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from ..v1.serializers.register_serializer import RegisterSerializer

class RegisterView(APIView):
    """
    POST /register/
    Public endpoint -- no authentication required to sign up.
    """

    # AllowAny overrides any global DEFAULT_PERMISSION_CLASSES (e.g. IsAuthenticated) that might otherwise block unauthenticated access to this view.
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """
        Returns the serializer class to be used for this view.
        """
        if self.request.version == "v1":
            return RegisterSerializer
        return RegisterSerializer  # v1 default / fallback

    def post(self, request, *args, **kwargs):
        """
        Handles user registration. Expects a JSON payload with email, password, first_name, last_name, and role.
        """
        # Pass the request version to the serializer class to ensure the correct serializer is used based on the API version.
        serializer_class = self.get_serializer_class()

        # Pass raw request data into the serializer for validation.
        # raise_exception=True automatically returns a 400 response with the serializer's error dict if validation fails -- no need to manually check serializer.is_valid() and return errors ourselves.
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Re-serialize the saved user to get a clean output dict (email, first_name, last_name, role) via output.data -- this internally calls the serializer's to_representation().
        output = serializer_class(user)

        return Response(
            data=output.data,
            status=status.HTTP_201_CREATED,
        )