from django import forms
from django.utils.dateparse import parse_datetime


class ISO8601DateTimeField(forms.DateTimeField):
    def strptime(self, value, format):
        return parse_datetime(value)
