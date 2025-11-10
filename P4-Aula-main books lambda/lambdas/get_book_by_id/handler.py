import json
import os
from botocore.exceptions import ClientError
from shared.utils.middleware import api_gateway_wrapper
from shared.db.dynamodb_db import DynamoDBDatabase

# Inicialización de la DB fuera del handler
try:
    db = DynamoDBDatabase()
except ClientError as e:
    print(f"Error inicializando DB: {e}")
    db = None

# Aplicamos el decorador que se encargará de:
# 1. Manejar KeyError (si falta pathParameters o book_id) -> 400 Bad Request.
# 2. Manejar ClientError (problemas de DynamoDB) -> 500 Internal Error.
# 3. Construir la respuesta final con CORS y Content-Type.
@api_gateway_wrapper
def handler(event, context):
    
    # 1. Manejo del error de inicialización de DB (caso especial)
    if db is None:
        raise ClientError({'Error': {'Code': 'ServiceUnavailable', 'Message': 'Base de datos no inicializada.'}}, 'GetBookById')

    # 2. Obtener el ID de la ruta
    book_id = event['pathParameters']['book_id']
    
    # 3. Lógica de lectura por ID
    book = db.get_book(book_id)

    # 4. Manejo de 'No encontrado' (Error de Negocio Específico)
    if book is None:
        return 404, {'error': f"Libro con ID {book_id} no encontrado."}
    
    # 5. Retorno de Éxito (200 OK)
    return 200, book.model_dump()