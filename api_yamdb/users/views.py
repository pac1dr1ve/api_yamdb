from rest_framework import (
    filters,
    generics,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.permissions import IsAdminUserOrSuperuser
from users.serializers import (
    SignUpSerializer,
    UserSerializer,
    UserTokenSerializer,
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def sign_up_view(request):
    if request.method == 'POST':
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        return Response(validated_data, status=status.HTTP_200_OK)


class UserMeView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = "username"
    search_fields = ("username",)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.action in [
            "destroy",
            "retrieve",
            "partial_update",
            "create",
            "list",
        ]:
            self.permission_classes = [IsAdminUserOrSuperuser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(
                username=serializer.validated_data.get("username")
            )
            token = RefreshToken.for_user(user)
            data = {
                "token": str(token.access_token),
            }
            return Response(data, status=status.HTTP_200_OK)

        except TokenError as e:
            raise InvalidToken(e.args[0])

        except User.DoesNotExist:
            return Response(
                "Пользователь не найден",
                status=status.HTTP_404_NOT_FOUND,
            )
