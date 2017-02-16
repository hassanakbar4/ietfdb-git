from django.conf.urls import patterns, url
from django.conf import settings

import ietf.stats.views

urlpatterns = patterns('',
    url("^$", ietf.stats.views.stats_index),
    url("^document/(?:(?P<stats_type>authors|pages|words|format|formlang|author/documents|author/affiliation|author/country|author/continent|author/citation)/)?$", ietf.stats.views.document_stats),
    url("^knowncountries/$", ietf.stats.views.known_countries_list),
    url("^review/(?:(?P<stats_type>completion|results|states|time)/)?(?:%(acronym)s/)?$" % settings.URL_REGEXPS, ietf.stats.views.review_stats),
)
