# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from ietf.name.models import *
from ietf.person.models import Email, Person

import datetime

class GroupInfo(models.Model):
    time = models.DateTimeField(default=datetime.datetime.now)
    name = models.CharField(max_length=80)
    state = models.ForeignKey(GroupStateName, null=True)
    type = models.ForeignKey(GroupTypeName, null=True)
    parent = models.ForeignKey('Group', blank=True, null=True)
    ad = models.ForeignKey(Person, verbose_name="AD", blank=True, null=True)
    list_email = models.CharField(max_length=64, blank=True)
    list_subscribe = models.CharField(max_length=255, blank=True)
    list_archive = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

    unused_states = models.ManyToManyField('doc.State', help_text="Document states that have been disabled for the group", blank=True)
    unused_tags = models.ManyToManyField(DocTagName, help_text="Document tags that have been disabled for the group", blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class GroupManager(models.Manager):
    def active_wgs(self):
        return self.get_query_set().filter(type='wg', state__in=('bof','proposed','active'))

class Group(GroupInfo):
    objects = GroupManager()

    acronym = models.SlugField(max_length=40, unique=True, db_index=True)
    charter = models.OneToOneField('doc.Document', related_name='chartered_group', blank=True, null=True)
    
    def latest_event(self, *args, **filter_args):
        """Get latest event of optional Python type and with filter
        arguments, e.g. g.latest_event(type="xyz") returns a GroupEvent
        while g.latest_event(ChangeStateGroupEvent, type="xyz") returns a
        ChangeStateGroupEvent event."""
        model = args[0] if args else GroupEvent
        e = model.objects.filter(group=self).filter(**filter_args).order_by('-time', '-id')[:1]
        return e[0] if e else None

class GroupHistory(GroupInfo):
    group = models.ForeignKey(Group, related_name='history_set')
    acronym = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural="group histories"

class GroupURL(models.Model):
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=255)
    url = models.URLField(verify_exists=False)
    def __unicode__(self):
	return u"%s (%s)" % (self.url, self.name)

class GroupMilestoneInfo(models.Model):
    group = models.ForeignKey(Group)
    # a group has two sets of milestones, current milestones
    # (active/under review/deleted) and charter milestones (active
    # during a charter/recharter event), events for charter milestones
    # are stored on the charter document
    state = models.ForeignKey(GroupMilestoneStateName)
    desc = models.CharField(verbose_name="Description", max_length=500)
    due = models.DateField()
    resolved = models.CharField(max_length=50, blank=True, help_text="Explanation of why milestone is resolved (usually \"Done\"), or empty if still due")
    time = models.DateTimeField(auto_now=True)

    docs = models.ManyToManyField('doc.Document', blank=True)

    def __unicode__(self):
	return self.desc[:20] + "..."
    class Meta:
        abstract = True
	ordering = ['due', 'id']

class GroupMilestone(GroupMilestoneInfo):
    pass

class GroupMilestoneHistory(GroupMilestoneInfo):
    milestone = models.ForeignKey(GroupMilestone, related_name="history_set")

class GroupStateTransitions(models.Model):
    """Captures that a group has overriden the default available
    document state transitions for a certain state."""
    group = models.ForeignKey(Group)
    state = models.ForeignKey('doc.State', help_text="State for which the next states should be overridden")
    next_states = models.ManyToManyField('doc.State', related_name='previous_groupstatetransitions_states')

    def __unicode__(self):
	return u'%s "%s" -> %s' % (self.group.acronym, self.state.name, [s.name for s in self.next_states.all()])

GROUP_EVENT_CHOICES = [
    ("changed_state", "Changed state"),
    ("added_comment", "Added comment"),
    ("info_changed", "Changed metadata"),
    ("requested_close", "Requested closing group"),
    ("changed_milestone", "Changed milestone"),
    ]

class GroupEvent(models.Model):
    """An occurrence for a group, used for tracking who, when and what."""
    group = models.ForeignKey(Group)
    time = models.DateTimeField(default=datetime.datetime.now, help_text="When the event happened")
    type = models.CharField(max_length=50, choices=GROUP_EVENT_CHOICES)
    by = models.ForeignKey(Person)
    desc = models.TextField()

    def __unicode__(self):
        return u"%s %s at %s" % (self.by.plain_name(), self.get_type_display().lower(), self.time)

    class Meta:
        ordering = ['-time', 'id']

class ChangeStateGroupEvent(GroupEvent):
    state = models.ForeignKey(GroupStateName)

class MilestoneGroupEvent(GroupEvent):
    milestone = models.ForeignKey(GroupMilestone)

class Role(models.Model):
    name = models.ForeignKey(RoleName)
    group = models.ForeignKey(Group)
    person = models.ForeignKey(Person)
    email = models.ForeignKey(Email, help_text="Email address used by person for this role")
    def __unicode__(self):
        return u"%s is %s in %s" % (self.person.plain_name(), self.name.name, self.group.acronym or self.group.name)

    def formatted_email(self):
        return u'"%s" <%s>' % (self.person.plain_name(), self.email.address)

class RoleHistory(models.Model):
    # RoleHistory doesn't have a time field as it's not supposed to be
    # used on its own - there should always be a GroupHistory
    # accompanying a change in roles, so lookup the appropriate
    # GroupHistory instead
    name = models.ForeignKey(RoleName)
    group = models.ForeignKey(GroupHistory)
    person = models.ForeignKey(Person)
    email = models.ForeignKey(Email, help_text="Email address used by person for this role")
    def __unicode__(self):
        return u"%s is %s in %s" % (self.person.plain_name(), self.name.name, self.group.acronym)

    class Meta:
        verbose_name_plural = "role histories"
