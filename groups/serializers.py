from rest_framework import serializers
from .models import *

class GroupCreationAndListingSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)  

    class Meta:
        model = Group
        fields = ['id', 'name', 'is_read_only', 'created_at', 'owner_name']
        # 'id' -> Group Id

class MemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    group_id = serializers.CharField(source='group.id', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    member_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Member
        fields = ['user_id', 'user_name', 'role', 'group_id', 'group_name', 'member_id', 'joined_at']
        # 'id' -> Member Id (not the id from User DB)


