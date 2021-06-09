from rest_framework.views import exception_handler


def exception_decorator(exception, context):
    response = exception_handler(exception, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response
