import sys, json, urlib2

def sendMessage(settings):
    print >> sys.stderr, "DEBUG Sending message with settings %s" % settings
    login = setting("login")
    password = settings.get("password")
    url = settings.get("url").rstrip('/')
    title = settings.get("title")
    description = settings.get("description")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        if not sendMessage(payload.get('configuration')):
            print >> sys.stderr, "FATAL Failed trying to send room notification"
            sys.exit(2)
        else:
            print >> sys.stderr, "INFO Room notification successfully sent"
    else:
        print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
        sys.exit(1)