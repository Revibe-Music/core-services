from rest_framework.views import exception_handler

# -----------------------------------------------------------------------------

def custom_exception_hanlder(exc, context):
    # call default exception handler to get response
    response = exception_handler(exc, context)

    # add custom response code to it
    if response is not None:
        response.data['status_code'] = response.status_code
    
    return response
