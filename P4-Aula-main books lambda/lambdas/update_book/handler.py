import json
from botocore.exceptions import ClientError
from shared.utils.middleware import api_gateway_wrapper
from shared.models.book import Book 
from shared.db.dynamodb_db import DynamoDBDatabase

# Inicialización de la DB fuera del handler
try:
    db = DynamoDBDatabase()
except ClientError as e:
    print(f"Error inicializando DB: {e}")
    db = None

# Aplicamos el decorador que se encarga de:
# - Capturar JSONDecodeError si el cuerpo es inválido.
# - Capturar KeyError si falta 'book_id'.
# - Capturar ValidationError si Book(**data) falla.
# - Capturar ClientError si DynamoDB falla.
@api_gateway_wrapper
def handler(event, context):
    
    # 1. Manejo del error de inicialización de DB (caso especial)
    if db is None:
        raise ClientError({'Error': {'Code': 'ServiceUnavailable', 'Message': 'Base de datos no inicializada.'}}, 'UpdateBook')

    # 2. Obtener ID de la ruta
    book_id = event['pathParameters']['book_id']
    
    # 3. Obtener y parsear el cuerpo (json.loads será capturado por el middleware si falla)
    data = json.loads(event.get('body', '{}'))
    
    # 4. Crear modelo e inyectar/forzar el ID de la ruta
    data['id'] = book_id 
    book = Book(**data)

    # 5. Lógica de actualización
    updated = db.update_book(book_id, book) 
    
    # 6. Manejo de 'No encontrado' (Error de Negocio Específico)
    if updated is None:
        return 404, {'error': f"Libro con ID {book_id} no encontrado para actualizar."}

    # 7. Retorno de Éxito (200 OK)
    return 200, updated.model_dump()