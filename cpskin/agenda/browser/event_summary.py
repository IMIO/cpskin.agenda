# -*- coding: utf-8 -*-
from plone.app.event.browser.event_summary import EventSummaryView
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from cpskin.agenda.behaviors.related_contacts import IRelatedContacts


class EventContactSummaryView(EventSummaryView):

    def get_organizer(self):
        if not getattr(self.context, 'organizer', None):
            return None
        else:
            return self.context.organizer.to_object

    def get_contact(self):
        if not getattr(self.context, 'contact', None):
            return None
        else:
            return self.context.contact.to_object

    def get_location(self):
        if not getattr(self.context, 'location', None):
            return None
        else:
            return self.context.location.to_object

    def get_partners(self):
        if not getattr(self.context, 'partners', None):
            return None
        else:
            partners = [p.to_object for p in self.context.partners]
            return partners

    def enabled(self):
        """Check if behavior is enabled"""
        fti = queryUtility(IDexterityFTI, name='Event')
        behaviors = list(fti.behaviors)
        if IRelatedContacts.__identifier__ in behaviors:
            return True
        else:
            return False
