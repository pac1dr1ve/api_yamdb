from rest_framework import (
    filters,
    permissions,
    status,
    viewsets,
    serializers,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
    action,
)
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)
from rest_framework_simplejwt.tokens import RefreshToken

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
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.save()
    return Response(validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ["username"]
    lookup_field = "username"
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
            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        elif request.method == "PATCH":
            if ("username" in request.data and
                    request.data["username"].lower() == "me"):
                return Response(
                    {"detail": "Использовать 'me' "
                               "в качестве username запрещено."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_token_obtain_pair_view(request):
    serializer = UserTokenSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data["username"])
        token = RefreshToken.for_user(user)
        return Response(
            {"token": str(token.access_token)},
            status=status.HTTP_200_OK
        )
    except NotFound as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except TokenError as e:
        raise InvalidToken(e.args[0])
    except serializers.ValidationError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
