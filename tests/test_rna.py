# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from mock import Mock, patch
from nose.tools import eq_, ok_

from rna import admin, fields, filters, models, views


@patch('rna.management.commands.rnasync.sync_data')
@override_settings(RNA_SYNC_URL='retrovirus')
class RnaSyncCommandTests(TestCase):
    def test_call_no_args(self, sync_data_mock):
        call_command('rnasync')
        sync_data_mock.assert_called_with(url='retrovirus', clean=False,
                                          last_modified=None, api_token=None)

    def test_call_with_args(self, sync_data_mock):
        call_command('rnasync', url='megavirus', clean=True)
        sync_data_mock.assert_called_with(url='megavirus', clean=True,
                                          last_modified=None, api_token=None)


class TimeStampedModelTest(TestCase):
    @patch('rna.models.models.Model.save')
    def test_default_modified(self, mock_super_save):
        start = datetime.now()
        model = models.TimeStampedModel()
        model.save(db='test')
        ok_(model.modified > start)
        mock_super_save.assert_called_once_with(db='test')

    @patch('rna.models.models.Model.save')
    def test_unmodified(self, mock_super_save):
        model = models.TimeStampedModel()
        model.modified = space_odyssey = datetime(2001, 1, 1)
        model.save(modified=False, db='test')
        eq_(model.modified, space_odyssey)
        mock_super_save.assert_called_once_with(db='test')


class NoteTest(TestCase):
    def test_unicode(self):
        """
        Should equal note
        """
        note = models.Note(note='test')
        eq_(unicode(note), 'test')

    def test_is_known_issue_for_not_known(self):
        """
        Should be False if is_known_issue is False.
        """
        note = models.Note(is_known_issue=False)
        release = Mock(spec=models.Release())
        eq_(note.is_known_issue_for(release), False)

    def test_is_known_issue_for_wrong_release(self):
        """
        Should be True if is_known_issue is True but fixed_in_release
        doesn't match given release.
        """
        fixed_release = Mock(spec=models.Release())
        release = Mock(spec=models.Release())
        note = models.Note(is_known_issue=True,
                           fixed_in_release=fixed_release)
        eq_(note.is_known_issue_for(release), True)

    def test_is_known_issue_for(self):
        """
        Should be False if is_known_issue is True and fixed_in_release
        matches the given release.
        """
        release = Mock(spec=models.Release())
        note = models.Note(is_known_issue=True,
                           fixed_in_release=release)
        eq_(note.is_known_issue_for(release), False)


