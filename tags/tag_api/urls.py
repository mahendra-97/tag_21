from django.urls import path, include
from .views import Tags, VMs, AssignUnassignTags

urlpatterns = [
   
    # Tags API
    path('tags', Tags.as_view()),
    path('tags/<str:id>', Tags.as_view()),
    path('Assign_Unassign_vm', AssignUnassignTags.as_view()),

    # VMs API
    path('vms', VMs.as_view(), name='vms'),
    path('vms/<int:vm_id>', VMs.as_view()),
]