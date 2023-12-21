from django.db import models
from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import uuid
from django.http import JsonResponse

class TagsModel(models.Model):

    tag_name  = models.CharField('tag_name',max_length=255,unique=True)
    scope  = models.CharField('scope',max_length=255,blank=True)
    # vms = models.ManyToManyField('VM',related_name='tags')

    class Meta:
        managed = True
        db_table = 'tags'
        verbose_name = 'tags'


class VM(models.Model):
    vm_name = models.CharField('vm_name', max_length=255, unique=True)
    creation_date = models.DateTimeField('creation_date', auto_now_add=True)
    tags = models.ManyToManyField('TagsModel', related_name='vms')

    class Meta:
        managed = True
        db_table = 'vms'
        verbose_name = 'vms'