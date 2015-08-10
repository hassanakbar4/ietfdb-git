# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def make_recipients(apps):

    Recipient=apps.get_model('mailtoken','Recipient')

    rc = Recipient.objects.create

    rc(slug='iesg',
       desc='The IESG',
       template='The IESG <iesg@ietf.org>')

    rc(slug='ietf_announce',
       desc='The IETF Announce list',
       template='IETF-Announce <ietf-announce@ietf.org>')

    rc(slug='rfc_editor',
       desc='The RFC Editor',
       template='<rfc-editor@rfc-editor.org>')

    rc(slug='iesg_secretary',
       desc='The Secretariat',
       template='<iesg-secretary@ietf.org>')

    rc(slug='doc_authors',
       desc="The document's authors",
       template='{{doc.name}}@ietf.org')

    rc(slug='doc_notify',
       desc="The addresses in the document's notify field",
       template='{{doc.notify}}')

    rc(slug='doc_group_chairs',
       desc="The document's group chairs (if the document is assigned to a working or research group)",
       template=None)

    rc(slug='doc_affecteddoc_authors',
       desc="The authors of the subject documents of a conflict-review or status-change",
       template=None)

    rc(slug='doc_affecteddoc_group_chairs',
       desc="The chairs of groups of the subject documents of a conflict-review or status-change",
       template=None)

    rc(slug='doc_affecteddoc_notify',
       desc="The notify field of the subject documents of a conflict-review or status-change",
       template=None)

    rc(slug='doc_shepherd',
       desc="The document's shepherd",
       template='{% if doc.shepherd %}{{doc.shepherd.address}}{% endif %}' )

    rc(slug='doc_ad',
       desc="The document's responsible Area Director",
       template='{% if doc.ad %}{{doc.ad.email_address}}{% endif %}' )

    rc(slug='doc_group_mail_list',
       desc="The list address of the document's group",
       template=None )

    rc(slug='doc_stream_owner',
       desc="The owner of the document's stream",
       template='{% if doc.stream_id == "ise" %}<rfc-ise@rfc-editor.org>{% endif %}{% if doc.stream_id == "irtf" %}<irtf-chair@irtf.org>{% endif %}{% if doc.stream_id == "ietf" %}<iesg@ietf.org>{% endif %}')

    rc(slug='conflict_review_stream_owner',
       desc="The stream owner of a document being reviewed for IETF stream conflicts",
       template = None )

    rc(slug='conflict_review_steering_group',
       desc="The steering group (e.g. IRSG) of a document being reviewed for IETF stream conflicts",
       template = None)

    rc(slug='iana_approve',
       desc="IANA's draft approval address",
       template='IANA <drafts-approval@icann.org>')

    rc(slug='iana',
       desc="IANA",
       template='<iana@iana.org>')

    rc(slug='group_mail_list',
       desc="The group's mailing list",
       template='{{ group.list_email }}')

    rc(slug='group_steering_group',
       desc="The group's steering group (IESG or IRSG)",
       template=None)

    rc(slug='group_chairs',
       desc="The group's chairs",
       template="{{group.acronym}}-chairs@ietf.org")

def make_mailtokens(apps):

    Recipient=apps.get_model('mailtoken','Recipient')
    MailToken=apps.get_model('mailtoken','MailToken')

    def mt_factory(slug,desc,recipient_slugs):
        m = MailToken.objects.create(slug=slug, desc=desc)
        m.recipients = Recipient.objects.filter(slug__in=recipient_slugs)

    mt_factory(slug='ballot_saved',
               desc='Recipients when a new ballot position (with discusses, other blocking positions, or comments) is saved',
               recipient_slugs=['iesg'])

    mt_factory(slug='ballot_saved_cc',
               desc='Copied when a new ballot position (with discusses, other blocking positions, or comments) is saved',
               recipient_slugs=['doc_authors',
                                'doc_group_chairs',
                                'doc_shepherd',
                                'doc_affecteddoc_authors',
                                'doc_affecteddoc_group_chairs',
                                'doc_affecteddoc_notify',
                                'conflict_review_stream_owner',
                                ])

    mt_factory(slug='ballot_deferred',
               desc='Recipients when a ballot is deferred to or undeferred from a future telechat',
               recipient_slugs=['iesg',
                                'iesg_secretary',
                                'doc_group_chairs',
                                'doc_notify',
                                'doc_authors',
                                'doc_shepherd',
                                'doc_affecteddoc_authors',
                                'doc_affecteddoc_group_chairs',
                                'doc_affecteddoc_notify',
                                'conflict_review_stream_owner',
                                ])

    mt_factory(slug='ballot_approved_ietf_stream',
               desc='Recipients when an IETF stream document ballot is approved',
               recipient_slugs=['ietf_announce'])

    mt_factory(slug='ballot_approved_ietf_stream_cc',
               desc='Copied when an IETF stream document ballot is approved',
               recipient_slugs=['iesg',
                                'doc_notify',
                                'doc_ad',
                                'doc_authors',
                                'doc_shepherd',
                                'doc_group_mail_list',
                                'doc_group_chairs',
                                'rfc_editor',
                                ])
 
    mt_factory(slug='ballot_approved_ietf_stream_iana',
               desc='Recipients for IANA message when an IETF stream document ballot is approved',
               recipient_slugs=['iana_approve'])

    mt_factory(slug='ballot_approved_conflrev',
               desc='Recipients when a conflict review ballot is approved',
               recipient_slugs=['conflict_review_stream_owner',
                                'conflict_review_steering_group',
                                'doc_affecteddoc_authors',
                                'doc_affecteddoc_group_chairs',
                                'doc_affecteddoc_notify',
                                'doc_notify',
                                ])

    mt_factory(slug='ballot_approved_conflrev_cc',
               desc='Copied when a conflict review ballot is approved',
               recipient_slugs=['iesg',
                                'ietf_announce',
                                'iana',
                                ])

    mt_factory(slug='ballot_approved_charter',
               desc='Recipients when a charter is approved',
               recipient_slugs=['ietf_announce',])
            
    mt_factory(slug='ballot_approved_charter_cc',
               desc='Copied when a charter is approved',
               recipient_slugs=['group_mail_list',
                                'group_steering_group',
                                'group_chairs',
                                'doc_notify',
                               ])
            
    mt_factory(slug='ballot_approved_status_change',
               desc='Recipients when a status change is approved',
               recipient_slugs=['ietf_announce',])
            
    mt_factory(slug='ballot_approved_status_change_cc',
               desc='Copied when a status change is approved',
               recipient_slugs=['iesg',
                                'rfc_editor',
                                'doc_notify',
                                'doc_affectddoc_authors',
                                'doc_affecteddoc_group_chairs',
                                'doc_affecteddoc_notify',
                               ])


def forward(apps, schema_editor):

    make_recipients(apps)
    make_mailtokens(apps)

def reverse(apps, schema_editor):

    Recipient=apps.get_model('mailtoken','Recipient')
    MailToken=apps.get_model('mailtoken','MailToken')

    Recipient.objects.all().delete()
    MailToken.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mailtoken', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
