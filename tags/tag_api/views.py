from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django import forms
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction
# from cloud_service_app.models.tags_model import TagsModel
# from cloud_service_app.forms.forms import tags_form 
from django.utils import timezone
import datetime
from rest_framework.views import APIView
# import requests
from django.db.models import Q
# from cloud_service_app.helpers import *
import json
from django.utils.translation import gettext as _

from .models import TagsModel, VM
from .forms import tags_form, VMForm


class Tags(APIView):
    def get(self,request):
        try:
            filters = Q()
            if request.method == 'GET' and 'id' in request.GET:
                id = request.GET['id']
                filters &= Q(id=id)

            if request.method == 'GET' and 'tag_name' in request.GET:
                tag_name = request.GET['tag_name']
                filters &= Q(tag_name=tag_name)

            if request.method == 'GET' and 'scope' in request.GET:
                scope = request.GET['scope']
                filters &= Q(scope=scope)

            if not filters:
                tags_data = TagsModel.objects.all().values()
            
            else:
                tags_data = TagsModel.objects.filter(filters).values()

            list_result = [entry for entry in tags_data]
            
            data = {'status':'success','error_code': 0, 'message': _("Tags get successfully"), 'data':list_result}
            return JsonResponse(data)


        except ValidationError as e:
            data = {'status':'error','error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except NameError as e:
            data = {'status':'error','error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)
		

    def post(self,request):
        try:
            form = tags_form(request.POST)
            if form.is_valid():
                tag_name = request.POST.get('tag_name')
                scope = request.POST.get('scope',default=None)   

                tag = TagsModel()
                tag.tag_name = tag_name
                tag.scope = scope

                tag_data = tag.save(force_insert=True)

            data = {'status':'success','error_code': 0, 'message': _("Tag Added successfully"), 'data':''} 

            return JsonResponse(data)
    
        except ValidationError as e:
            data = {'status':'error','error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except NameError as e:
            data = {'status':'error','error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)


    def delete(self,request):
        try:
            id = request.GET.get('id')

            if id==None or id=='None' or id=='':
                data = {'status':'error','error_code': 100, 'message': _('Tag id is required')}
                return JsonResponse(data)

            id = int(id)

            if id != '' and id > 0:
                is_exist = TagsModel.objects.filter(id=id).count()

                if is_exist > 0:
                    
                    delete_tag = TagsModel.objects.filter(id=id).delete()

                    data = {'status':'success','error_code': 0, 'message': _("Tag deleted successfully.")}
                    return JsonResponse(data)

                else:
                    data = {'status':'error','error_code': 100, 'message': _("Invalid Request.")}
                    return JsonResponse(data)
            else:
                data = {'status':'error','error_code': 100, 'message': _("Invalid Request.")}
                return JsonResponse(data)

        except NameError as e:
            data = {'status':'error','error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except KeyError as e:
            data = {'status':'error','error_code': 102, 'message': "error: {0} is required".format(e)}
            return JsonResponse(data)

        except Exception as e:
            data = {'status':'error','error_code': 101, 'message': "error: {0}".format(e)}        
            return JsonResponse(data)
        

class AssignUnassignTags(APIView):

    def post(self, request):

        try:
            action = request.POST.get('action')

            if action == 'assign':
                tag_id = request.data.get('tag_id')
                demo_vm_ids = request.data.getlist('demo_vm_ids')

                tag = get_object_or_404(TagsModel, id=tag_id)

                tag.vms.add(*demo_vm_ids)

                data = {'status': 'success', 'error_code': 0, 'message': _("Tag Assigned to Objects successfully"), 'data': ''}
                return JsonResponse(data)

            elif action == 'unassign':
                tag_id = request.POST.get('tag_id')

                demo_vm_ids = request.POST.getlist('demo_vm_ids')

                tag = get_object_or_404(TagsModel, id=tag_id)

                tag.vms.remove(*demo_vm_ids)

                data = {'status':'success', 'error_code': 0, 'message': _("Tag Unassigned from Objects successfully"), 'data': ''}
                return JsonResponse(data)

            else:
                data = {'status':'error', 'error_code': 108, 'message': _("Invalid action")}
                return JsonResponse(data)

        except ValidationError as e:
            data = {'status':'error', 'error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except Exception as e:
            data = {'status':'error', 'error_code': 101, 'message': "error: {0}".format(e)}        
            return JsonResponse(data)


# =============================================================================================================================
        

class VMs(APIView):
    def get(self, request):
        try:
            tag_name = request.GET.get('tag_name')
            scope = request.GET.get('scope')

            queryset = VM.objects.all()

            if tag_name:
                queryset = queryset.filter(tags__tag_name=tag_name)

            if scope:
                queryset = queryset.filter(tags__scope=scope)

            vm_data = queryset.values()
            vm_list_result = [entry for entry in vm_data]

            data = {'status': 'success', 'error_code': 0, 'message': _("VMs retrieved successfully"), 'data': vm_list_result}
            return JsonResponse(data)
        except Exception as e:
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)

    def post(self, request):
        try:
            form = VMForm(request.POST)

            vm_name = request.POST.get('vm_name')
            tag_name = request.POST.get('tags')
            scope = request.POST.get('scope')

            # Get or create the VM instance
            vm_instance, created = VM.objects.get_or_create(vm_name=vm_name)

            # Get the tag instance by name
            result = TagsModel.objects.get_or_create(tag_name=tag_name, scope=scope)
            tag_instance, created = result[0], result[1]

            # Assign the tag to the VM instance
            vm_instance.tags.add(tag_instance)

            data = {'status': 'success', 'error_code': 0, 'message': _("VM added successfully"), 'data': ''}
            return JsonResponse(data)

        except Exception as e:
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)

    def put(self, request, vm_id):
        try:
            vm_instance = VM.objects.get(id=vm_id)
            form = VMForm(request.POST, instance=vm_instance)

            if form.is_valid():
                # Save VM without committing to the database
                updated_vm_instance = form.save(commit=False)

                # Get tag IDs from the request
                tag_ids = request.POST.getlist('tags')

                # Assign tags to the updated VM instance
                updated_vm_instance.tags.set(tag_ids)

                # Save the updated VM instance to the database
                updated_vm_instance.save()

                data = {'status': 'success', 'error_code': 0, 'message': _("VM updated successfully"), 'data': ''}
                return JsonResponse(data)
            else:
                data = {'status': 'error', 'error_code': 103, 'message': f"Validation Error: {form.errors}"}
                return JsonResponse(data)

        except VM.DoesNotExist:
            data = {'status': 'error', 'error_code': 100, 'message': _("VM not found")}
            return JsonResponse(data)

        except Exception as e:
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)

    def delete(self, request, vm_id):
        try:
            vm = VM.objects.get(id=vm_id)
            vm.delete()

            data = {'status': 'success', 'error_code': 0, 'message': _("VM deleted successfully")}
            return JsonResponse(data)

        except VM.DoesNotExist:
            data = {'status': 'error', 'error_code': 100, 'message': _("VM not found")}
            return JsonResponse(data)

        except Exception as e:
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)

