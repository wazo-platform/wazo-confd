from xivo.rest_api_helpers import APIException


class DeviceCorruptedError(APIException):
    def __init__(self, device_id: int):
        self.device_id = device_id
        super().__init__(
            status_code=400,
            error_id='device-corrupted',
            message=f"Device {device_id} has a corrupted configuration",
            resource='Device',
            details={
                'device_id': device_id,
            },
        )

    def __str__(self):
        return self.message
