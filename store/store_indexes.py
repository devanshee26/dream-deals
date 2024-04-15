from elasticsearch_dsl import Document, Text, Integer, Keyword
from elasticsearch_dsl.connections import connections
from .models import Product

# Define a connection to Elasticsearch
connections.create_connection(hosts=['localhost'])

class ProductIndex(Document):
    name = Text()
    categories = Keyword()
    description = Text()
    price = Integer()

    class Index:
        name = 'product_index'

# Update index when Product objects are saved or deleted
@ProductIndex.doc_type
class ProductDocument(Document):
    class Meta:
        model = Product
