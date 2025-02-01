from rest_framework import (
    filters,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import api_view, permission_classes, action
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


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def sign_up_view(request):
    if request.method == 'POST':
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        return Response(validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = [IsAdminUserOrSuperuser]

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user

        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "PATCH":
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


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
