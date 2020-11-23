# -*- coding: utf-8 -*-
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

import transaction
import unittest


VIEWLET = "$.fancybox.open($('.lightbox [data-fancybox]'));"


class TestViewletBase(unittest.TestCase):
    """ When no Lightboxes exist in the site. """

    layer = COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        self.wf = self.portal.portal_workflow
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Document", id="page1", title="Page 1")
        self.portal.invokeFactory("Document", id="page2", title="Page 2")

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
        super(TestViewletNoLightboxes, self).setUp()
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
        super(TestViewletLocalLightbox, self).setUp()
        self.portal.invokeFactory(
            "Lightbox",
            id="lightbox1",
            title="Lightbox 1",
            lightbox_where='select'
        )
        self.wf.doActionFor(self.portal.lightbox1, 'publish')
        transaction.commit()

    def xtest_is_present_with_marker(self):
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
        super(TestViewletGlobalLightbox, self).setUp()
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        self.portal.invokeFactory(
            "Lightbox",
            id="lightbox2",
            title="Lightbox 2",
            lightbox_where='select'
        )
        self.wf.doActionFor(self.portal.lightbox1, 'publish')
        self.wf.doActionFor(self.portal.lightbox2, 'publish')
        transaction.commit()

    def test_is_present_with_global_marker(self):
        """ Any page should have the viewlet. """
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)

    def xtest_is_present_with_local_marker(self):
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
        super(TestViewletCookie, self).setUp()
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        self.wf.doActionFor(self.portal.lightbox1, 'publish')
        transaction.commit()

    def test_is_not_present_after_first(self):
        """ The global 'once' lightbox is set to show only once. """
        self.portal.lightbox1.lightbox_repeat = 'once'
        transaction.commit()
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)
        browser.open(page1.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)

    def test_is_present_every_time(self):
        """ The 'always' lightbox should show every time. """
        self.portal.lightbox1.lightbox_repeat = 'always'
        transaction.commit()
        page1 = self.portal.page1
        browser = self.get_browser()
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)
        browser.open(page1.absolute_url())
        self.assertIn(VIEWLET, browser.contents)


class TestViewletPrivateLightbox(TestViewletBase):
    """ When there is a lightbox in private state. """

    def setUp(self):
        """ One page with local lightbox in private state. """
        super(TestViewletPrivateLightbox, self).setUp()
        alsoProvides(self.portal.page1, ICollectiveFancyboxMarker)
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
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
        super(TestViewletDates, self).setUp()
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")
        self.portal.invokeFactory(
            "Lightbox",
            id="lightbox2",
            title="Lightbox 2",
            lightbox_where='select'
        )
        transaction.commit()
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
        self.portal.lightbox1.lightbox_where = 'seleect'
        self.portal.lightbox2.lightbox_where = 'everywhere'
        transaction.commit()
        page2 = self.portal.page2
        browser = self.get_browser()
        browser.open(page2.absolute_url())
        self.assertNotIn(VIEWLET, browser.contents)
