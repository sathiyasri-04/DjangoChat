from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from .models import *
from .serializers import *
from credentials.models import UserRole

def group_page(request):
    return render(request, 'groups.html')

def group_creation_page(request):
    return render(request, 'groupCreation.html')

class GroupListingAndCreation(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user
        groupName = request.data.get('name')
        readOnly = request.data.get('is_read_only')

        if not groupName:
            return Response({"error":"Enter group name. 'name' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if readOnly is None:
            return Response({"error":"'read-only' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Group.objects.filter(name=groupName).exists():
            return Response({"error":f"A group with name '{groupName}' already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = GroupCreationAndListingSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        group = serializer.save(owner=user) # user creating the group becomes owner
        if user.role!=UserRole.ADMIN: # ADMIN role can not be changed
            user.role = UserRole.OWNER # role = OWNER
            user.save(update_fields=['role']) # user role is updated to owner in User DB

        Member.objects.create(user=user, group=group)
        
        return Response({"data": serializer.data, "message": "Group created succesfully."}, status=status.HTTP_201_CREATED)

    def get(self, request):

        groups = Group.objects.all()
        serializer = GroupCreationAndListingSerializer(groups, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SpecificGroupView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, id): # id -> Group Id
        
        group = Group.objects.filter(id=id).first()

        if not group:
            return Response({"error":f"Group with id: {id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GroupCreationAndListingSerializer(group)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id): # id -> Group Id

        '''
        Only Admin or Owner can delete a group.
        '''
        
        group = Group.objects.filter(id=id).first()

        if not group:
            return Response({"error":f"Group with id: {id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if request.user!=group.owner and request.user.role!=UserRole.ADMIN:
            return Response({"error":"Only admin and owner can delete a group."}, status=status.HTTP_403_FORBIDDEN)
        
        groupName = group.name

        group.delete()

        return Response({"message":f"Group, '{groupName}' with id:'{id}' has been deleted successfully by {request.user.username} of role: {request.user.role}"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addMember(request, id): # id -> Group Id

    group = Group.objects.filter(id=id).first()

    if not group:
        return Response({"error":f"Group with id: {id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    member = Member.objects.filter(user=request.user, group=group).first()

    if member:
        return Response({"error":f"Member with id:{member.id} already exists in Group, '{group.name}' with group_id: {group.id}"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = MemberSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save(user=request.user, group=group) #manually setting 'user' and 'group' as they are not passed in request.data or request body
    return Response({"data":serializer.data, "message":"Member has been added successfully."}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMembers(request, id): #id -> Group Id

    group = Group.objects.filter(id=id).first()

    if not group:
        return Response({"error":f"Group with id: {id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    members = Member.objects.filter(group=group)

    serializer = MemberSerializer(members, many = True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAMember(request, group_id, member_id): 

    group = Group.objects.filter(id=group_id).first()

    if not group:
        return Response({"error":f"Group with id: {group_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    member = Member.objects.filter(group=group, id=member_id).first()

    if not member:
        return Response({"error":f"Member with id: {member_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MemberSerializer(member)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def removeMember(request, group_id, member_id):

    group = Group.objects.filter(id=group_id).first()

    if not group:
        return Response({"error":f"Group with id: {group_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    member = Member.objects.filter(id=member_id, group=group).first()

    if not member:
        return Response({"error":f"Member with member_id:{member_id} does not exist in Group, '{group.name}'with group_id:{group_id}"}, status=status.HTTP_404_NOT_FOUND)
    
    groupName = group.name
    requestingRemoval = request.user #one who requests
    requestingRemovalRole = request.user.role 
    memberBeingRemoved = member.user #one who is being removed
    memberBeingRemovedRole = member.user.role 

    if requestingRemovalRole==UserRole.USER:
        return Response({"error":"Only Admin or Owner can remove user from group."}, status=status.HTTP_403_FORBIDDEN)

    if memberBeingRemovedRole==UserRole.USER:
        member.delete()
        return Response({"message":f"Member, '{memberBeingRemoved.username}' with member_id:{member_id} has been removed from Group, '{groupName}' with group_id:{group_id} by '{requestingRemoval.username}' of role:{requestingRemovalRole}"}, status=status.HTTP_200_OK)
    
    if memberBeingRemovedRole==UserRole.OWNER and requestingRemovalRole==UserRole.OWNER:
        return Response({"error":"Admin can only remove an owner."}, status=status.HTTP_403_FORBIDDEN)
    
    if memberBeingRemovedRole==UserRole.OWNER and requestingRemovalRole==UserRole.ADMIN:
        member.delete()
        group.owner = requestingRemoval
        group.save()
        #add here
        return Response({"message":f"Member, '{memberBeingRemoved.username}' with member_id:{member_id} has been removed from Group, '{groupName}' with group_id:{group_id} by '{requestingRemoval.username}' of role:{requestingRemovalRole}"}, status=status.HTTP_200_OK)
    
    if memberBeingRemovedRole==UserRole.ADMIN and requestingRemovalRole==UserRole.ADMIN:
        if member.user==group.owner:
            return Response({"error":"Admin, as a owner of a group cannot remove themself without promoting a user to an owner."})
    
    member.delete()
    return Response({"message":f"Admin, '{memberBeingRemoved.username}' with member_id:{member_id} has removed themself from Group, '{groupName}' and demoted from role: owner."})
# Admin has to become member and owner, if owner is removed -> to add this

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def leaveGroup(request, group_id, member_id):

    group = Group.objects.filter(id=group_id).first()

    if not group:
        return Response({"error":f"Group with id: {group_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    member = Member.objects.filter(id=member_id, group=group).first()

    if not member:
        return Response({"error":f"Member with member_id:{member_id} does not exist in Group, '{group.name}'with group_id:{group_id}"}, status=status.HTTP_404_NOT_FOUND)
    
    groupName = group.name
    requestingLeave = request.user #one who requests
    requestingLeaveRole = request.user.role 
    memberLeaving = member.user #one who is being removed
    memberLeavingRole = member.user.role 

    if requestingLeaveRole==UserRole.USER:
        if requestingLeave == memberLeaving:
            member.delete()
            return Response({"message":f"Member, '{memberLeaving.username}' with member_id:{member_id} has been removed from Group, '{groupName}' with group_id:{group_id}"}, status=status.HTTP_200_OK)
        else:
            return Response({"error":"A user can only remove their account."}, status=status.HTTP_403_FORBIDDEN)
    else:
        #add here
        return Response({"error":"An owner or an admin as the owner have to promote a user to owner before leaving the group."}, status=status.HTTP_400_BAD_REQUEST)
#Admin can leave if he is not the owner - to add this
# or delete group if only owner or admin exists and had to leave - add this one for sure
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def promoteToOwner(request, group_id, member_id): # member_id -> id of user becoming the owner

    requestingUserRole = request.user.role

    if requestingUserRole==UserRole.USER:
        return Response({"error":"Only Admin or Owner can promote a user to Owner"}, status=status.HTTP_403_FORBIDDEN)
    
    group = Group.objects.filter(id=group_id).first()

    if not group:
        return Response({"error":f"Group with id: {group_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    member = Member.objects.filter(id=member_id, group=group).first()

    if not member:
        return Response({"error":f"Member with member_id:{member_id} does not exist in Group, '{group.name}'with group_id:{group_id}"}, status=status.HTTP_404_NOT_FOUND)
    
    if group.owner==member:
        return Response({"error":f"'{member.user.username}' is already the Owner of the Group, '{group.name}'"}, status=status.HTTP_400_BAD_REQUEST)
    
    previousOwner = group.owner
    group.owner = member.user
    group.save()

    if previousOwner.role!=UserRole.ADMIN:
        previousOwner.role = UserRole.USER
        previousOwner.save(update_fields=['role'])

    if member.user.role!=UserRole.ADMIN:
        member.user.role = UserRole.OWNER
        member.user.save(update_fields=['role'])
    
    return Response({"message": f"'{member.user.username}' has been promoted to Owner of group '{group.name}'."}, status=status.HTTP_200_OK)
    
