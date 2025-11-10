import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
from .db import Database
from models.book import Book
import os

class DynamoDBDatabase(Database):
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table_name = os.getenv('DB_DYNAMONAME')
        self.table = self.dynamodb.Table(self.table_name)
        self.initialize()
    
    def initialize(self):
        try:
            self.table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # La tabla no existe, crearla
                print(f"Creando tabla DynamoDB '{self.table_name}'...")
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'book_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'book_id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                # Esperar a que la tabla esté activa
                table.wait_until_exists()
                
                # Actualizar referencia a la tabla
                self.table = table
            else:
                raise
    
    def create_book(self, book: Book) -> Book:
        self.table.put_item(Item=book.model_dump())
        return book
    
    def get_book(self, book_id: str) -> Optional[Book]:
        response = self.table.get_item(Key={'book_id': book_id})
        if 'Item' in response:
            return Book(**response['Item'])
        return None
    
    def get_all_books(self) -> List[Book]:
        response = self.table.scan()
        books = [Book(**item) for item in response.get('Items', [])]
        return sorted(books, key=lambda x: x.position)
    
    def update_book(self, book_id: str, book: Book) -> Optional[Book]:
        book.update_timestamp()
        book.book_id = book_id
        self.table.put_item(Item=book.model_dump())
        return book
    
    def delete_book(self, book_id: str) -> bool:
        response = self.table.delete_item(
            Key={'book_id': book_id},
            ReturnValues='ALL_OLD'
        )
        return 'Attributes' in response
