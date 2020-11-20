# -*- coding: utf-8 -*-
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from z3c.relationfield.index import dump
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.interface import providedBy

import logging


log = logging.getLogger(__name__)


class hasLightbox(object):
    """ Used by the viewlet and by the bundle expression property. """

    def __call__(self):
        self.target = None
        self.portal = api.portal.get()
        enabled = self._hasLocalMarker()
        enabled = enabled or self._hasGlobalMarker()

        if not enabled:
            return False

        self.lightbox = self._findLightbox()
        if not self.lightbox:  # TODO remove this block
            class LB():
                id = 'foobar'
                expires = self.target.expires

            self.lightbox = LB()
            pass
            # return True  # TODO will be False once we have tests

        if not self._showFirstTimeOrReturning():
            return False

        enabled = self._isPublished() and self._isEffective()

        return enabled

    def _hasLocalMarker(self):
        """Does context have the marker?"""
        if ICollectiveFancyboxMarker in providedBy(self.context):
            self.target = self.context
        return bool(self.target)

    def _hasGlobalMarker(self):
        """Does portal have the global marker?"""
        if ICollectiveFancyboxMarkerGlobal in providedBy(self.portal):
            self.target = self.portal
        return bool(self.target)

    def _findGlobalLightbox(self):
        """ query the catalog for lightbox_where == 'everywhere'
            because the portal does not have an int_id
        """
        obj = None
        query = {'lightbox_where': 'everywhere'}
        for result in api.content.find(**query):
            try:
                obj = result.getObject()
            except Exception:
                log.error(
                    'Not possible to fetch object from catalog result for '
                    'item: {0}.'.format(result.getPath()))
            # there should only be one
            return obj
        log.warning('We have ICollectiveFancyboxMarkerGlobal but no lightbox')
        return None

    def _findLocalLightbox(self):
        """ Look for relations of type Lightbox that point here."""
        cat = getUtility(ICatalog)
        int_id = dump(self.context, cat, {})

        if int_id:
            rels = cat.findRelations(dict(to_id=int_id))
            relations = [r for r in rels]
            for relation in (relations or []):
                if not relation.isBroken():
                    obj = relation.from_object
                    if hasattr(obj, 'portal_type'):
                        if obj and obj.portal_type == 'Lightbox':
                            return obj
        log.warning('We have ICollectiveFancyboxMarker but no lightbox')
        return None

    def XX_findLightbox(self):
        """ Find the lightbox object that points to self.target. """
        if self.context == self.portal:
            return self._findGlobalLightbox()
        else:
            return self._findLocalLightbox()

    def _findLightbox(self):
        """ TODO remove this. """
        return self.target.lightbox

    def _hasCookie(self):
        pass

    def _isPublished(self):
        return api.content.get_state(self.lightbox) == 'published'

    def _isEffective(self):
        lb = self.lightbox
        return lb.effective().isPast() and lb.expires().isFuture()

    def _showFirstTimeOrReturning(self):
        """ If there is a cookie, visitor has already seen the lightbox.
            We assume first time visitor if there is no cookie.
            In the latter case, set the cookie.
            *Note to self*: this is called at least twice for each page load,
            1. from the bundle expression='context/@@hasLightbox'
            2. from the viewlet.
        """
        id = 'collective.fancybox.{}'.format(self.lightbox.id)
        cookie = self.request.cookies.get(id)
        if cookie:
            return (self.lightbox.lightbox_repeat == 'always')

        else:
            self.request.response.setCookie(
                id,
                "I Was Here",
                expires=self.lightbox.expires().ISO()
            )
            return True


class LightboxViewlet(ViewletBase):

    def update(self):
        super(LightboxViewlet, self).update()
        self.enabled = self.context.unrestrictedTraverse('@@hasLightbox')()
