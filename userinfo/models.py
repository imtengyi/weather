from __future__ import unicode_literals
from django.db import models

# Create your models here.
from django import forms


class User(models.Model):
    id = models.AutoField(primary_key = True, max_length = 11, name = 'id')
    name = models.CharField(max_length = 6, name = 'name')
    phone = models.CharField(max_length = 11, name = 'phone')
    city_name = models.CharField(max_length = 6, name = 'city_name')
    send_sms_time = models.CharField(max_length = 10, name = 'send_sms_time')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('id',)


