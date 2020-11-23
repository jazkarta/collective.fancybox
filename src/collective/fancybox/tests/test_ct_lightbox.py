# -*- coding: utf-8 -*-
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from collective.fancybox.content.lightbox import ILightbox  # NOQA E501
from collective.fancybox.testing import COLLECTIVE_FANCYBOX_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility
from zope.interface import Invalid
from zope.interface import providedBy

import unittest


class LightboxIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_FANCYBOX_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_lightbox_schema(self):
        fti = queryUtility(IDexterityFTI, name='Lightbox')
        schema = fti.lookupSchema()
        self.assertEqual(ILightbox, schema)

    def test_ct_lightbox_fti(self):
        fti = queryUtility(IDexterityFTI, name='Lightbox')
        self.assertTrue(fti)

    def test_ct_lightbox_factory(self):
        fti = queryUtility(IDexterityFTI, name='Lightbox')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ILightbox.providedBy(obj),
            u'ILightbox not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_lightbox_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
        )

        self.assertTrue(
            ILightbox.providedBy(obj),
            u'ILightbox not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('lightbox', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('lightbox', parent.objectIds())

    def test_ct_lightbox_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Lightbox')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_lightbox_catalog_index_metadata(self):
        self.assertTrue('lightbox_where' in self.portal.portal_catalog.indexes())
        self.assertTrue('lightbox_where' in self.portal.portal_catalog.schema())

    def test_ct_lightbox_defaults_indexed(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
        )

        result = self.portal.portal_catalog(path='/'.join(obj.getPhysicalPath()))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].lightbox_where, 'everywhere')
        self.assertEqual(result[0].lightbox_repeat, 'always')

    def test_ct_lightbox_global_marker(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
        )

        self.assertIn(ICollectiveFancyboxMarkerGlobal, providedBy(self.portal))

    def test_ct_lightbox_cannot_add_two_globals(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
        )

        try:
            api.content.create(
                container=self.portal,
                type='Lightbox',
                id='lightbox2',
            )
            self.fail()
        except Invalid:
            pass

    def test_ct_lightbox_global_empties_targets(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        obj = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
            lightbox_targets=['foo', ],
        )
        self.assertEqual([], obj.lightbox_targets)

    def test_ct_lightbox_nowhere_empties_targets(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        obj = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
            lightbox_where='nowhere',
            lightbox_targets=['foo', ],
        )
        self.assertEqual([], obj.lightbox_targets)

    def xtest_ct_lightbox_local_sets_markers(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
            lightbox_where='select',
            lightbox_targets=['foo', ],  # TODO how to set target?
        )

        query = {'object_provides': ICollectiveFancyboxMarker}
        result = api.content.find(**query)
        self.assertEqual(1, len(result))

    def test_ct_lightbox_clear_global_marker_on_delete(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        obj = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
        )

        api.content.delete(obj)
        self.assertNotIn(ICollectiveFancyboxMarkerGlobal, providedBy(self.portal))

    def test_ct_lightbox_clear_local_markers_on_delete(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        obj = api.content.create(
            container=self.portal,
            type='Lightbox',
            id='lightbox',
            lightbox_where='select',
        )

        api.content.delete(obj)
        query = {'object_provides': ICollectiveFancyboxMarker}
        result = api.content.find(**query)
        self.assertEqual(0, len(result))
