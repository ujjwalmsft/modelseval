import azure.functions as func
import json
 
def main(req: func.HttpRequest, connectionInfo: dict) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(connectionInfo),
        mimetype="application/json",
        status_code=200
    )