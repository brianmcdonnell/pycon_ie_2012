
def validate_params(handler, param_list):
    ''' Hiding this code here as it's not interesting for the tornado examples. '''
    if 'user' in param_list:
        username = handler.get_argument('user', None)
        if username is None:
            handler.set_status(400)
            handler.write("Bad Request. Missing 'user' url parameter.")
            handler.finish()
            return False
        data = handler.get_argument('data', None)

    if 'data' in param_list:
        if data is None:
            handler.set_status(400)
            handler.write("Bad Request. No data to translate.")
            handler.finish()
            return False
        if not data.strip().endswith('.'):
            handler.set_status(400)
            handler.write("Bad Request. Input data must end with period.")
            handler.finish()
            return False
    return True
