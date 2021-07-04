class ProbloxException(Exception):
    pass

class WebError(ProbloxException):
    pass

class APIError(ProbloxException):
    def __init__(self, code, message, response=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.response = response