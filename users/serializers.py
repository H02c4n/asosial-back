from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Kullanıcıyı GÖSTERMEK için. Şifre asla dönmez.
    Post içinde author olarak da kullanılacak.
    """
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'avatar', 'date_joined',
            'followers_count', 'following_count',
        ]
        read_only_fields = fields  # tümü sadece okunur — güncelleme için ayrı serializer


class RegisterSerializer(serializers.ModelSerializer):
    """
    YENİ kullanıcı oluşturmak için. Şifre iki kez girilir,
    eşleşmeli ve Django validatörlerinden geçmeli.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Şifreler eşleşmiyor.'})
        return attrs

    def create(self, validated_data):
        # password2'yi çıkar (model alanı değil)
        validated_data.pop('password2')
        password = validated_data.pop('password')
        # create_user şifreyi hash'ler — create() DEĞİL!
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Profil güncelleme. username ve email değiştirilemez (güvenlik).
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'avatar']



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    SimpleJWT'nin default login response'una 'user' bilgisini de ekler.
    Böylece login sonrası ayrıca /me çağrısı yapmaya gerek kalmaz.
    """
    def validate(self, attrs):
        data = super().validate(attrs)     # {'access': '...', 'refresh': '...'}
        data['user'] = UserSerializer(self.user).data
        return data


class UserDetailSerializer(UserSerializer):
    """
    Profil detayında ekstra: 'ben bu kullanıcıyı takip ediyor muyum?'
    UserSerializer'ı bozmuyoruz; nested alan olarak post'larda sade kalıyor.
    """
    is_following = serializers.SerializerMethodField()
    is_me = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['is_following', 'is_me']
        read_only_fields = fields

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(pk=obj.pk).exists()
        return False

    def get_is_me(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and request.user == obj)