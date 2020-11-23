# -*- coding: utf-8 -*-
from collective.fancybox.content.lightbox import ILightbox
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from collective.fancybox.testing import \
    COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING  # noqa: E501
from collective.fancybox.testing import MockLightbox
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.interface import alsoProvides
from zope.interface import Invalid

import unittest


class TestInvariant(unittest.TestCase):
    """ The the Lightbox content type invariant. """

    layer = COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING

    def setUp(self):
        """ Custom shared utility setup for tests. """
        self.portal = self.layer['portal']

    def test_targets_not_empty(self):
        """ When lightbox_where=='select' at least one target must be selected.
        """
        data = MockLightbox()
        data.lightbox_where = 'select'
        data.lightbox_targets = 'hello'

        try:
            ILightbox.validateInvariants(data)
        except Invalid:
            self.fail()

    def test_targets_empty(self):
        data = MockLightbox()
        data.lightbox_where = 'select'

        try:
            ILightbox.validateInvariants(data)
            self.fail()
        except Invalid:
            pass

    def test_global_marker_exists_where_unchanged(self):
        data = MockLightbox()
        data.lightbox_where = 'everywhere'
        setattr(data.__context__, 'lightbox_where', 'everywhere')
        alsoProvides(self.portal, ICollectiveFancyboxMarkerGlobal)

        try:
            ILightbox.validateInvariants(data)
        except Invalid:
            self.fail()

    def test_global_marker_exists_where_changed(self):
        data = MockLightbox()
        data.lightbox_where = 'everywhere'
        setattr(data.__context__, 'lightbox_where', 'local')
        alsoProvides(self.portal, ICollectiveFancyboxMarkerGlobal)

        try:
            ILightbox.validateInvariants(data)
            self.fail()
        except Invalid:
            pass

    def test_other_global_lightbox_exists_where_changed(self):
        data = MockLightbox()
        data.lightbox_where = 'everywhere'
        setattr(data.__context__, 'lightbox_where', 'local')

        # How do we populate a catalog index for the test?
        setRoles(self.portal, TEST_USER_ID, ["Manager", "Member"])
        self.portal.invokeFactory("Lightbox", id="lightbox1", title="Lightbox 1")

        try:
            ILightbox.validateInvariants(data)
            self.fail()
        except Invalid:
            pass
