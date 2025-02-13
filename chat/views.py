from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from credentials.models import UserRole
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from groups.models import *

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sendMessage(request):

    group_id = request.data.get('group')
    text = request.data.get('text', '').strip()
    user = request.user

    if not group_id:
        return Response({"error":"group is a required field."}, status=status.HTTP_400_BAD_REQUEST)
    if not text:
        return Response({"error":"text is a required field."}, status=status.HTTP_400_BAD_REQUEST)
    
    group = Group.objects.filter(id=group_id).first()
    if not group:
        return Response({"error":f"Group with id:{group_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    message_data = {
        "group": group_id,
        "sender": request.user.id, 
        "text": text
    }

    if not Member.objects.filter(user=user, group=group).exists():
        return Response({"error":f"User, {user.username} does not exist in Group, {group.name}"})
    
    if user.role==UserRole.USER and group.is_read_only==True:
        return Response({"error":"This group is readonly. Only admins can send message."})

    serializer = MessageSerializer(data=message_data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMessagesUserGroup(request, group_id, user_id):

    group = Group.objects.filter(id=group_id).first()

    if not group:
        return Response({"error":f"Group with id:{group_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    sender = User.objects.filter(id=user_id).first()

    if not sender:
        return Response({"error":f"User with id:{user_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role!=UserRole.ADMIN:
        return Response({"error":"Only admins can access"}, status=status.HTTP_400_BAD_REQUEST)

    
    messages = Message.objects.filter(group=group, sender=sender)

    serializer = MessageSerializer(messages, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMessagesOfGroup(request, group_id):

    group = Group.objects.filter(id=group_id).first()

    if not group:
        return Response({"error":f"Group with id:{group_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    messages = Message.objects.filter(group=group)

    serializer = MessageSerializer(messages, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAMessage(request, message_id):

    if request.user.role!=UserRole.ADMIN:
        return Response({"error":"Only admins can access"}, status=status.HTTP_400_BAD_REQUEST)

    message = Message.objects.filter(id=message_id).first()

    if not message:
        return Response({"error":f"Message with id:{message_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = MessageSerializer(message)

    return Response(serializer.data, status=status.HTTP_200_OK)

def chatGroup(request, group_id):
    print(group_id)
    group = Group.objects.filter(id=group_id).first()
    group_name = group.name
    return render(request, 'chatGroup.html', {'group_id': group_id})

