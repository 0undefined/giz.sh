from django import template
from django.template.defaultfilters import stringfilter
import pycmarkgfm

from gitolite.models import Issue

register = template.Library()

def markdown(string : str) -> str:
    return pycmarkgfm.gfm_to_html(string)

def status_icon(issue : Issue) -> str:
    status = list(filter(lambda s: s == issue.status, list(issue.IssueStatusOptions)))[0]
    icon = ""

    icon += "status_" + status.name.lower()
    #if status[0] == Issue.IssueStatusOptions.OPEN:
    #    icon = "fa-circle-dot status_open"

    #elif status[0] == Issue.IssueStatusOptions.CLOSED:
    #    icon = "fa-circle-check status_closed"

    #elif status[0] == Issue.IssueStatusOptions.REOPENED:
    #    icon = "fa-circle-exclamation status_reopened"

    #elif status[0] == Issue.IssueStatusOptions.WONTFIX:
    #    icon = "fa-circle-xmark status_wontfix"

    #elif status[0] == Issue.IssueStatusOptions.DUPLICATE:
    #    icon = "fa-copy status_duplicate"

    return '<span class="status">' + status.label + ' <i class="fa-solid ' + icon + '"></i></span>'


@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]

register.filter('markdown', markdown)
register.filter('status_icon', status_icon)
register.filter('upto', upto)
