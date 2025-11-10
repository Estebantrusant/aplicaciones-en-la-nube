import json
import os
from shared.utils.middleware import api_gateway_wrapper 
from shared.models.book import Book 
from shared.db.dynamodb_db import DynamoDBDatabase
from botocore.exceptions import ClientError 

# Inicialización de la DB fuera del handler para reutilizar la conexión
try:
    db = DynamoDBDatabase()
except ClientError as e:
    print(f"Error inicializando DB: {e}")
    db = None

# Aplicamos el decorador que maneja TRY/EXCEPT y las respuestas
@api_gateway_wrapper
def handler(event, context):
    
    # Manejo del error de inicialización de DB (caso especial, fuera del decorador)
    if db is None:
        raise Exception("Base de datos no inicializada. Revisa la variable de entorno DB_DYNAMONAME.")
        
    data = json.loads(event.get('body', '{}')) 
    book = Book(**data) # La validación de Pydantic aquí será capturada por el decorador
    
    created = db.create_book(book) 
    
    # Simplemente retorna el status code y el cuerpo (dict)
    return 201, created.model_dump()
