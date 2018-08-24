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
    from_value = settings.get("from", "splunk")
    body = r'{"tlmrSplunkMon": {"title": "%s", "description": ["%s"], "category": "%s", "from": "%s"}}' % (
        title_value, description_value, category_value, from_value)
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
        print >> sys.stderr, "ERROR Error sending message: %s" % e
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        if not send_message(payload.get('configuration')):
            print >> sys.stderr, "FATAL Failed trying to send room notification"
            sys.exit(2)
        else:
            print >> sys.stderr, "INFO Room notification successfully sent"
    else:
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)
