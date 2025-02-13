from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()  # Use the custom user model

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'Please provide username, email, and password'},
                        status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'},
                        status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Assign 'User' role by default
    user = User.objects.create_user(username=username, email=email, password=password, role='User')

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'User created successfully',
        'role': user.role,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username,
        'email': user.email,
    }, status=status.HTTP_201_CREATED)

def register_page(request):
    return render(request, 'register.html')

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    authenticated_user = authenticate(username=username, password=password)
    if authenticated_user is None:
        return Response({'error': 'Invalid credentials'},
                        status=status.HTTP_400_BAD_REQUEST)
     
    refresh = RefreshToken.for_user(authenticated_user)
    return Response({
        'message': 'User logged in successfully',
        'role': authenticated_user.role,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': authenticated_user.username,
        'email': authenticated_user.email, 
        'id': authenticated_user.id   
    },
    status=status.HTTP_200_OK) 

def login_page(request):
    return render(request, 'login.html')

def group_directions_page(request):
    return render(request, 'groupDirection.html')
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)


            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response({"username": request.user.username, "role": request.user.role, "user_id": request.user.id})


