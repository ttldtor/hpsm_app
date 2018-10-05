# coding=utf-8
import base64
import json
import sys
import urllib2
import urllib
import splunk.rest as rest
import tempfile
import os.path
from datetime import datetime


def now_str():
    return datetime.now().isoformat(' ')


log_format = "%s %s| %s"


def log(level, message):
    with open(os.path.join(tempfile.gettempdir(), 'hpsmapp.log'), 'a') as f:
        print >> f, log_format % (now_str(), level, message)


def debug(message):
    log("DEBUG", message)


def info(message):
    log("INFO", message)


def error(message):
    log("ERROR", message)


def get_incident_key(incident_id, session_key):
    query = '{"incident_id": "%s"}' % incident_id
    uri = '/servicesNS/nobody/alert_manager/storage/collections/data/incidents?query=%s' % urllib.quote(query)
    incident = get_rest_data(uri, session_key)
    incident_key = incident[0]["_key"]
    return incident_key


def set_incident_external_reference_id(external_key, incident_key, session_key):
    uri = '/servicesNS/nobody/alert_manager/storage/collections/data/incidents/%s' % incident_key
    incident = get_rest_data(uri, session_key)
    incident['external_reference_id'] = external_key
    get_rest_data(uri, session_key, json.dumps(incident))


def get_rest_data(uri, session_key, data=None):
    try:
        if data is None:
            server_response, server_content = rest.simpleRequest(uri, sessionKey=session_key)
        else:
            server_response, server_content = rest.simpleRequest(uri, sessionKey=session_key, jsonargs=data)
    except Exception as e:
        error(e)
        server_content = None

    try:
        return_data = json.loads(server_content)
    except Exception as e:
        error(e)
        return_data = []

    return return_data


def send_message(settings, session_key):
    print >> sys.stderr, "DEBUG Sending message with settings %s, session_key = %s" % (settings, session_key)
    debug("Sending message with settings %s, session_key = %s" % (settings, session_key))
    login_value = settings.get("login")
    password_value = settings.get("password")
    base_url_value = settings.get("url").rstrip('/')
    title_value = settings.get("title")
    description_value = settings.get("description")
    category_value = settings.get("category", "incidents")
    subcategory_value = settings.get("subcategory", "Другое")
    product_type_value = settings.get("productType", "Другое")
    from_value = settings.get("from", "splunk")
    affected_item_value = settings.get("affectedItem", "CI1127974")
    location_value = settings.get("location", "5a12997da100a05f506e1e38")
    callback_contact_value = settings.get("callbackContact", "splunk")
    contact_name_value = settings.get("contactName", "splunk")
    assignment_value = settings.get("assignment", "SPLUNK")
    incident_id_value = settings.get("incidentId", "Unknown")

    body = json.dumps(
        {
            "tlmrSplunkMon": {
                "title": title_value,
                "description": [description_value],
                "category": category_value,
                "subcategory": subcategory_value,
                "product.type": product_type_value,
                "from": from_value,
                "affected.item": affected_item_value,
                "location": location_value,
                "callback.contact": callback_contact_value,
                "contact.name": contact_name_value,
                "assignment": assignment_value
            }
        }
    )

    print >> sys.stderr, 'DEBUG Calling url="%s" with body=%s' % (base_url_value, body)
    debug('Calling url="%s" with body=%s' % (base_url_value, body))
    request = urllib2.Request(base_url_value, body, {"Content-Type": "application/json"})
    request.add_header("Authorization",
                       "Basic %s" % base64.encodestring('%s:%s' % (login_value, password_value)).replace('\n', ''))
    try:
        res = urllib2.urlopen(request)
        body = res.read()
        print >> sys.stderr, "INFO HPSM server responded with HTTP status=%d" % res.code
        info('HPSM server responded with HTTP status=%d' % res.code)
        print >> sys.stderr, "DEBUG HPSM server response: %s" % json.dumps(body)
        debug('HPSM server response: %s' % json.dumps(body))

        if 200 <= res.code < 300 and incident_id_value != "Unknown":
            json_body = json.loads(body)
            incident_data = json_body.get("tlmrSplunkMon")
            external_id = incident_data.get("number", "")

            if external_id != "":
                incident_key = get_incident_key(incident_id_value, session_key)
                set_incident_external_reference_id(external_id, incident_key, session_key)

        return 200 <= res.code < 300
    except urllib2.HTTPError, e:
        print >> sys.stderr, "ERROR Error sending HPSM incident: %s" % e
        error("ERROR Error sending HPSM incident: %s" % e)
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        if not send_message(payload.get('configuration'), payload.get('session_key')):
            print >> sys.stderr, "FATAL Failed trying to send HPSM incident"
            error('Failed trying to send HPSM incident')
            sys.exit(2)
        else:
            print >> sys.stderr, "INFO HPSM incident successfully sent"
            info('HPSM incident successfully sent')
    else:
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        error('FATAL Unsupported execution mode (expected --execute flag)')
        sys.exit(1)
