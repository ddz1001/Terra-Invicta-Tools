#Copyright 2026 Dante Zitello
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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