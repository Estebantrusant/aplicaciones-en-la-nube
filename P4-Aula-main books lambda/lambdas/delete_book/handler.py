import json
from botocore.exceptions import ClientError
from shared.utils.middleware import api_gateway_wrapper
from shared.db.dynamodb_db import DynamoDBDatabase

# Inicialización de la DB fuera del handler
try:
    db = DynamoDBDatabase()
except ClientError as e:
    print(f"Error inicializando DB: {e}")
    db = None

# Aplicamos el decorador que se encargará de TRY/EXCEPT y la respuesta HTTP
@api_gateway_wrapper
def handler(event, context):
    
    # 1. Manejo del error de inicialización de DB (caso especial)
    if db is None:
        raise ClientError({'Error': {'Code': 'ServiceUnavailable', 'Message': 'Base de datos no inicializada.'}}, 'DeleteBook')

    # 2. Obtener el ID de la ruta
    # Si 'pathParameters' o 'book_id' faltan, el decorador capturará el KeyError
    book_id = event['pathParameters']['book_id']
    
    # 3. Lógica de borrado
    deleted = db.delete_book(book_id)
    
    # 4. Manejo de 'No encontrado' (Error de Negocio Específico)
    if not deleted:
        from shared.utils.response import create_response
        return create_response(
            status_code=404,
            body={'error': f"Libro con ID {book_id} no encontrado para borrar."},
            is_error=True
        )

    # 5. Retorno de Éxito (204 No Content)
    # El middleware crea la respuesta 204 incluyendo solo las cabeceras CORS.
    return 204, None 