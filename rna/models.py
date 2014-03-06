# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from django.db import models
from django_extensions.db.fields import CreationDateTimeField


class TimeStampedModel(models.Model):
    """
    Replacement for django_extensions.db.models.TimeStampedModel
    that updates the modified timestamp by default, but allows
    that behavior to be overridden by passing a modified=False
    parameter to the save method
    """
    created = CreationDateTimeField()
    modified = models.DateTimeField(editable=False, blank=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if kwargs.pop('modified', True):
            self.modified = datetime.now()
        super(TimeStampedModel, self).save(*args, **kwargs)


class Release(TimeStampedModel):
    CHANNELS = ('Nightly', 'Aurora', 'Beta', 'Release', 'ESR')
    PRODUCTS = ('Firefox', 'Firefox for Android',
                'Firefox Extended Support Release', 'Firefox OS')

    product = models.CharField(max_length=255,
                               choices=[(p, p) for p in PRODUCTS])
    channel = models.CharField(max_length=255,
                               choices=[(c, c) for c in CHANNELS])
    version = models.CharField(max_length=255)
    release_date = models.DateTimeField()
    text = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    bug_list = models.TextField(blank=True)
    bug_search_url = models.CharField(max_length=2000, blank=True)
    system_requirements = models.TextField(blank=True)

    def equivalent_release_for_product(self, product):
        """
        Returns the release for a specified product with the same
        channel and major version with the highest minor version,
        or None if no such releases exist
        """
        return (
            self._default_manager.filter(
                version__startswith=self.version.split('.')[0] + '.',
                channel=self.channel, product=product).order_by('-version')[:1]
            or [None])[0]

    def equivalent_android_release(self):
        if self.product == 'Firefox':
            return self.equivalent_release_for_product('Firefox for Android')

    def equivalent_desktop_release(self):
        if self.product == 'Firefox for Android':
            return self.equivalent_release_for_product('Firefox')

    def notes(self):
        """
        Retrieve a list of Note instances that should be shown for this
        release, sorted by tag and grouped as either new features or
        known issues.
        """
        tag_index = dict((tag, i) for i, tag in enumerate(Note.TAGS))
        notes = sorted(self.note_set.all(),
                       key=lambda note: tag_index.get(note.tag, 0))
        new_features = (note for note in notes if
                        not note.is_known_issue_for(self))
        known_issues = (note for note in notes if
                        note.is_known_issue_for(self))

        return new_features, known_issues

    def __unicode__(self):
        return '{product} v{version} {channel}'.format(
            product=self.product, version=self.version, channel=self.channel)

    class Meta:
        #TODO: see if this has a significant performance impact
        ordering = ('product', '-version', 'channel')


class Note(TimeStampedModel):
    TAGS = ('New', 'Changed', 'HTML5', 'Developer', 'Fixed')

    bug = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    releases = models.ManyToManyField(Release, blank=True)
    is_known_issue = models.BooleanField(default=False)
    fixed_in_release = models.ForeignKey(Release, null=True, blank=True,
                                         related_name='fixed_note_set')
    tag = models.CharField(max_length=255, blank=True,
                           choices=[(t, t) for t in TAGS])
    sort_num = models.IntegerField(null=True, blank=True)

    def is_known_issue_for(self, release):
        return self.is_known_issue and self.fixed_in_release != release

    class Meta:
        ordering = ('sort_num',)

    def __unicode__(self):
        return self.note
