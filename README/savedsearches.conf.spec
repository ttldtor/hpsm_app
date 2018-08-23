# HPSM alert settings

action.hpsm = [0|1]
* enable HPSM notification

action.hpsm.param.title = <string>
* The HPSM incident title
* (required)

action.hpsm.param.description = <string>
* The HPSM incident description
* (required)

action.hpsm.param.category = <string>
* Override HPSM incident category from global alert_actions config
* (optional)

action.hpsm.param.from = <string>
* Override Splunk service name from global alert_actions config
* (optional)

action.hpsm.param.login = <string>
* Override HPSM user login from global alert_actions config
* (optional)

action.hpsm.param.password = <string>
* Override HPSM user password from global alert_actions config
* (optional)
