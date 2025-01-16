import json
import csv
import io



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