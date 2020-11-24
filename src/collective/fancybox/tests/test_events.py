# -*- coding: utf-8 -*-
from collective.fancybox.content.events import lightboxModified
from collective.fancybox.content.lightbox import getRelationValue
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from collective.fancybox.testing import \
    COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING  # noqa: E501
from collective.fancybox.testing import MockLightbox
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import providedBy

import transaction
import unittest


VIEWLET = "$.fancybox.open($('.lightbox [data-fancybox]'));"


class TestEventHandlers(unittest.TestCase):
    """ When no Lightboxes exist in the site. """

    layer = COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING

    def setUp(self):
        """ Custom shared utility setup for tests. """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        self.wf = self.portal.portal_workflow

    def test_modified_everywhere_clears_targets(self):
        """ on modified leaves targets empty if lightbox_where is everywhere.
        """
        data = MockLightbox()
        data.lightbox_where = 'everywhere'
        data.lightbox_targets = 'hello'

        lightboxModified(data, None)

        self.assertEqual(data.lightbox_targets, [])

    def test_modified_everywhere_sets_global_marker(self):
        """ on modified set global marker if lightbox_where is everywhere.
        """
        data = MockLightbox()
        data.lightbox_where = 'everywhere'

        lightboxModified(data, None)

        self.assertIn(ICollectiveFancyboxMarkerGlobal, providedBy(self.portal))

    def test_modified_everywhere_clears_local_markers(self):
        """ on modified clears local markers if lightbox_where is everywhere.
        """
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        target = api.content.create(
            container=self.portal,
            type='Document',
            id='page1',
            title='Page1',
        )
        rel = getRelationValue(target)

        data = MockLightbox()
        data.lightbox_where = 'everywhere'
        data.lightbox_targets = [rel, ]

        lightboxModified(data, None)

        self.assertNotIn(ICollectiveFancyboxMarker, providedBy(target))

    def test_modified_nowhere_clears_targets(self):
        """ on modified leaves targets empty if lightbox_where is nowhere.
        """
        data = MockLightbox()
        data.lightbox_where = 'nowhere'
        data.lightbox_targets = 'hello'

        lightboxModified(data, None)

        self.assertEqual(data.lightbox_targets, [])

    def test_modified_nowhere_clears_global_marker(self):
        """ on modified clears global marker if lightbox_where is nowhere.
        """
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        data = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
            lightbox_where='everywhere',
        )
        data.lightbox_where = 'nowhere'
        data.reindexObject()

        lightboxModified(data, None)

        self.assertNotIn(ICollectiveFancyboxMarkerGlobal, providedBy(self.portal))

    def test_modified_nowhere_multiple_global_error(self):
        """ on modified raises error when multiple global lightboxes exist.
        """
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        api.content.create(
            container=self.portal,
            type='Document',
            id='page1',
            title='Page1',
        )
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        self.portal.invokeFactory(
            "Lightbox",
            id="lightbox2",
            title="Lightbox 2",
            lightbox_where='nowhere',
        )
        self.portal.lightbox2.lightbox_where = 'everywhere'
        self.portal.lightbox2.reindexObject()
        transaction.commit()
        self.portal.lightbox2.lightbox_where = 'nowhere'
        try:
            lightboxModified(self.portal.lightbox2, None)
            self.fail()
        except Invalid:
            pass

    def test_modified_nowhere_clears_local_markers(self):
        """ on modified clears local markers if lightbox_where is nowhere.
        """
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        target = api.content.create(
            container=self.portal,
            type='Document',
            id='page1',
            title='Page1',
        )
        rel = getRelationValue(target)

        data = MockLightbox()
        data.lightbox_where = 'nowhere'
        data.lightbox_targets = [rel, ]

        lightboxModified(data, None)

        self.assertNotIn(ICollectiveFancyboxMarker, providedBy(target))

    def test_modified_select_clears_global_marker(self):
        """ on modified clears global marker if lightbox_where is select.
        """
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        data = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
            lightbox_where='everywhere',
        )
        data.lightbox_where = 'select'
        data.reindexObject()

        lightboxModified(data, None)

        self.assertNotIn(ICollectiveFancyboxMarkerGlobal, providedBy(self.portal))

    def test_modified_select_sets_local_markers(self):
        """ on modified sets local markers if lightbox_where is select.
        """
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        target = api.content.create(
            container=self.portal,
            type='Document',
            id='page1',
            title='Page1',
        )
        rel = getRelationValue(target)

        data = MockLightbox()
        data.lightbox_where = 'select'
        data.lightbox_targets = [rel, ]

        lightboxModified(data, None)

        self.assertIn(ICollectiveFancyboxMarker, providedBy(target))

    def test_modified_select_error(self):
        """ on modified raises error if local marker already exists
        """
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        target = api.content.create(
            container=self.portal,
            type='Document',
            id='page1',
            title='Page1',
        )
        rel = getRelationValue(target)

        alsoProvides(target, ICollectiveFancyboxMarker)

        data = MockLightbox()
        data.lightbox_where = 'select'
        data.lightbox_targets = [rel, ]

        try:
            lightboxModified(data, None)
            self.fail()
        except Invalid:
            pass

    def test_modified_always_clears_cookie(self):
        """ on modified clears the cookie if lightbox_repeat is always.
        """
        data = MockLightbox()
        data.id = 'foo'
        data.lightbox_where = 'everywhere'
        data.lightbox_repeat = 'always'

        lightboxModified(data, None)

        cookies = self.request.response.cookies
        expected = {
            'collective.fancybox.foo': {
                'max_age': 0,
                'expires': 'Wed, 31 Dec 1997 23:59:59 GMT',
                'value': 'deleted',
                'quoted': True
            }
        }
        self.assertEqual(cookies, expected)
