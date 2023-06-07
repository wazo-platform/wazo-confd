from werkzeug.exceptions import HTTPException


class DHCPError(Exception):
    pass


class InvalidInterfaces(DHCPError, HTTPException):
    code = 400
    description = 'Network interfaces specified are invalid'

    def __init__(self, invalid_interfaces: list[str] = None, response=None):
        super().__init__(
            description=f'Invalid network interfaces: {", ".join(invalid_interfaces)}',
            response=response,
        )
        self.invalid_interfaces = invalid_interfaces
