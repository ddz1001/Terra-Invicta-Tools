import json
import csv
import io
import xml.dom.minidom as xml


def to_json(values: list[dict]):
    return json.dumps(values, indent=4)

def to_csv(values: list[dict]):
    headers = values[0].keys()

    strbuffer = io.StringIO()
    writer = csv.writer(strbuffer, delimiter=',', quotechar='"', quoting=csv.QUOTE_STRINGS, dialect='excel')
    writer.writerow(headers)

    for row in values:
        writer.writerow(row.values())

    return strbuffer.getvalue()

def to_html_table(values: list[dict]):
    document = xml.Document()

    table = document.createElement('table')
    document.appendChild(table)

    headers = values[0].keys()

    hrow = table.appendChild( document.createElement('tr') )
    for header in headers:
        th = document.createElement('th')
        th.appendChild(document.createTextNode( str(header) ))
        hrow.appendChild(th)
    table.appendChild(hrow)

    for row in values:
        cr = document.createElement('tr')
        for value in row.values():
            td = document.createElement('td')
            td.appendChild( document.createTextNode(str(value)))
            cr.appendChild( td )
        table.appendChild(cr)

    return table.toprettyxml(indent='  ')