# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.fancybox.testing import \
    COLLECTIVE_FANCYBOX_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.fancybox is properly installed."""

    layer = COLLECTIVE_FANCYBOX_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        if get_installer:
            self.installer = get_installer(self.portal, self.request)
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        self.registry = getUtility(IRegistry)

    def test_product_installed(self):
        """Test if collective.fancybox is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.fancybox'))

    def test_browserlayer(self):
        """Test that ICollectiveFancyboxLayer is registered."""
        from collective.fancybox.interfaces import (
            ICollectiveFancyboxLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveFancyboxLayer,
            utils.registered_layers())

    def test_resources(self):
        # Test availability of bundles and resources
        self.assertEqual(
            self.registry.records.get(
                'plone.bundles/fancybox.resources'
            ).value,
            ['fancybox'],
        )

        self.assertEqual(
            self.registry.records.get(
                'plone.bundles/fancybox.expression'
            ).value,
            None,
        )

        self.assertEqual(
            self.registry.records.get('plone.resources/fancybox.css').value,
            ['++plone++collective.fancybox/jquery.fancybox.min.css',]
        )

        self.assertEqual(
            self.registry.records.get('plone.resources/fancybox.js').value,
            '++plone++collective.fancybox/jquery.fancybox.min.js',
        )


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_FANCYBOX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['collective.fancybox'])
        setRoles(self.portal, TEST_USER_ID, roles_before)
        self.registry = getUtility(IRegistry)

    def test_product_uninstalled(self):
        """Test if collective.fancybox is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.fancybox'))

        # These are removed
        self.assertEqual(
            self.registry.records.get('plone.resources/fancybox.js'), None
        )
        self.assertEqual(
            self.registry.records.get('plone.resources/fancybox.css'), None
        )
        self.assertEqual(
            self.registry.records.get('plone.bundles/fancybox'), None
        )
        self.assertEqual(
            self.registry.records.get('plone.bundles/fancybox.resources'), None
        )

    def test_browserlayer_removed(self):
        """Test that ICollectiveFancyboxLayer is removed."""
        from collective.fancybox.interfaces import \
            ICollectiveFancyboxLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectiveFancyboxLayer,
            utils.registered_layers())

