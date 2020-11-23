# -*- coding: utf-8 -*-
from collective.fancybox import _
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from plone import api
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import noLongerProvides
from zope.interface import providedBy

import logging


log = logging.getLogger(__name__)


def lightboxCreated(object, event):
    if object.lightbox_where == u'everywhere':
        clearTargets(object)
        setGlobalMarker()
    if object.lightbox_where == u'nowhere':
        clearTargets(object)
    if object.lightbox_where == u'select':
        setLocalMarkers(object.lightbox_targets)


def lightboxModified(object, event):
    if object.lightbox_where == u'everywhere':
        clearTargets(object)
        setGlobalMarker()
        clearLocalMarkers()
    if object.lightbox_where == u'nowhere':
        clearTargets(object)
        clearGlobalMarker(object)
        clearLocalMarkers()
        clearCookie(object)
    if object.lightbox_where == u'select':
        clearGlobalMarker(object)
        setLocalMarkers(object.lightbox_targets)
    if object.lightbox_repeat == u'always':
        clearCookie(object)


def lightboxRemoved(object, event):
    clearCookie(object)
    if object.lightbox_where == u'everywhere':
        clearGlobalMarker(object)
    if object.lightbox_where == u'select':
        clearLocalMarkers()  # maybe?


def clearTargets(data):
    """ This is used because the fields lightbox_where and lightbox_targets
        are independent, so it is possible that the targets field contains
        some values even though it should be empty based on lightbox_where.
    """
    data.lightbox_targets = []


def clearGlobalMarker(context):
    # is there an object with index lightbox_where == u'everywhere'?
    # is it different that the current context?
    # then leave it alone
    # otherwise, noLongerProvides(portal, MarkerGlobal)
    obj = None
    query = {'lightbox_where': 'everywhere'}
    for result in api.content.find(**query):
        try:
            if not obj:
                obj = result.getObject()
            else:
                log.error(
                    'There should be at most one global '
                    'lightbox: {0}.'.format(result.getPath())
                )
        except Exception:
            log.error(
                'Not possible to fetch object from catalog result for '
                'item: {0}.'.format(result.getPath())
            )
    if (obj is None) or (obj == context):
        noLongerProvides(api.portal.get(), ICollectiveFancyboxMarkerGlobal)


def clearLocalMarkers():
    # TODO
    pass


def setGlobalMarker():
    if ICollectiveFancyboxMarkerGlobal in providedBy(api.portal.get()):
        raise Invalid(_('Another lightbox already shows everywhere'))
    else:
        alsoProvides(api.portal.get(), ICollectiveFancyboxMarkerGlobal)


def setLocalMarkers(targets):
    # TODO
    pass


def clearCookie(context):
    # This is kinda pointless
    request = getRequest()
    id = 'collective.fancybox.{}'.format(context.id)
    request.response.expireCookie(id)
