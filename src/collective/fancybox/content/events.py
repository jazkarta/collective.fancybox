# -*- coding: utf-8 -*-
from collective.fancybox import _
from collective.fancybox.content.lightbox import canSetGlobalMarker
from collective.fancybox.content.lightbox import canSetLocalMarker
from collective.fancybox.content.lightbox import clearLocalMarker
from collective.fancybox.content.lightbox import getLocalLightboxesFor
from collective.fancybox.content.lightbox import setLocalMarker
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from plone import api
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import noLongerProvides

import logging


log = logging.getLogger(__name__)


def lightboxCreated(object, event):
    if object.lightbox_where == u'everywhere':
        clearTargets(object)
        setGlobalMarker(object)
    if object.lightbox_where == u'nowhere':
        clearTargets(object)
    if object.lightbox_where == u'select':
        setLocalMarkers(object, object.lightbox_targets)


def lightboxModified(object, event):
    targets = object.lightbox_targets
    if object.lightbox_where == u'everywhere':
        clearTargets(object)
        setGlobalMarker(object)
        clearLocalMarkers(targets)
    if object.lightbox_where == u'nowhere':
        clearTargets(object)
        clearGlobalMarker(object)
        clearLocalMarkers(targets)
        clearCookie(object)
    if object.lightbox_where == u'select':
        clearGlobalMarker(object)
        setLocalMarkers(object, targets)
    if object.lightbox_repeat == u'always':
        clearCookie(object)


def lightboxRemoved(object, event):
    targets = object.lightbox_targets
    clearCookie(object)
    if object.lightbox_where == u'everywhere':
        clearGlobalMarker(object)
    if object.lightbox_where == u'select':
        clearLocalMarkers(targets)


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
    if canSetGlobalMarker(context):
        noLongerProvides(api.portal.get(), ICollectiveFancyboxMarkerGlobal)


def clearLocalMarkers(targets):
    for target in targets or []:
        if hasattr(target, 'isBroken') and not target.isBroken():
            clearLocalMarker(target.to_object)


def setGlobalMarker(context):
    if canSetGlobalMarker(context):
        alsoProvides(api.portal.get(), ICollectiveFancyboxMarkerGlobal)
    else:
        raise Invalid(_('Another lightbox already shows everywhere'))


def setLocalMarkers(lightbox, targets):
    for target in targets:
        if not target.isBroken():
            obj = target.to_object
            if canSetLocalMarker(lightbox, obj):
                setLocalMarker(obj)
            else:
                msg = 'Another lightbox already points to {0}: {1}'
                slot = obj.absolute_url_path()
                slot1 = getLocalLightboxesFor(obj)[0].absolute_url_path()
                raise Invalid(msg.format(slot, slot1))


def clearCookie(context):
    # This is kinda pointless
    request = getRequest()
    id = 'collective.fancybox.{}'.format(context.id)
    request.response.expireCookie(id)
