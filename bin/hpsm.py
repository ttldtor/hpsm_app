# coding=utf-8
import base64
import json
import sys
import urllib2


def send_message(settings):
    print >> sys.stderr, "DEBUG Sending message with settings %s" % settings
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
    request = urllib2.Request(base_url_value, body, {"Content-Type": "application/json"})
    request.add_header("Authorization",
                       "Basic %s" % base64.encodestring('%s:%s' % (login_value, password_value)).replace('\n', ''))
    try:
        res = urllib2.urlopen(request)
        body = res.read()
        print >> sys.stderr, "INFO HPSM server responded with HTTP status=%d" % res.code
        print >> sys.stderr, "DEBUG HPSM server response: %s" % json.dumps(body)
        return 200 <= res.code < 300
    except urllib2.HTTPError, e:
        print >> sys.stderr, "ERROR Error sending HPSM incident: %s" % e
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        if not send_message(payload.get('configuration')):
            print >> sys.stderr, "FATAL Failed trying to send HPSM incident"
            sys.exit(2)
        else:
            print >> sys.stderr, "INFO HPSM incident successfully sent"
    else:
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)
