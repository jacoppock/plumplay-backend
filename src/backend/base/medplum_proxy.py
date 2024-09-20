import requests
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

MEDPLUM_SERVER_URL = "http://localhost:8000/"


@csrf_exempt
def proxy_medplum(request: HttpRequest, path: str) -> JsonResponse:
    url = f"{MEDPLUM_SERVER_URL}/{path}"
    method = request.method.lower()
    data = request.body if method in ["post", "put", "patch"] else None
    headers = {
        "Authorization": request.headers.get("Authorization", ""),
        "Content-Type": "application/json",
    }

    response = requests.request(method, url, headers=headers, data=data)
    return JsonResponse(response.json(), status=response.status_code)
