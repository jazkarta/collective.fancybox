# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from collective.fancybox.testing import \
    COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING  # noqa: E501
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import transaction
import unittest


VIEWLET = "$.fancybox.open($('.lightbox [data-fancybox]'));"


class TestViewlet(unittest.TestCase):
    """Test that the viewlet is rendered."""

    layer = COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING

    def get_browser(self):
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        return browser

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        alsoProvides(self.portal.page1, ICollectiveFancyboxMarker)
        transaction.commit()

    def test_is_present_with_marker(self):
        """Test if the viewlet is present when the object has marker interface."""
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)

    def test_is_not_present_without_marker(self):
        """Test if the viewlet is present when the object has marker interface."""
        page1 = self.portal.page1
        noLongerProvides(page1, ICollectiveFancyboxMarker)
        transaction.commit()

        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)
