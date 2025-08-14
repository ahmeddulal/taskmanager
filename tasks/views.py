from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, generics, status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Task
from .serializers import TaskSerializer, RegisterSerializer
from .permissions import IsOwnerOrAdmin
from utils.response_handler import success_response, error_response

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(data=serializer.data, message="User registered successfully", status_code=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Wrap the JWT tokens in success_response
        if response.status_code == status.HTTP_200_OK:
            return success_response(data=response.data, message="Login successful")
        return error_response(message="Login failed", status_code=response.status_code, errors=response.data)


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return success_response(data=response.data, message="Token refreshed successfully")
        return error_response(message="Token refresh failed", status_code=response.status_code, errors=response.data)


class LogoutView(APIView):
    """Blacklist refresh token to logout."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return error_response(message="'refresh' token is required.", status_code=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()  # Ensure rest_framework_simplejwt.token_blacklist is installed
        except Exception:
            return error_response(message="Invalid refresh token.", status_code=status.HTTP_400_BAD_REQUEST)
        return success_response(message="Logged out successfully", data=None, status_code=status.HTTP_200_OK)



class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Override list
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Tasks retrieved successfully")

    # Override retrieve
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Task retrieved successfully")

    # Override create
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(data=serializer.data, message="Task created successfully", status_code=status.HTTP_201_CREATED)

    # Override destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message="Task deleted successfully", data=None, status_code=status.HTTP_200_OK)
