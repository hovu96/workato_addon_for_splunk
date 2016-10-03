

callback_search_param = 'action.workato.param.callback_url'
workato_alert_action = 'action.workato'

def has_workato_alert_action(saved_search):
    if workato_alert_action in saved_search.content:
        if saved_search[workato_alert_action] == '1':
            return True
    return False

def has_callback(saved_search):
    if callback_search_param in saved_search.content:
        if saved_search[callback_search_param]:
            return True
    return False

def add_callback(saved_search, callback_url):
    kwargs = {
        "actions": "workato",
        callback_search_param: callback_url,
        }
    saved_search.update(**kwargs)

def remove_callback(saved_search, callback_url):
    if callback_search_param in saved_search.content:
        if saved_search[callback_search_param] != callback_url:
            raise Exception('callback not registered')
    kwargs = {
        "actions": "",
        callback_search_param: "",
        }
    saved_search.update(**kwargs)
