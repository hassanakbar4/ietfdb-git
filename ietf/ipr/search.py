import re
import django.utils.html
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from ietf.idtracker.models import IETFWG, InternetDraft, Rfc
from ietf.ipr.models import IprRfc, IprDraft, IprDetail
from ietf.ipr.related import related_docs
from ietf.utils import log


def mark_last_doc(iprs):
    for item in iprs:
        if item.drafts.count():
            item.last_draft = item.drafts.all()[int(item.drafts.count())-1]
        if item.rfcs.count():
            item.last_rfc = item.rfcs.all()[int(item.rfcs.count())-1]

def mark_related_doc(iprs):
    for item in iprs:
        for entry in item.drafts.all():
            related_docs(entry.document, [])
        for entry in item.rfcs.all():
            related_docs(entry.document, [])

def unique_iprs(iprs):
    ids = []
    unique = []
    for ipr in iprs:
        if not ipr.ipr_id in ids:
            ids += [ ipr.ipr_id ]
            unique += [ ipr ]
    return unique

def iprs_from_docs(docs):
    iprs = []
    for doc in docs:
        if isinstance(doc, InternetDraft):
            disclosures = [ item.ipr for item in IprDraft.objects.filter(document=doc, ipr__status__in=[1,3]) ]
        elif isinstance(doc, Rfc):
            disclosures = [ item.ipr for item in IprRfc.objects.filter(document=doc, ipr__status__in=[1,3]) ]
        else:
            raise ValueError("Doc type is neither draft nor rfc: %s" % doc)
        if disclosures:
            doc.iprs = disclosures
            iprs += disclosures
    iprs = list(set(iprs))
    return iprs, docs

def search(request, type="", q="", id=""):
    wgs = IETFWG.objects.filter(group_type__group_type_id=1).exclude(group_acronym__acronym='2000').select_related().order_by('acronym.acronym')
    args = request.REQUEST.items()
    if args:
        for key, value in args:
            if key == "option":
                type = value
            if re.match(".*search", key):
                q = value
            if re.match(".*id", key):
                id = value
        if type and q or id:
            log("Got query: type=%s, q=%s, id=%s" % (type, q, id))

            # Search by RFC number or draft-identifier
            # Document list with IPRs
            if type in ["document_search", "rfc_search"]:
                if type == "document_search":
                    if q:
                        start = InternetDraft.objects.filter(filename__contains=q)
                    if id:
                        start = InternetDraft.objects.filter(id_document_tag=id)
                if type == "rfc_search":
                    if q:
                        start = Rfc.objects.filter(rfc_number=q)
                if start.count() == 1:
                    first = start[0]
                    # get all related drafts, then search for IPRs on all

                    docs = related_docs(first, [])
                    #docs = get_doclist.get_doclist(first)
                    iprs, docs = iprs_from_docs(docs)
                    return render("ipr/search_doc_result.html", {"q": q, "first": first, "iprs": iprs, "docs": docs},
                                  context_instance=RequestContext(request) )
                elif start.count():
                    return render("ipr/search_doc_list.html", {"q": q, "docs": start },
                                  context_instance=RequestContext(request) )                        
                else:
                    raise ValueError("Missing or malformed search parameters, or internal error")

            # Search by legal name
            # IPR list with documents
            elif type == "patent_search":
                iprs = IprDetail.objects.filter(legal_name__icontains=q, status__in=[1,3]).order_by("-submitted_date", "-ipr_id")
                count = iprs.count()
                iprs = [ ipr for ipr in iprs if not ipr.updated_by.all() ]
                # Some extra information, to help us render 'and' between the
                # last two documents in a sequence
                mark_last_doc(iprs)
                return render("ipr/search_holder_result.html", {"q": q, "iprs": iprs, "count": count },
                                  context_instance=RequestContext(request) )

            # Search by content of email or pagent_info field
            # IPR list with documents
            elif type == "patent_info_search":
                pass

            # Search by wg acronym
            # Document list with IPRs
            elif type == "wg_search":
                try:
                    docs = list(InternetDraft.objects.filter(group__acronym=q))
                except:
                    docs = []
                docs += [ draft.replaced_by for draft in docs if draft.replaced_by_id ]
                docs += list(Rfc.objects.filter(group_acronym=q))

                docs = [ doc for doc in docs if doc.ipr.count() ]
                iprs, docs = iprs_from_docs(docs)
                count = len(iprs)
                return render("ipr/search_wg_result.html", {"q": q, "docs": docs, "count": count },
                                  context_instance=RequestContext(request) )

            # Search by rfc and id title
            # Document list with IPRs
            elif type == "title_search":
                try:
                    docs = list(InternetDraft.objects.filter(title__icontains=q))
                except:
                    docs = []
                docs += list(Rfc.objects.filter(title__icontains=q))

                docs = [ doc for doc in docs if doc.ipr.count() ]
                iprs, docs = iprs_from_docs(docs)
                count = len(iprs)
                return render("ipr/search_doctitle_result.html", {"q": q, "docs": docs, "count": count },
                                  context_instance=RequestContext(request) )


            # Search by title of IPR disclosure
            # IPR list with documents
            elif type == "ipr_title_search":
                pass
            else:
                raise ValueError("Unexpected search type in IPR query: %s" % type)
        return django.http.HttpResponseRedirect(request.path)
    return render("ipr/search.html", {"wgs": wgs}, context_instance=RequestContext(request))
