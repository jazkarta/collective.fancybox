# -*- coding: utf-8 -*-
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from zope.interface import noLongerProvides


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'collective.fancybox:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
    noLongerProvides(api.portal.get(), ICollectiveFancyboxMarkerGlobal)
    query = {'object_provides': ICollectiveFancyboxMarker}
    for result in api.content.find(**query):
        obj = result.getObject()
        noLongerProvides(obj, ICollectiveFancyboxMarker)