class ReleaseTest(TestCase):
    def test_unicode(self):
        """
        Should equal name
        """
        release = models.Release(product='Firefox',
                                 channel='Release',
                                 version='12.0.1')
        eq_(unicode(release), 'Firefox 12.0.1 Release')

    def test_major_version(self):
        """
        Should return the version up to, but not including, the first dot
        """
        eq_(models.Release(version='42.0').major_version(), '42')

    def test_get_bug_search_url(self):
        """
        Should return self.bug_search_url
        """
        eq_(models.Release(
            bug_search_url='http://example.com').get_bug_search_url(),
            'http://example.com')

    def test_get_bug_search_url_default(self):
        """
        Should construct based on major version
        """
        eq_(models.Release(version='42.0').get_bug_search_url(),
            'https://bugzilla.mozilla.org/buglist.cgi?'
            'j_top=OR&f1=target_milestone&o3=equals&v3=Firefox%2042&'
            'o1=equals&resolution=FIXED&o2=anyexact&query_format=advanced&'
            'f3=target_milestone&f2=cf_status_firefox42&'
            'bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&'
            'v1=mozilla42&v2=fixed%2Cverified&limit=0')

    def test_get_bug_search_url_thunderbird(self):
        """
        Should construct based on major version
        """
        eq_(models.Release(version='42.0', product='Thunderbird').get_bug_search_url(),
            'https://bugzilla.mozilla.org/buglist.cgi?'
            'classification=Client%20Software&query_format=advanced&'
            'bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&'
            'target_milestone=Thunderbird%2042.0&product=Thunderbird'
            '&resolution=FIXED'
            )

    def test_notes(self):
        """
        Should split notes into new features and known issues.
        """
        new_feature_1 = Mock(**{'is_known_issue_for.return_value': False,
                                'tag': 'Changed'})
        new_feature_2 = Mock(**{'is_known_issue_for.return_value': False})
        dot_fix = Mock(**{'is_known_issue_for.return_value': False,
                          'tag': 'Fixed',
                          'note': '42.0.1 rendering glitches'})
        known_issue_1 = Mock(**{'is_known_issue_for.return_value': True})
        known_issue_2 = Mock(**{'is_known_issue_for.return_value': True})

        with patch.object(models.Release, 'note_set') as note_set:
            release = models.Release()
            note_set.order_by.return_value = [
                new_feature_2, new_feature_1, dot_fix, known_issue_1,
                known_issue_2]
            new_features, known_issues = release.notes()
            note_set.order_by.assert_called_with('-sort_num', 'created')

        eq_(new_features, [dot_fix, new_feature_2, new_feature_1])
        eq_(known_issues, [known_issue_1, known_issue_2])

    def test_notes_public_only(self):
        """
        Should filter notes based on is_public attr.
        """
        with patch.object(models.Release, 'note_set') as note_set:
            release = models.Release()
            release.notes(public_only=True)
            note_set.order_by.return_value.filter.assert_called_with(
                is_public=True)

    @override_settings(DEV=True)
    def test_equivalent_release_for_product_dev(self):
        """
        Should return the release for the specified product with
        the same channel and major version
        """
        release = models.Release(version='42.0', channel='Release')
        release._default_manager = Mock()
        mock_order_by = release._default_manager.filter.return_value.order_by
        mock_order_by.return_value = [
            models.Release(version='42.0'), models.Release(version='42.0.1')]
        eq_(release.equivalent_release_for_product('Firefox').version,
            '42.0.1')
        release._default_manager.filter.assert_called_once_with(
            version__startswith='42.', channel='Release', product='Firefox')
        mock_order_by.assert_called_once_with('-version')

    @override_settings(DEV=False)
    def test_equivalent_release_for_product_prod(self):
        """
        Should return the release for the specified product with
        the same channel and major version, with an additional filter
        is_public=True
        """
        release = models.Release(version='42.0', channel='Release')
        release._default_manager = Mock()
        mock_order_by = release._default_manager.filter.return_value.order_by
        mock_public_filter = Mock(
            return_value=[
                models.Release(version='42.0'), models.Release(version='42.0.1')])
        mock_order_by.return_value = Mock(filter=mock_public_filter)
        eq_(release.equivalent_release_for_product('Firefox').version,
            '42.0.1')
        release._default_manager.filter.assert_called_once_with(
            version__startswith='42.', channel='Release', product='Firefox')
        mock_public_filter.assert_called_once_with(is_public=True)

    @override_settings(DEV=False)
    def test_equivalent_release_for_product_33_1(self):
        """
        Should order by 2nd version # for 33.1 after applying other
        sorting criteria
        """
        release = models.Release(version='33.1', channel='Release')
        release._default_manager = Mock()
        mock_order_by = release._default_manager.filter.return_value.order_by
        mock_public_filter = Mock(
            return_value=[
                models.Release(version='33.0.3'), models.Release(version='33.1')])
        mock_order_by.return_value = Mock(filter=mock_public_filter)
        eq_(release.equivalent_release_for_product('Firefox').version,
            '33.1')
        release._default_manager.filter.assert_called_once_with(
            version__startswith='33.', channel='Release', product='Firefox')
        mock_public_filter.assert_called_once_with(is_public=True)

    def test_no_equivalent_release_for_product(self):
        """
        Should return None for empty querysets
        """
        release = models.Release(version='42.0', channel='Release')
        release._default_manager = Mock()
        release._default_manager.filter.return_value.order_by.return_value = \
            models.Release.objects.none()
        eq_(release.equivalent_release_for_product('Firefox'), None)

    def test_equivalent_android_release(self):
        """
        Should return the equivalent_release_for_product where the
        product is 'Firefox for Android'
        """
        release = models.Release(product='Firefox')
        release.equivalent_release_for_product = Mock()
        eq_(release.equivalent_android_release(),
            release.equivalent_release_for_product.return_value)
        release.equivalent_release_for_product.assert_called_once_with(
            'Firefox for Android')

    def test_equivalent_android_release_non_firefox_product(self):
        """
        Should not call equivalent_release_for_product if
        self.product does not equal 'Firefox'
        """
        release = models.Release(product='Firefox OS')
        release.equivalent_release_for_product = Mock()
        eq_(release.equivalent_android_release(), None)
        eq_(release.equivalent_release_for_product.called, 0)

    def test_equivalent_desktop_release(self):
        """
        Should return the equivalent_release_for_product where the
        product is 'Firefox'
        """
        release = models.Release(product='Firefox for Android')
        release.equivalent_release_for_product = Mock()
        eq_(release.equivalent_desktop_release(),
            release.equivalent_release_for_product.return_value)
        release.equivalent_release_for_product.assert_called_once_with(
            'Firefox')

    def test_equivalent_desktop_release_non_firefox_product(self):
        """
        Should not call equivalent_release_for_product if
        self.product does not equal 'Firefox for Android'
        """
        release = models.Release(product='Firefox OS')
        release.equivalent_release_for_product = Mock()
        eq_(release.equivalent_desktop_release(), None)
        eq_(release.equivalent_release_for_product.called, 0)


