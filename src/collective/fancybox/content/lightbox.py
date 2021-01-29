# -*- coding: utf-8 -*-
from collective.fancybox import _
from collective.fancybox.interfaces import ICollectiveFancyboxMarker
from collective.fancybox.interfaces import ICollectiveFancyboxMarkerGlobal
from plone import api
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.indexer.decorator import indexer
from plone.supermodel import model
from z3c.form.browser.radio import RadioFieldWidget
from z3c.relationfield.index import dump
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from z3c.relationfield import RelationValue
from zc.relation.interfaces import ICatalog
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import providedBy
from zope.intid.interfaces import IIntIds
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import logging


log = logging.getLogger(__name__)


class ILightbox(model.Schema):
    """ Marker interface and Dexterity Python Schema for Lightbox
    """
    directives.widget(lightbox_repeat=RadioFieldWidget)
    lightbox_repeat = schema.Choice(
        title=_(u'How often shall this lightbox be shown?'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(value=u'once', title=u'Once'),
            SimpleTerm(value=u'always', title=u'Always'),
        ]),
        required=False,
        default=u'always',
    )

    directives.widget(lightbox_where=RadioFieldWidget)
    lightbox_where = schema.Choice(
        title=_(u'Which pages will this lightbox be shown on?'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(value=u'nowhere', title=u'Nowhere (Disabled)'),
            SimpleTerm(value=u'everywhere', title=u'Everywhere'),
            SimpleTerm(value=u'select', title=u'On the pages selected below only'),
        ]),
        required=False,
        default=u'everywhere',
    )

    lightbox_targets = RelationList(
        title=u"Show the lightbox on these pages",
        default=[],
        value_type=RelationChoice(vocabulary='plone.app.vocabularies.Catalog'),
        required=False,
        missing_value=[],
    )
    directives.widget(
        "lightbox_targets",
        RelatedItemsFieldWidget,
        vocabulary='plone.app.vocabularies.Catalog',
    )

    lightbox_button_label = schema.TextLine(
        title=_(u'Button Label'),
        description=u'Label for the button displayed under the caption',
        default=u'',
        required=False,
    )

    lightbox_url = schema.URI(
        title=u"URL",
        description=u"Open this URL when the caption button is clicked",
        required=False,
    )

    @invariant
    def validate_lightbox(data):
        if data.lightbox_where == u'select':
            if not data.lightbox_targets:
                raise Invalid(_('You did not pick a page for your lightbox'))
        if data.lightbox_where == u'everywhere':
            old_where = getattr(data.__context__, 'lightbox_where', None)
            if old_where != data.lightbox_where:
                msg = 'Another lightbox already shows everywhere {0}'
                if hasGlobalMarker():
                    query = {'lightbox_where': 'everywhere'}
                    results = api.content.find(**query)
                    if len(results) > 0:
                        slot = results[0].getPath()
                    else:
                        slot = ''
                    raise Invalid(msg.format(slot))


@implementer(ILightbox)
class Lightbox(Item):
    """
    """


@indexer(ILightbox)
def lightbox_where(object, **kw):
    return object.lightbox_where


@indexer(ILightbox)
def lightbox_repeat(object, **kw):
    return object.lightbox_repeat


def clearLocalMarker(context):
    noLongerProvides(context, ICollectiveFancyboxMarker)


def hasGlobalMarker():
    return ICollectiveFancyboxMarkerGlobal in providedBy(api.portal.get())


def hasLocalMarker(context):
    return ICollectiveFancyboxMarker in providedBy(context)


def setLocalMarker(context):
    alsoProvides(context, ICollectiveFancyboxMarker)


def getRelationValue(context):
    intids = getUtility(IIntIds)
    return RelationValue(intids.getId(context))


def getLocalLightboxesFor(context):
    lightboxes = []
    cat = getUtility(ICatalog)
    int_id = dump(context, cat, {})

    if int_id:
        rels = cat.findRelations(dict(to_id=int_id))
        relations = [r for r in rels]
        for relation in (relations or []):
            if not relation.isBroken():
                obj = relation.from_object
                if hasattr(obj, 'portal_type'):
                    if obj and obj.portal_type == 'Lightbox':
                        lightboxes.append(obj)
    return lightboxes


def getGlobalLightbox():
    obj = None
    query = {'lightbox_where': 'everywhere'}
    for result in api.content.find(**query):
        if not obj:
            obj = result.getObject()
        else:
            raise Invalid(
                'There should be at most one global '
                'lightbox: {0}.'.format(result.getPath())
            )
    return obj


def canSetGlobalMarker(lightbox):
    obj = getGlobalLightbox()
    return (obj is None) or (obj == lightbox)


def canSetLocalMarker(lightbox, target):
    lightboxes = getLocalLightboxesFor(target)
    if len(lightboxes) == 0:
        return True
    elif len(lightboxes) == 1:
        lb = lightboxes[0]
        return (lb is None) or (lb == lightbox)
    else:
        return False
