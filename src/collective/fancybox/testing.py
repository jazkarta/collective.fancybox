# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import collective.fancybox


class MockContext(object):
    lightbox_where = None


class MockLightbox(object):
    id = None
    lightbox_targets = None
    lightbox_repeat = None
    __context__ = MockContext()


class CollectiveFancyboxLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.fancybox)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.fancybox:default')


COLLECTIVE_FANCYBOX_FIXTURE = CollectiveFancyboxLayer()


COLLECTIVE_FANCYBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_FANCYBOX_FIXTURE,),
    name='CollectiveFancyboxLayer:IntegrationTesting',
)


COLLECTIVE_FANCYBOX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FANCYBOX_FIXTURE,),
    name='CollectiveFancyboxLayer:FunctionalTesting',
)


COLLECTIVE_FANCYBOX_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_FANCYBOX_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveFancyboxLayer:AcceptanceTesting',
)
