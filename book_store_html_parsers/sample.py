import json
import sys
import urllib
from xml.sax.saxutils import escape

for arg in sys.argv[1:]:

    url = arg
    f = urllib.urlopen(url)

    # html_escape_table = {
    #     '"': "&quot;",
    #     "'": "&apos;"
    # }
    # html_unescape_table = {v: k for k, v in html_escape_table.items()}


    # def html_escape(text):
    #     return escape(text, html_escape_table)


    # def html_unescape(text):
    #     return unescape(text, html_unescape_table)

    # escape() and unescape() takes care of &, < and >.


    # html = html_escape(f.read())
    html = f.read().replace('"', '\"').replace('\n', '\\n').replace('\t\t', '\t')
    d = dict(url=url, html=html)

    print json.dumps(d)
