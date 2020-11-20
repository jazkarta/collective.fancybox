# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
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

import transaction
import unittest


VIEWLET = "$.fancybox.open($('.lightbox [data-fancybox]'));"


class TestViewletBase(unittest.TestCase):
    """ When no Lightboxes exist in the site. """

    layer = COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING

    def get_browser(self):
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        return browser


class TestViewletNoLightboxes(TestViewletBase):
    """ When no Lightboxes exist in the site. """

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        transaction.commit()

    def test_is_not_present_without_marker(self):
        """ There is no viewlet. """
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)


class TestViewletLocalLightbox(TestViewletBase):
    """ When there is a local lightbox. """

    def setUp(self):
        """ One page with local lightbox and one without. """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        self.portal.invokeFactory("Document", id="page2", title="Page 2")
        alsoProvides(self.portal.page1, ICollectiveFancyboxMarker)
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        transaction.commit()
        setattr(self.portal.page1, 'lightbox', self.portal.lightbox1)
        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.portal.lightbox1, 'publish')
        transaction.commit()

    def test_is_present_with_marker(self):
        """ Test if the viewlet is present when the object has marker interface. """
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)

    def test_is_not_present_without_marker(self):
        """ There is no viewlet. """
        page2 = self.portal.page2
        browser = self.get_browser()
        browser.open(page2.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)


class TestViewletGlobalLightbox(TestViewletBase):
    """ When there is a global lightbox. """

    def setUp(self):
        """ One page with global lightbox and one with local lightbox. """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        self.portal.invokeFactory("Document", id="page2", title="Page 2")
        alsoProvides(self.portal, ICollectiveFancyboxMarkerGlobal)
        alsoProvides(self.portal.page2, ICollectiveFancyboxMarker)
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        self.portal.invokeFactory("Lightbox", id="lightbox2", title="Lightbox 2")
        transaction.commit()
        setattr(self.portal, 'lightbox', self.portal.lightbox1)
        setattr(self.portal.page2, 'lightbox', self.portal.lightbox2)
        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.portal.lightbox1, 'publish')
        workflow.doActionFor(self.portal.lightbox2, 'publish')
        transaction.commit()

    def test_is_present_with_global_marker(self):
        """ Any page should have the viewlet. """
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)

    def test_is_present_with_local_marker(self):
        """ A page with the local marker should have the local lightbox. """
        page2 = self.portal.page2
        browser = self.get_browser()
        browser.open(page2.absolute_url())
        # TODO distinguish between local and global viewlet
        self.assertIn(VIEWLET, browser.contents)


class TestViewletCookie(TestViewletBase):
    """ A cookie and the lightbox_repeat setting determine whether the
        lightbox gets shown only once or every time.
    """

    def setUp(self):
        """One page with global lightbox and one with local lightbox.
           The global lightbox is shown only once.
           The local one is shown every time.
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        self.portal.invokeFactory("Document", id="page2", title="Page 2")
        alsoProvides(self.portal, ICollectiveFancyboxMarkerGlobal)
        alsoProvides(self.portal.page2, ICollectiveFancyboxMarker)
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        self.portal.invokeFactory("Lightbox", id="lightbox2", title="Lightbox 2")
        transaction.commit()
        setattr(self.portal, 'lightbox', self.portal.lightbox1)
        setattr(self.portal.page2, 'lightbox', self.portal.lightbox2)
        self.portal.lightbox1.lightbox_repeat = 'once'
        self.portal.lightbox2.lightbox_repeat = 'always'
        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.portal.lightbox1, 'publish')
        workflow.doActionFor(self.portal.lightbox2, 'publish')
        transaction.commit()

    def test_is_not_present_globally_after_first(self):
        """ The global lightbox is set to show only once. """
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)
        browser.open(page1.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)

    def test_is_present_every_time(self):
        """ The local lightbox should show every time. """
        page2 = self.portal.page2
        browser = self.get_browser()
        browser.open(page2.absolute_url())
        # TODO distinguish between local and global viewlet
        self.assertIn(VIEWLET, browser.contents)
        browser.open(page2.absolute_url())
        self.assertIn(VIEWLET, browser.contents)


class TestViewletPrivateLightbox(TestViewletBase):
    """ When there is a lightbox in private state. """

    def setUp(self):
        """ One page with local lightbox in private state. """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        alsoProvides(self.portal.page1, ICollectiveFancyboxMarker)
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        transaction.commit()
        setattr(self.portal.page1, 'lightbox', self.portal.lightbox1)
        transaction.commit()

    def test_is_not_present_when_private(self):
        """ The viewlet is not present when the lightbox is private. """
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)


class TestViewletDates(TestViewletBase):
    """ When the lightbox is before effective or after expiration. """

    def setUp(self):
        """ Two pages with one lightbox each,
            one not yet effective,
            the other already expired.
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        self.portal.invokeFactory("Document", id="page2", title="Page 2")
        alsoProvides(self.portal.page1, ICollectiveFancyboxMarker)
        alsoProvides(self.portal.page2, ICollectiveFancyboxMarker)
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        self.portal.invokeFactory("Lightbox", id="lightbox2", title="Lightbox 2")
        transaction.commit()
        setattr(self.portal.page1, 'lightbox', self.portal.lightbox1)
        setattr(self.portal.page2, 'lightbox', self.portal.lightbox2)
        self.portal.lightbox1.content_status_modify(workflow_action='publish',
                                                    effective_date='1/1/2031',
                                                    expiration_date='1/2/2031')
        self.portal.lightbox2.content_status_modify(workflow_action='publish',
                                                    effective_date='1/1/2010',
                                                    expiration_date='1/2/2011')
        transaction.commit()

    def test_is_not_present_when_not_effective(self):
        """ The viewlet is not present when effective date is in the future. """
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)

    def test_is_not_present_when_expired(self):
        """ The viewlet is not present when expired. """
        page2 = self.portal.page2
        browser = self.get_browser()
        browser.open(page2.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)
