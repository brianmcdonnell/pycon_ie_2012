from twisted.web import resource

def validate_params(request, param_list):
    ''' Hiding this code here as it's not interesting for the twisted examples. '''

    if 'user' in param_list:
        user = request.args.get('user', None)
        if user is None:
            return resource.ErrorPage(400, "Bad Request", "Missing 'user' url parameter.").render(request)

    if 'data' in param_list:
        data = request.args.get('data', None)
        if data is None:
            return resource.ErrorPage(400, "Bad Request", "Missing 'data' url parameter. Nothing to translate.").render(request)
        input_str = data[0]
        if not input_str.strip().endswith('.'):
            return resource.ErrorPage(400, "Bad Request", "Input data must end with period").render(request)
