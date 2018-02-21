from django.db import models

from ietf.group.models import Group
from ietf.name.models import DBTemplateTypeName
from ietf.utils.models import ForeignKey


TEMPLATE_TYPES = (
    ('plain', 'Plain'),
    ('rst', 'reStructuredText'),
    ('django', 'Django'),
    )


class DBTemplate(models.Model):
    path = models.CharField( max_length=255, unique=True, blank=False, null=False, )
    title = models.CharField( max_length=255, blank=False, null=False, )
    variables = models.TextField( blank=True, null=True, )
    type = ForeignKey( DBTemplateTypeName, )
    content = models.TextField( blank=False, null=False, )
    group = ForeignKey( Group, blank=True, null=True, )

    def __unicode__(self):
        return self.title
