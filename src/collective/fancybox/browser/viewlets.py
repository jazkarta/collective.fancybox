# -*- coding: utf-8 -*-
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from plone.app.layout.viewlets.common import ViewletBase
from zope.interface import providedBy


class hasLightbox(object):
    """ Used by the viewlet and by the bundle expression property. """

    def __call__(self):
        enabled = ICollectiveFancyboxMarker in providedBy(self.context)
        return enabled


class LightboxViewlet(ViewletBase):

    def update(self):
        super(LightboxViewlet, self).update()
        self.enabled = self.context.unrestrictedTraverse('@@hasLightbox')()
