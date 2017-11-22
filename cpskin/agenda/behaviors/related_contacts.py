# -*- coding: utf-8 -*-
from collective.contact.widget.schema import ContactChoice
from collective.contact.widget.schema import ContactList
from collective.contact.widget.source import ContactSourceBinder
from collective.geo.geographer.geo import GeoreferencingAnnotator
from collective.geo.geographer.interfaces import IGeoreferenceable
from cpskin.core.utils import add_behavior
from cpskin.core.utils import remove_behavior
from cpskin.locales import CPSkinMessageFactory as _
from persistent.dict import PersistentDict
from plone.app.contenttypes.interfaces import IEvent
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.relationfield.relation import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


KEY = 'collective.geo.geographer.georeference'


@provider(IFormFieldProvider)
class IRelatedContacts(model.Schema):

    form.order_before(location='IRichText.text')
    location = ContactChoice(
        title=_(u'Location'),
        source=ContactSourceBinder(
            portal_type=('organization',),
        ),
        required=False,
    )

    form.order_after(organizer='IRelatedContacts.location')
    organizer = ContactChoice(
        title=_(u'Organizer'),
        source=ContactSourceBinder(
            portal_type=('person', 'organization'),
        ),
        required=False,
    )

    form.order_after(contact='IRelatedContacts.organizer')
    contact = ContactChoice(
        title=_(u'Contact'),
        source=ContactSourceBinder(
            portal_type=('person', 'organization'),
        ),
        required=False,
    )

    form.order_after(partners='IRelatedContacts.contact')
    partners = ContactList(
        title=_(u'Partners'),
        value_type=ContactChoice(
            title=_(u'Partner'),
            source=ContactSourceBinder(
                portal_type=('person', 'organization'),
            )
        ),
        required=False,
    )


class LocationRelatedContactsGeoreferencingAnnotator(GeoreferencingAnnotator):

    def __init__(self, context):
        if isinstance(getattr(context, 'location', None), RelationValue):
            contact_obj = context.location.to_object
            context = contact_obj
        self.context = context
        annotations = IAnnotations(self.context)
        self.geo = annotations.get(KEY, None)
        if not self.geo:
            annotations[KEY] = PersistentDict()
            self.geo = annotations[KEY]
            self.geo['type'] = None
            self.geo['coordinates'] = None
            self.geo['crs'] = None


class ILocationRelatedContactsGeoreferenceable(IGeoreferenceable):
    pass


@implementer(IRelatedContacts)
@adapter(IEvent)
class RelatedContacts(object):

    def __init__(self, context):
        self.context = context

    @property
    def location(self):
        return getattr(self.context, 'location', None)

    @location.setter
    def location(self, value):
        self.context.location = value

    @property
    def organizer(self):
        return getattr(self.context, 'organizer', None)

    @organizer.setter
    def organizer(self, value):
        self.context.organizer = value

    @property
    def contact(self):
        return getattr(self.context, 'contact', None)

    @contact.setter
    def contact(self, value):
        self.context.contact = value

    @property
    def partners(self):
        return getattr(self.context, 'partners', None)

    @partners.setter
    def partners(self, value):
        self.context.partners = value


def modified_event(obj, event):
    type_name = obj.id
    if type_name == 'Event':
        pae_behaviors = [
            'plone.app.event.dx.behaviors.IEventAttendees',
            'plone.app.event.dx.behaviors.IEventLocation',
            'plone.app.event.dx.behaviors.IEventContact'
        ]
        if 'cpskin.agenda.behaviors.related_contacts.IRelatedContacts' in obj.behaviors:  # noqa
            for pae_behavior in pae_behaviors:
                remove_behavior(type_name, pae_behavior)
        else:
            for pae_behavior in pae_behaviors:
                add_behavior(type_name, pae_behavior)
