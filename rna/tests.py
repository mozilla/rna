# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from django.test import TestCase
from mock import Mock, patch
from nose.tools import eq_, ok_

from . import fields, filters, models, serializers, views


class AdminTest(TestCase):
    @patch('django.contrib.admin.site.register')
    def test_register(self, mock_register):
        import rna.rna.admin  # NOQA
        mock_register.assert_any_call(models.Channel)
        mock_register.assert_any_call(models.Product)
        mock_register.assert_any_call(models.Tag)
        mock_register.assert_any_call(models.Note)


class TimeStampedModelTest(TestCase):
    @patch('rna.rna.models.models.Model.save')
    def test_default_modified(self, mock_super_save):
        start = datetime.now()
        model = models.TimeStampedModel()
        model.save(db='test')
        ok_(model.modified > start)
        mock_super_save.assert_called_once_with(db='test')

    @patch('rna.rna.models.models.Model.save')
    def test_unmodified(self, mock_super_save):
        model = models.TimeStampedModel()
        model.modified = space_odyssey = datetime(2001, 1, 1)
        model.save(modified=False, db='test')
        eq_(model.modified, space_odyssey)
        mock_super_save.assert_called_once_with(db='test')


class ChannelTest(TestCase):
    def test_unicode(self):
        """
        Should equal name
        """
        channel = models.Channel(name='test')
        eq_(unicode(channel), 'test')


class ProductTest(TestCase):
    def test_unicode(self):
        """
        Should equal name
        """
        product = models.Product(name='test')
        eq_(unicode(product), 'test')


class NoteTest(TestCase):
    def test_unicode(self):
        """
        Should equal description
        """
        note = models.Note(html='test')
        eq_(unicode(note), 'test')


class TagTest(TestCase):
    def test_unicode(self):
        """
        Should equal text
        """
        tag = models.Tag(text='test')
        eq_(unicode(tag), 'test')


class ISO8601DateTimeFieldTest(TestCase):
    @patch('rna.rna.fields.parse_datetime')
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


class TimestampedFilterBackendTest(TestCase):
    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class',
           return_value='The Dude')
    def test_filter_class(self, mock_super_get_filter_class):
        """
        Should return super call if view has filter_class attr
        """
        mock_view = Mock(filter_class='abides')
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(mock_view), 'The Dude')

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class',
           return_value='The Dude')
    def test_filter_fields(self, mock_super_get_filter_class):
        """
        Should return super call if view has filter_fields attr
        """
        mock_view = Mock(filter_fields='abides')
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(mock_view), 'The Dude')

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_no_queryset(self, mock_super_get_filter_class):
        """
        Should return None if queryset is None (the default)
        """
        view = 'nice'
        filter_backend = filters.TimestampedFilterBackend()
        eq_(filter_backend.get_filter_class(view), None)
        ok_(not mock_super_get_filter_class.called)

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
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

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
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

    @patch('rna.rna.filters.DjangoFilterBackend.get_filter_class')
    def test_exclude_fields(self, mock_super_get_filter_class):
        """
        Should not include fields named in the view.
        """
        view = lambda: None
        view.filter_fields_exclude = ('created_before', 'id')
        queryset = Mock(model=TimeStampedModelSubclass)
        filter_backend = filters.TimestampedFilterBackend()
        filter_class = filter_backend.get_filter_class(view, queryset=queryset)
        eq_(filter_class.Meta.model, TimeStampedModelSubclass)
        eq_(filter_class.Meta.fields,
            ['created_after', 'modified_before', 'modified_after', 'test'])
        ok_(not mock_super_get_filter_class.called)


class GetClientSerializerClassTest(TestCase):
    def test_get_client_serializer_class(self):
        ClientSerializer = serializers.get_client_serializer_class(
            'mock_model_class')
        ok_(issubclass(ClientSerializer,
                       serializers.UnmodifiedTimestampSerializer))
        eq_(ClientSerializer.Meta.model, 'mock_model_class')


class HyperlinkedModelSerializerWithPkFieldTest(TestCase):
    @patch('rna.rna.serializers.HyperlinkedModelSerializerWithPkField'
           '.get_field', return_value='mock field')
    @patch('rna.rna.serializers.HyperlinkedModelSerializerWithPkField'
           '.__init__', return_value=None)
    def test_get_pk_field(self, mock_init, mock_get_field):
        serializer = serializers.HyperlinkedModelSerializerWithPkField()
        eq_(serializer.get_pk_field('model_field'), 'mock field')
        mock_get_field.assert_called_once_with('model_field')


class UnmodifiedTimestampSerializerTest(TestCase):
    @patch('rna.rna.serializers.serializers.ModelSerializer.restore_object',
           return_value=Mock(created='mock datetime str'))
    @patch('rna.rna.serializers.parse_datetime',
           return_value='mock parsed datetime')
    @patch('rna.rna.serializers.UnmodifiedTimestampSerializer.__init__',
           return_value=None)
    def test_restore_object(self, mock_init, mock_parse_datetime,
                            mock_super_restore_object):
        serializer = serializers.UnmodifiedTimestampSerializer()
        obj = serializer.restore_object('attrs')
        eq_(obj.created, 'mock parsed datetime')
        mock_super_restore_object.assert_called_once_with(
            'attrs', instance=None)
        mock_parse_datetime.assert_called_once_with('mock datetime str')

    @patch('rna.rna.serializers.serializers.ModelSerializer.save_object',
           return_value='abides')
    @patch('rna.rna.serializers.UnmodifiedTimestampSerializer.__init__',
           return_value=None)
    def test_save_object(self, mock_init, mock_super_save_object):
        serializer = serializers.UnmodifiedTimestampSerializer()
        the_dude = serializer.save_object('the dude', modified=True)
        eq_(the_dude, 'abides')
        mock_super_save_object.assert_called_once_with(
            'the dude', modified=False)


class URLsTest(TestCase):
    @patch('rest_framework.routers.DefaultRouter.register')
    @patch('rest_framework.routers.DefaultRouter.urls')
    def test_urls(self, mock_urls, mock_register):
        from . import urls
        mock_register.assert_any_call('channels', views.ChannelViewSet)
        mock_register.assert_any_call('notes', views.NoteViewSet)
        mock_register.assert_any_call('products', views.ProductViewSet)
        mock_register.assert_any_call('tags', views.TagViewSet)
        eq_(urls.urlpatterns, mock_urls)
