import json
from functools import wraps
from botocore.exceptions import ClientError
from pydantic import ValidationError
from shared.utils.response import create_response

def api_gateway_wrapper(func):
    """
    Decorador que envuelve un handler de Lambda para manejar:
    1. Parsing del cuerpo del evento (JSON).
    2. Manejo de excepciones estandarizadas (ValidationError, ClientError).
    3. Construcción de la respuesta final de API Gateway.
    """
    
    @wraps(func)
    def wrapper(event, context):
        try:
            # 1. Ejecutar el handler principal (con su lógica de negocios)
            # La función decorada retorna (status_code, body_dict)
            status_code, response_body = func(event, context)
            
            # 2. Si todo sale bien, construir la respuesta de éxito
            return create_response(
                status_code=status_code,
                body=response_body
            )

        except ValidationError as e:
            # Manejo de errores de validación (Pydantic) -> 400 Bad Request
            return create_response(
                status_code=400,
                body={'error': 'Validation error', 'details': e.errors()},
                is_error=True
            )
        except ClientError as e:
            # Manejo de errores de AWS SDK (DynamoDB) -> 500 Internal Error
            return create_response(
                status_code=500,
                body={'error': 'DynamoDB error', 'details': e.response['Error']['Message']},
                is_error=True
            )
        except json.JSONDecodeError:
            # Manejo de error de cuerpo JSON inválido -> 400 Bad Request
            return create_response(
                status_code=400,
                body={'error': 'Invalid JSON body'},
                is_error=True
            )
        except Exception as e:
            # Manejo de cualquier otro error no capturado -> 500 Internal Server Error
            print(f"Error inesperado: {e}")
            return create_response(
                status_code=500,
                body={'error': 'Internal server error', 'details': str(e)},
                is_error=True
            )
            
    return wrapper