from app.schemas.common import APIResponse


def api_response(message: str, data=None, success: bool = True) -> APIResponse:
    return APIResponse(success=success, message=message, data=data)
