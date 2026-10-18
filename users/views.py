from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.pagination import StandardPagination
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserDetailSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    Kullanıcı oluşturur ve HEMEN token döner (otomatik login).
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Otomatik login: token üret
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/users/login/
    {'username': ..., 'password': ...} → {'access', 'refresh', 'user'}
    """
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(generics.GenericAPIView):
    """
    POST /api/users/logout/
    {'refresh': '...'} → refresh token'ı blacklist'e ekler.
    Access token'ı frontend siler (stateless).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token gerekli.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'detail': 'Çıkış yapıldı.'},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {'detail': 'Geçersiz veya zaten iptal edilmiş token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/users/me/  → kendi profilim
    PATCH /api/users/me/  → profil güncelle (bio, avatar, first_name...)
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/users/                 → kullanıcı listesi
    GET /api/users/{username}/      → profil detayı
    POST /api/users/{username}/follow/    → takip et
    POST /api/users/{username}/unfollow/  → takipten çık
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    lookup_field = 'username'
    lookup_value_regex = r'[\w.@+-]+'   # Django User'ın kabul ettiği karakterler

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, username=None):
        target = self.get_object()
        if target == request.user:
            return Response(
                {'detail': 'Kendinizi takip edemezsiniz.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.following.add(target)
        return Response({'detail': f'@{target.username} takip edildi.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, username=None):
        target = self.get_object()
        request.user.following.remove(target)
        return Response({'detail': f'@{target.username} takipten çıkıldı.'})