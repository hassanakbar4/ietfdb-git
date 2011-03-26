# Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
#  * Neither the name of the Nokia Corporation and/or its
#    subsidiary(-ies) nor the names of its contributors may be used
#    to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django.conf.urls.defaults import patterns, url
from ietf.idrfc import views_doc, views_search, views_edit, views_ballot, views

urlpatterns = patterns('',
    (r'^/?$', views_search.search_main),
    (r'^search/$', views_search.search_results),
    (r'^all/$', views_search.all),
    (r'^active/$', views_search.active),
    (r'^in-last-call/$', views_search.in_last_call),
    url(r'^ad/(?P<name>[A-Za-z0-9.-]+)/$', views_search.by_ad, name="doc_search_by_ad"),
                       
    url(r'^(?P<name>[A-Za-z0-9.-]+)/((?P<tab>ballot|writeup|history)/)?$', views_doc.document_main, name="doc_view"),
    (r'^(?P<name>[A-Za-z0-9.-]+)/doc.json$', views_doc.document_debug),
    (r'^(?P<name>[A-Za-z0-9.-]+)/_ballot.data$', views_doc.document_ballot),
    (r'^(?P<name>[A-Za-z0-9.-]+)/ballot.tsv$', views_doc.ballot_tsv),
    (r'^(?P<name>[A-Za-z0-9.-]+)/ballot.json$', views_doc.ballot_json),

    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/state/$', views_edit.change_state, name='doc_change_state'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/info/$', views_edit.edit_info, name='doc_edit_info'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/requestresurrect/$', views_edit.request_resurrect, name='doc_request_resurrect'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/resurrect/$', views_edit.resurrect, name='doc_resurrect'),                       
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/addcomment/$', views_edit.add_comment, name='doc_add_comment'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/position/$', views_ballot.edit_position, name='doc_edit_position'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/deferballot/$', views_ballot.defer_ballot, name='doc_defer_ballot'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/undeferballot/$', views_ballot.undefer_ballot, name='doc_undefer_ballot'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/sendballotcomment/$', views_ballot.send_ballot_comment, name='doc_send_ballot_comment'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/lastcalltext/$', views_ballot.lastcalltext, name='doc_ballot_lastcall'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/ballotwriteupnotes/$', views_ballot.ballot_writeupnotes, name='doc_ballot_writeupnotes'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/approvaltext/$', views_ballot.ballot_approvaltext, name='doc_ballot_approvaltext'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/approveballot/$', views_ballot.approve_ballot, name='doc_approve_ballot'),
    url(r'^(?P<name>[A-Za-z0-9.-]+)/edit/makelastcall/$', views_ballot.make_last_call, name='doc_make_last_call'),
)
