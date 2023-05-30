from django import template
import pycmarkgfm

register = template.Library()

def markdown(string : str) -> str:
    return pycmarkgfm.gfm_to_html(string)

register.filter('markdown', markdown)
