# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveFancyboxLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ICollectiveFancyboxMarker(Interface):
    """Interface that marks an item that has a lightbox."""


class ICollectiveFancyboxMarkerGlobal(Interface):
    """There is a lightbox enabled on the whole site."""
