from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers.register_serializer import RegisterSerializer

class RegisterView(APIView):
    """
    POST /register/
    Public endpoint -- no authentication required to sign up.
    """

    # AllowAny overrides any global DEFAULT_PERMISSION_CLASSES (e.g. IsAuthenticated) that might otherwise block unauthenticated access to this view.
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Pass raw request data into the serializer for validation.
        serializer = RegisterSerializer(data=request.data)

        # raise_exception=True automatically returns a 400 response with the serializer's error dict if validation fails -- no need to manually check serializer.is_valid() and return errors ourselves.
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Re-serialize the saved user to get a clean output dict (email, first_name, last_name, role) via output.data -- this internally calls the serializer's to_representation().
        output = RegisterSerializer(user)

        return Response(
            data=output.data,
            status=status.HTTP_201_CREATED,
        )