from django.urls import path
from .views import *

urlpatterns = [
    path('groupCreation/page/', group_creation_page, name="group-creation"),
    path('page/', group_page, name="groups-listing"),

    # Group Management
    path("", GroupListingAndCreation.as_view(), name="group-list-create"),  # List all groups & create a new one
    path("<int:id>/", SpecificGroupView.as_view(), name="group-detail"),  # Fetch, update, delete a group

    # Group Membership Management
    path("<int:id>/members/", getMembers, name="group-members"),  # List all members in a group
    path("<int:group_id>/members/<int:member_id>/", getAMember, name="get-a-member"), # Get a member of a group
    path("<int:id>/members/add/", addMember, name="add-member"),  # Add a user to a group
    path("<int:group_id>/members/remove/<int:member_id>/", removeMember, name="remove-member"),  # Remove a user
    path("<int:group_id>/members/leave/<int:member_id>/", leaveGroup, name="remove-member"), # Leave a group
    path("<int:group_id>/members/promote/<int:member_id>/", promoteToOwner, name="remove-member"), # Promote
]