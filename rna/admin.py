# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django import forms
from django.contrib import admin
from pagedown.widgets import AdminPagedownWidget

from . import models


class NoteAdminForm(forms.ModelForm):
    note = forms.CharField(widget=AdminPagedownWidget())
    releases = forms.ModelMultipleChoiceField(
        required=False, queryset=models.Release.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Releases', is_stacked=False))

    class Meta:
        model = models.Note


class NoteAdmin(admin.ModelAdmin):
    form = NoteAdminForm
    list_display = ('id', 'bug', 'tag', 'note', 'created')
    list_display_links = ('id',)
    list_filter = ('tag', 'is_known_issue', 'releases__product',
                   'releases__version')
    search_fields = ('bug', 'note', 'releases__version')


class ReleaseAdminForm(forms.ModelForm):
    system_requirements = forms.CharField(widget=AdminPagedownWidget(),
                                          required=False)
    text = forms.CharField(widget=AdminPagedownWidget(), required=False)
    release_date = forms.DateTimeField(widget=admin.widgets.AdminDateWidget)

    class Meta:
        model = models.Release


class ReleaseAdmin(admin.ModelAdmin):
    form = ReleaseAdminForm
    list_display = ('version', 'product', 'channel', 'is_public',
                    'release_date', 'text')
    list_filter = ('product', 'channel', 'is_public')
    ordering = ('-release_date',)
    search_fields = ('version', 'text')


admin.site.register(models.Note, NoteAdmin)
admin.site.register(models.Release, ReleaseAdmin)