class ISO8601DateTimeFieldTest(TestCase):
    @patch('rna.fields.parse_datetime')
    def test_strptime(self, mock_parse_datetime):
        """
        Should equal expected_date returned by mock_parse_datetime
        """
        expected_date = datetime(2001, 1, 1)
        mock_parse_datetime.return_value = expected_date
        field = fields.ISO8601DateTimeField()
        eq_(field.strptime('value', 'format'), expected_date)


class TimeStampedModelSubclass(models.TimeStampedModel):
    test = models.models.BooleanField(default=True)

    class Meta:
        app_label = 'test_rna'


class TimestampedFilterBackendTest(TestCase):
    @patch('rna.filters.DjangoFilterBackend.get_filter_class',
           return_value='The Dude')
    def test_filter_class(self, mock_super_get_filter_class):
        """
        Should return super call if view has filter_class attr
        """
        mock_view = Mock(filter_class='abides')
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(mock_view), 'The Dude')

    @patch('rna.filters.DjangoFilterBackend.get_filter_class',
           return_value='The Dude')
    def test_filter_fields(self, mock_super_get_filter_class):
        """
        Should return super call if view has filter_fields attr
        """
        mock_view = Mock(filter_fields='abides')
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(mock_view), 'The Dude')

    @patch('rna.filters.DjangoFilterBackend.get_filter_class')
    def test_no_queryset(self, mock_super_get_filter_class):
        """
        Should return None if queryset is None (the default)
        """
        view = 'nice'
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(view), None)
        ok_(not mock_super_get_filter_class.called)

    @patch('rna.filters.DjangoFilterBackend.get_filter_class')
    def test_non_timestampedmodel(self, mock_super_get_filter_class):
        """
        Should return None if queryset.model is not a subclass of
        models.TimeStampedModel
        """
        view = 'nice'
        queryset = Mock(model=models.models.Model)  # model
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(view, queryset=queryset), None)
        ok_(not mock_super_get_filter_class.called)

    @patch('rna.filters.DjangoFilterBackend.get_filter_class')
    def test_default(self, mock_super_get_filter_class):
        """
        Should return a subclass of the default_filter_set instance
        attr with the inner Meta class model attr equal to the queryset
        model and fields equal to all of the model fields except
        created and modified, and in addition the created_before,
        created_after, modified_before, and modified_after fields
        """
        view = 'nice'
        queryset = Mock(model=TimeStampedModelSubclass)
        filter_backend = filters.TimestampedFilterBackend()
        filter_class = filter_backend.get_filter_class(view, queryset=queryset)
        eq_(filter_class.Meta.model, TimeStampedModelSubclass)
        eq_(filter_class.Meta.fields,
            ['created_before', 'created_after', 'modified_before',
             'modified_after', 'id', 'test'])
        ok_(not mock_super_get_filter_class.called)

    @patch('rna.filters.DjangoFilterBackend.get_filter_class')
    def test_exclude_fields(self, mock_super_get_filter_class):
        """
        Should not include fields named in the view.
        """
        mock_view = Mock(
            filter_class=None, filter_fields=None,
            filter_fields_exclude=('created_before', 'id'))
        queryset = Mock(model=TimeStampedModelSubclass)
        filter_backend = filters.TimestampedFilterBackend()
        filter_class = filter_backend.get_filter_class(
            mock_view, queryset=queryset)
        eq_(filter_class.Meta.model, TimeStampedModelSubclass)
        eq_(filter_class.Meta.fields,
            ['created_after', 'modified_before', 'modified_after', 'test'])
        eq_(mock_super_get_filter_class.called, 0)


