import uuid
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from .models import User, Subscription
from .serializers import UserCreateSerializer, SetAvatarSerializer, SetPasswordSerializer
from .serializers import (
    UserSerializer
)
from django.core.mail import send_mail
from .serializers import UsersRecipesSerializer
from rest_framework.authtoken.models import Token
import requests
from rest_framework.decorators import api_view, permission_classes


class CustomUserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


User = get_user_model()


class SubscriptionListView(generics.ListAPIView):
    serializer_class = UsersRecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(subscribers__subscriber=self.request.user)



class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        author = get_object_or_404(User, pk=id)
        if author == request.user:
            return Response({'error': 'Нельзя подписаться на себя.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscription.objects.get_or_create(subscriber=request.user, author=author)
        if not created:
            return Response({'error': 'Вы уже подписаны.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UsersRecipesSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(subscriber=request.user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Вы не подписаны на данного пользователя.'}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = SetAvatarSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.avatar = serializer.validated_data['avatar']
            user.save()
            return Response({"avatar": user.avatar.url if user.avatar else None}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({"current_password": ["Неверный текущий пароль."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
User = get_user_model()

class GitHubOAuthTokenLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Code not provided"}, status=400)

        token_resp = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        token_json = token_resp.json()
        access_token = token_json.get("access_token")

        if not access_token:
            return Response({"error": "Invalid GitHub code"}, status=400)

        user_resp = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_resp.json()
        
        print(user_data)

        email = user_data.get("email")

        if not email:
            email_resp = requests.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails = email_resp.json()
            print(emails)
            email = next((e["email"] for e in emails if e.get("primary")), None)

        if not email:
            return Response({"error": "Email not found"}, status=400)

        user, created = User.objects.get_or_create(email=email, defaults={
            "username": email.split("@")[0]
        })

        # Получаем или создаём токен
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "auth_token": token.key
        })


def generate_password():
    return str(uuid.uuid4())

@api_view(['POST'])
def reset_password_and_send_new(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    new_password = generate_password()

    user.set_password(new_password)
    user.save()

    send_mail(
        subject='Ваш новый пароль',
        message=f'Здравствуйте, ваш новый пароль: {new_password}\nПожалуйста, смените его после входа.',
        from_email='zakiroffkam@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({'detail': 'Новый пароль отправлен на email'}, status=status.HTTP_200_OK)