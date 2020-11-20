# -*- coding: utf-8 -*-
from collective.fancybox.content.lightbox import ILightbox  # NOQA E501
from collective.fancybox.testing import COLLECTIVE_FANCYBOX_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

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
