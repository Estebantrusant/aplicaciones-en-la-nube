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

# Aplicamos el decorador que se encargará de TRY/EXCEPT y la respuesta HTTP
@api_gateway_wrapper
def handler(event, context):
    
    # 1. Manejo del error de inicialización de DB (caso especial)
    if db is None:
        raise ClientError({'Error': {'Code': 'ServiceUnavailable', 'Message': 'Base de datos no inicializada.'}}, 'GetAllBooks')

    # 2. Lógica de lectura (GET ALL)
    books_list = db.get_all_books() # Asumiendo que get_all_books devuelve una lista de objetos Book
    
    # 3. Convertir lista de modelos Pydantic a lista de diccionarios
    data = [book.model_dump() for book in books_list]
    
    # 4. Retorno de Éxito (200 OK)
    # El middleware se encarga de añadir las cabeceras CORS, Content-Type, y hacer json.dumps.
    return 200, data