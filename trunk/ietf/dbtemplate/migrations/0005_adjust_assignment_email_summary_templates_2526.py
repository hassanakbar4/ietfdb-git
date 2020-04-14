# Copyright The IETF Trust 2019-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-13 13:41


from django.db import migrations

def forward(apps, schema_editor):
    DBTemplate = apps.get_model('dbtemplate','DBTemplate')

    DBTemplate.objects.filter(pk=182).update(content="""{% autoescape off %}Subject: Open review assignments in {{group.acronym}}

The following reviewers have assignments:{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }} {% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc.name }}-{% if r.review_request.requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request.doc.rev }}{% endif %} {{ r.earlier_reviews }}{% endfor %}

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}{% endautoescape %}
""")

    DBTemplate.objects.filter(pk=183).update(content="""{% autoescape off %}Subject: Review Assignments

Hi all,

The following reviewers have assignments:{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               Type      LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }} {% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{r.review_request.type.name|ljust:"10"}}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc.name }}-{% if r.review_request.requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request.doc.rev }}{% endif %}{% if r.earlier_reviews %} {{ r.earlier_reviews }}{% endif %}{% endfor %}

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}
The LC and Telechat review templates are included below:
-------------------------------------------------------

-- Begin LC Template --
I am the assigned Gen-ART reviewer for this draft. The General Area
Review Team (Gen-ART) reviews all IETF documents being processed
by the IESG for the IETF Chair.  Please treat these comments just
like any other last call comments.

For more information, please see the FAQ at

<https://trac.ietf.org/trac/gen/wiki/GenArtfaq>.

Document:
Reviewer:
Review Date:
IETF LC End Date:
IESG Telechat date: (if known)

Summary:

Major issues:

Minor issues:

Nits/editorial comments:

-- End LC Template --

-- Begin Telechat Template --
I am the assigned Gen-ART reviewer for this draft. The General Area
Review Team (Gen-ART) reviews all IETF documents being processed
by the IESG for the IETF Chair. Please wait for direction from your
document shepherd or AD before posting a new version of the draft.

For more information, please see the FAQ at

<https://trac.ietf.org/trac/gen/wiki/GenArtfaq>.

Document:
Reviewer:
Review Date:
IETF LC End Date:
IESG Telechat date: (if known)

Summary:

Major issues:

Minor issues:

Nits/editorial comments:

-- End Telechat Template --
{% endautoescape %}

""")
    
    DBTemplate.objects.filter(pk=184).update(content="""{% autoescape off %}Subject: Assignments

Review instructions and related resources are at:
http://tools.ietf.org/area/sec/trac/wiki/SecDirReview{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }}{{ r.earlier_review|yesno:'R, , ' }}{% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc.name }}-{% if r.review_request.requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request.doc.rev }}{% endif %}{% endfor %}

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}{% endautoescape %}

""")

    DBTemplate.objects.filter(pk=185).update(content="""{% autoescape off %}Subject: Open review assignments in {{group.acronym}}

Review instructions and related resources are at:
<https://trac.ietf.org/trac/ops/wiki/Directorates>

The following reviewers have assignments:{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }} {% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc.name }}-{% if r.review_request.requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request.doc.rev }}{% endif %} {{ r.earlier_reviews }}{% endfor %}

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}{% endautoescape %}

""")


def reverse(apps, schema_editor):
    DBTemplate = apps.get_model('dbtemplate','DBTemplate')

    DBTemplate.objects.filter(pk=182).update(content="""{% autoescape off %}Subject: Open review assignments in {{group.acronym}}

The following reviewers have assignments:{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }} {% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc_id }}-{% if r.review_request..requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request..doc.rev }}{% endif %} {{ r.earlier_review_mark }}{% endfor %}

* Other revision previously reviewed
** This revision already reviewed

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}{% endautoescape %}
""")

    DBTemplate.objects.filter(pk=183).update(content="""{% autoescape off %}Subject: Review Assignments

Hi all,

The following reviewers have assignments:{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               Type      LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }} {% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{r.review_request.type.name|ljust:"10"}}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc.name }}-{% if r.review_request.requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request.doc.rev }}{% endif %}{% if r.earlier_review_mark %} {{ r.earlier_review_mark }}{% endif %}{% endfor %}

* Other revision previously reviewed
** This revision already reviewed

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}
The LC and Telechat review templates are included below:
-------------------------------------------------------

-- Begin LC Template --
I am the assigned Gen-ART reviewer for this draft. The General Area
Review Team (Gen-ART) reviews all IETF documents being processed
by the IESG for the IETF Chair.  Please treat these comments just
like any other last call comments.

For more information, please see the FAQ at

<https://trac.ietf.org/trac/gen/wiki/GenArtfaq>.

Document:
Reviewer:
Review Date:
IETF LC End Date:
IESG Telechat date: (if known)

Summary:

Major issues:

Minor issues:

Nits/editorial comments:

-- End LC Template --

-- Begin Telechat Template --
I am the assigned Gen-ART reviewer for this draft. The General Area
Review Team (Gen-ART) reviews all IETF documents being processed
by the IESG for the IETF Chair. Please wait for direction from your
document shepherd or AD before posting a new version of the draft.

For more information, please see the FAQ at

<https://trac.ietf.org/trac/gen/wiki/GenArtfaq>.

Document:
Reviewer:
Review Date:
IETF LC End Date:
IESG Telechat date: (if known)

Summary:

Major issues:

Minor issues:

Nits/editorial comments:

-- End Telechat Template --
{% endautoescape %}

""")
    
    DBTemplate.objects.filter(pk=184).update(content="""{% autoescape off %}Subject: Assignments

Review instructions and related resources are at:
http://tools.ietf.org/area/sec/trac/wiki/SecDirReview{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }}{{ r.earlier_review|yesno:'R, , ' }}{% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc.name }}-{% if r.review_request.requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request.doc.rev }}{% endif %}{% endfor %}

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}{% endautoescape %}

""")

    DBTemplate.objects.filter(pk=185).update(content="""{% autoescape off %}Subject: Open review assignments in {{group.acronym}}

Review instructions and related resources are at:
<https://trac.ietf.org/trac/ops/wiki/Directorates>

The following reviewers have assignments:{% for r in review_assignments %}{% ifchanged r.section %}

{{r.section}}

{% if r.section == 'Early review requests:' %}Reviewer               Due        Draft{% else %}Reviewer               LC end     Draft{% endif %}{% endifchanged %}
{{ r.reviewer.person.plain_name|ljust:"22" }} {% if r.section == 'Early review requests:' %}{{ r.review_request.deadline|date:"Y-m-d" }}{% else %}{{ r.lastcall_ends|default:"None      " }}{% endif %} {{ r.review_request.doc.name }}-{% if r.review_request.requested_rev %}{{ r.review_request.requested_rev }}{% else %}{{ r.review_request.doc.rev }}{% endif %} {{ r.earlier_review_mark }}{% endfor %}

* Other revision previously reviewed
** This revision already reviewed

{% if rotation_list %}Next in the reviewer rotation:

{% for p in rotation_list %}  {{ p }}
{% endfor %}{% endif %}{% endautoescape %}

""")


class Migration(migrations.Migration):

    dependencies = [
        ('dbtemplate', '0004_adjust_assignment_email_summary_templates'),
    ]

    operations = [
        migrations.RunPython(forward,reverse),
    ]