class URLsTest(TestCase):
    @patch('rest_framework.routers.DefaultRouter.register')
    @patch('rest_framework.routers.DefaultRouter.urls')
    def test_urls(self, mock_urls, mock_register):
        from . import urls
        mock_register.assert_any_call('notes', views.NoteViewSet)
        mock_register.assert_any_call('releases', views.ReleaseViewSet)
        ok_(set(mock_urls).issubset(urls.urlpatterns))


class ReleaseAdminTest(TestCase):
    @patch('rna.admin.ReleaseAdmin.message_user')
    @patch('rna.admin.now')
    def test_copy_releases(self, mock_now, mock_message_user):
        mock_release_model = Mock()
        mock_release_model.objects.filter.return_value.count.return_value = 1
        release_admin = admin.ReleaseAdmin(mock_release_model, 'admin_site')
        mock_release = Mock(id=1, version='42.0', product='Firefox')
        mock_release.note_set.all.return_value = ['note']

        release_admin.copy_releases('request', [mock_release])

        mock_release_model.objects.filter.assert_called_once_with(
            version__endswith='42.0', product='Firefox')
        eq_(mock_release.id, None)
        eq_(mock_release.version, 'copy-42.0')
        mock_release.save.assert_called_once_with()
        mock_release.note_set.add.assert_called_once_with('note')
        mock_release.note_set.update.assert_called_once_with(
            modified=mock_now.return_value)
        mock_message_user.assert_called_once_with('request', 'Copied Release')

    @patch('rna.admin.ReleaseAdmin.message_user')
    @patch('rna.admin.now')
    def test_2nd_copy_releases(self, mock_now, mock_message_user):
        mock_release_model = Mock()
        mock_release_model.objects.filter.return_value.count.return_value = 2
        release_admin = admin.ReleaseAdmin(mock_release_model, 'admin_site')
        mock_release = Mock(id=1, version='42.0', product='Firefox')
        mock_release.note_set.all.return_value = ['note']

        release_admin.copy_releases('request', [mock_release])

        mock_release_model.objects.filter.assert_called_once_with(
            version__endswith='42.0', product='Firefox')
        eq_(mock_release.id, None)
        eq_(mock_release.version, 'copy2-42.0')
        mock_release.save.assert_called_once_with()
        mock_release.note_set.add.assert_called_once_with('note')
        mock_release.note_set.update.assert_called_once_with(
            modified=mock_now.return_value)
        mock_message_user.assert_called_once_with('request', 'Copied Release')
