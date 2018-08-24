import re
from enum import Enum, auto
from datetime import datetime

"""
This exception is throw when a request parsing fails
"""
class RequestException(Exception):
    pass

"""
This is the base class of an addon, 
- configure() method is called on addons loading,
  configuration parameter is a dictionnary
- execute() method is called when a request is received and parsed
  duplex parameter is an instance of the Duplex class in the bottom of this file
"""
class Addon(object):

    def configure(self, configuration):
        raise NotImplementedError()
    
    def execute(self, duplex):
        raise NotImplementedError()

"""
HTTP Protocol
"""
class HTTPStatus(object):
    class Status(Enum):
        UNKNOWN = 0
        CONTINUE = 100
        SWITCHING_PROTOCOLS = 101
        OK = 200
        CREATED = 201
        ACCEPTED = 202
        NONAUTHORITATIVE_INFORMATION = 203
        NO_CONTENT = 204
        RESET_CONTENT = 205
        PARTIAL_CONTENT = 206
        MULTIPLE_CHOICES = 300
        MOVED_PERMANENTLY = 301
        FOUND = 302
        SEE_OTHER = 303
        NOT_MODIFIED = 304
        USE_PROXY = 305
        TEMPORARY_REDIRECT = 307
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        PAYMENT_REQUIRED = 402
        FORBIDDEN = 403
        NOT_FOUND = 404
        METHOD_NOT_ALLOWED = 405
        NOT_ACCEPTABLE = 406
        PROXY_AUTHENTICATION_REQUIRED = 407
        REQUEST_TIMEOUT = 408
        CONFLICT = 409
        GONE = 410
        LENGTH_REQUIRED = 411
        PRECONDITION_FAILED = 412
        REQUEST_ENTITY_TOO_LARGE = 413
        REQUEST_URI_TOO_LARGE = 414
        UNSUPPORTED_MEDIA_TYPE = 415
        REQUESTED_RANGE_NOT_SATISFIABLE = 416
        EXPECTATION_FAILED = 417
        IM_A_TEAPOT = 418
        INTERNAL_SERVER_ERROR = 500
        NOT_IMPLEMENTED = 501
        BAD_GATEWAY = 502
        SERVICE_UNAVAILABLE = 503
        GATEWAY_TIMEOUT = 504
        HTTP_VERSION_NOT_SUPPORTED = 505

    class Version(Enum):
        UNKNOWN = auto()
        HTTP_0_9 = auto()
        HTTP_1_0 = auto()
        HTTP_1_1 = auto()
        HTTP_2_0 = auto()

        @staticmethod
        def to_type(strVersion):
            return {
                'HTTP/0.9': HTTPStatus.Version.HTTP_0_9,
                'HTTP/1.0': HTTPStatus.Version.HTTP_1_0,
                'HTTP/1.1': HTTPStatus.Version.HTTP_1_1,
                'HTTP/2.0': HTTPStatus.Version.HTTP_2_0
            }.get(strVersion, HTTPStatus.Version.UNKNOWN)

        @staticmethod
        def to_string(version):
            return {
                HTTPStatus.Version.HTTP_0_9: 'HTTP/0.9',
                HTTPStatus.Version.HTTP_1_0: 'HTTP/1.0',
                HTTPStatus.Version.HTTP_1_1: 'HTTP/1.1',
                HTTPStatus.Version.HTTP_2_0: 'HTTP/2.0'
            }.get(version, 'HTTP/UNKNOWN')
    
    class Method(Enum):
        UNKNOWN = auto()
        OPTIONS = auto()
        GET = auto()
        HEAD = auto()
        POST = auto()
        PUT = auto()
        DELETE = auto()
        TRACE = auto()
        CONNECT = auto()

        @staticmethod
        def to_type(strMethod):
            return {
                'OPTIONS': HTTPStatus.Method.OPTIONS,
                'GET': HTTPStatus.Method.GET,
                'HEAD': HTTPStatus.Method.HEAD,
                'POST': HTTPStatus.Method.POST,
                'PUT': HTTPStatus.Method.PUT,
                'DELETE': HTTPStatus.Method.DELETE,
                'TRACE': HTTPStatus.Method.TRACE,
                'CONNECT': HTTPStatus.Method.CONNECT,
            }.get(strMethod, HTTPStatus.Method.UNKNOWN)

        @staticmethod
        def to_string(method):
            return {
                HTTPStatus.Method.OPTIONS: 'OPTIONS',
                HTTPStatus.Method.GET: 'GET',
                HTTPStatus.Method.HEAD: 'HEAD',
                HTTPStatus.Method.POST: 'POST',
                HTTPStatus.Method.PUT: 'PUT',
                HTTPStatus.Method.DELETE: 'DELETE',
                HTTPStatus.Method.TRACE: 'TRACE',
                HTTPStatus.Method.CONNECT: 'CONNECT',
            }.get(method, 'UNKNOWN')

