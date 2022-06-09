# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED

class CoapError(Exception):
    @property
    def exit_status(self):
        if 200 <= self.coap_code <= 231:
            return 0
        elif 400 <= self.coap_code <= 431:
            return 100 + (self.coap_code % 100)
        elif 500 <= self.coap_code <= 531:
            return 200 + (self.coap_code % 100)
        else:
            return 200  # Internal Server Error

    def __init__(self, coap_code, msg):
        super(Exception, self).__init__('%d: %s' % (coap_code, msg))
        self.coap_code = coap_code


CoapError.BAD_REQUEST = CoapError(400, 'Bad Request')
CoapError.UNAUTHORIZED = CoapError(401, 'Unauthorized')
CoapError.BAD_OPTION = CoapError(402, 'Bad Option')
CoapError.FORBIDDEN = CoapError(403, 'Forbidden')
CoapError.NOT_FOUND = CoapError(404, 'Not Found')
CoapError.METHOD_NOT_ALLOWED = CoapError(405, 'Method Not Allowed')
CoapError.NOT_ACCEPTABLE = CoapError(406, 'Not Acceptable')
CoapError.PRECONDITION_FAILED = CoapError(412, 'Precondition Failed')
CoapError.REQUEST_ENTITY_TOO_LARGE = CoapError(413, 'Request Entity Too Large')
CoapError.UNSUPPORTED_CONTENT_FORMAT = CoapError(415, 'Unsupported Content Format')

CoapError.INTERNAL_SERVER_ERROR = CoapError(500, 'Internal Server Error')
CoapError.NOT_IMPLEMENTED = CoapError(501, 'Not Implemented')
CoapError.BAD_GATEWAY = CoapError(502, 'Bad Gateway')
CoapError.SERVICE_UNAVAILABLE = CoapError(503, 'Service Unavailable')
CoapError.GATEWAY_TIMEOUT = CoapError(504, 'Gateway Timeout')
CoapError.PROXYING_NOT_SUPPORTED = CoapError(505, 'Proxying Not Supported')
