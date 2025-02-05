from rest_framework import (
    filters,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
    action,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdminUserOrSuperuser
from users.models import User
from users.serializers import (
    SignUpSerializer,
    UserSerializer,
    UserTokenSerializer, UserNoAdminSerializer,
)


@api_view(("POST",))
@permission_classes((permissions.AllowAny,))
def sign_up_view(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.save()
    return Response(validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "patch", "delete")
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    permission_classes = (IsAdminUserOrSuperuser,)

    # Для выбора сериализатора в зависимости от роли
    def get_serializer_class(self):
        if (self.request.user.is_authenticated
                and self.request.user.role == "admin"):
            return UserSerializer
        return UserNoAdminSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    def patch_me(self, request):
        user = request.user
        # if ("username" in request.data
        #         and request.data["username"].lower() == "me"):
        #     return Response(
        #         {"detail": "Использовать 'me' "
        #                    "в качестве username запрещено."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        serializer = UserNoAdminSerializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(("POST",))
@permission_classes((permissions.AllowAny,))
def get_token_obtain_pair_view(request):
    serializer = UserTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.validated_data['token']
    return Response({"token": token}, status=status.HTTP_200_OK)