"""
This class represent a parsed HTTP request
"""
class HTTPRequest(object):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.get('version', HTTPStatus.Version.UNKNOWN)
        self.headers = kwargs.get('headers', {})
        self.body = kwargs.get('body', None)
        self.method = kwargs.get('method', HTTPStatus.Method.UNKNOWN)
        self.uri = kwargs.get('uri', None)

"""
This class represent an HTTP answer, it has to be formated to be sent, see format_response method
"""
class HTTPResponse(object):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.get('version', HTTPStatus.Version.UNKNOWN)
        self.headers = kwargs.get('headers', {})
        self.body = kwargs.get('body', None)
        self.status = kwargs.get('status', HTTPStatus.Status.UNKNOWN)
        self.reason = kwargs.get('reason', self.status.name)

"""
This class will contains the parsed request, the response instance, and the socket who received the request
"""
class HTTPDuplex(object):
    request = None
    response = None
    socket = None

"""
Call this method to get a parsed HTTP request
"""
def parse_request(raw_request):
    raw_request = raw_request.split('\r\n\n')
    head_spltd_request = raw_request[0].split('\r\n')
    head_pattern = re.match(r'(.*?)\s(.*?)\s(.*)', head_spltd_request[0])

    if not head_pattern:
        raise RequestException()

    method = HTTPStatus.Method.to_type(head_pattern.group(1))
    uri = head_pattern.group(2)
    http_version = HTTPStatus.Version.to_type(head_pattern.group(3))

    headers = dict()

    for raw_header in head_spltd_request[1:]:
        header_pattern = re.match(r'(.*?):\s(.*)', raw_header)

        if header_pattern is not None:
            headers[header_pattern.group(1)] = header_pattern.group(2)
    
    if len(raw_request) > 1:
        body = '\n\n'.join(raw_request[1:])
    else:
        body = None
    
    return HTTPRequest(method=method, uri=uri, version=http_version, headers=headers, body=body)

"""
This method is made to parse php-cgi response
"""
def parse_php_response(raw_response):
    raw_response = raw_response.decode('utf-8').splitlines()

    http_version = HTTPStatus.Version.UNKNOWN
    status = HTTPStatus.Status.UNKNOWN
    reason = 'UNKNOWN'
    body = ''

    headers = dict()

    for k, raw_header in enumerate(raw_response):
        if not raw_header:
            body = ''.join(raw_response[k:])
            break

        header_pattern = re.match(r'(.*?):\s(.*)', raw_header)

        if header_pattern is not None:
            headers[header_pattern.group(1)] = header_pattern.group(2)

    return HTTPResponse(version=http_version, status=status, reason=reason, headers=headers, body=body)

"""
Call this method to convert an HTTP response instance to a text response
"""
def format_response(response_instance):
    raw_response = list()

    raw_response.append(' '.join([
        HTTPStatus.Version.to_string(response_instance.version),
        str(response_instance.status.value),
        response_instance.reason
    ]))

    response_instance.headers['Date'] = datetime.now().strftime('%a, %d %b %Y %X %Z')

    if 'Content-Length' not in response_instance.headers:
        response_instance.headers['Content-Length'] = len(response_instance.body)

    for key, value in response_instance.headers.items():
        raw_response.append(': '.join([str(key), str(value)]))
    
    raw_response.append('\n')
    raw_response.append(response_instance.body)

    return '\n'.join(raw_response)