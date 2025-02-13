from django.db import models
from django.conf import settings
from credentials.models import UserRole

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)  
    is_read_only = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)  
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_groups")  # If the Owner account deleted from DB, owner left the group or owner removed from the group, the group will persist


class Member(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_memberships")
    #If user account deleted from DB, user left the group or removed from the group, the member record will be deleted
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")  
    #If the group is deleted, member records will be deleted.
    joined_at = models.DateTimeField(auto_now_add=True)

    def check_admin_or_owner(self, user):

        return user.role in [UserRole.ADMIN, UserRole.OWNER]

