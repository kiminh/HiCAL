import os
import django
import httplib2
import urllib.parse

os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings.local'
django.setup()

from treccoreweb.judgment.models import Judgement
from treccoreweb.topic.models import Topic
from config.settings.base import CAL_SERVER_IP, CAL_SERVER_PORT


judgments = {}


for row in Topic.objects.all():
    session_id = str(row.uuid)
    seed_query = str(row.seed_query)

    judgments[(session_id, seed_query)] = []

for row in Judgement.objects.all():
    session_id = str(row.topic.uuid)
    seed_query = str(row.topic.seed_query)

    judgments[(session_id, seed_query)].append((row.doc_id, -1 if row.nonrelevant else 1))


for session_id, seed_query in judgments:
    h = httplib2.Http()
    url = "http://{}:{}/CAL/begin".format(CAL_SERVER_IP, CAL_SERVER_PORT)

    body = {'session_id': session_id,
            'seed_query': seed_query}
    body = urllib.parse.urlencode(body)
    resp, _ = h.request(url,
                        body=body,
                        headers={'Content-Type': 'text/parameters; charset=UTF-8'},
                        method="POST")

    if resp and resp['status'] != '200':
        print("Session {}-'{}' already exists".format(session_id, seed_query))
    else:
        print("Restoring {}: '{}'...".format(session_id, seed_query))
        for doc_id, rel in judgments[(session_id, seed_query)]:
            url = "http://{}:{}/CAL/judge".format(CAL_SERVER_IP, CAL_SERVER_PORT)
            body = {'session_id': session_id,
                    'doc_id': doc_id,
                    'rel': rel}
            body = urllib.parse.urlencode(body)

            resp, _ = h.request(url,
                                body=body,
                                headers={
                                    'Content-Type': 'text/parameters; charset=UTF-8'
                                },
                                method="POST")

            if resp and resp['status'] != '200':
                print("\tError: Judgment on document "
                      "{} was not received by CAL. {} ".format(doc_id, resp))