import json

# 1. Definición de Cabeceras CORS (Globales)
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}

def create_response(status_code: int, body: dict = None, is_error: bool = False) -> dict:
    """
    Genera la respuesta estándar de API Gateway para Lambda.

    Args:
        status_code: El código de estado HTTP (ej: 200, 201, 400, 500).
        body: El cuerpo de la respuesta como diccionario (será convertido a JSON).
        is_error: Si es True, asegura que solo se usen los encabezados CORS.
                  Si es False (éxito), añade Content-Type: application/json.
    """
    
    headers = CORS_HEADERS.copy()

    if not is_error:
        # Para respuestas de éxito, añadimos el tipo de contenido
        headers["Content-Type"] = "application/json"
    
    # El body de la respuesta debe ser un string JSON
    body_string = json.dumps(body) if body is not None else '{}'

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": body_string
    }