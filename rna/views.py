# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from itertools import chain
import json

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet

from . import models


def auth_token(request):
    if request.user.is_active and request.user.is_staff:
        token, created = Token.objects.get_or_create(user=request.user)
        return HttpResponse(
            content=json.dumps({'token': token.key}),
            content_type='application/json')
    else:
        return HttpResponseForbidden()


class NoteViewSet(ModelViewSet):
    model = models.Note


class ReleaseViewSet(ModelViewSet):
    model = models.Release


class NestedNoteView(generics.ListAPIView):
    model = models.Note

    def get_queryset(self):
        release = get_object_or_404(models.Release, pk=self.kwargs.get('pk'))
        return chain(*release.notes())
