import logging
from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from dotenv import load_dotenv

from src.api.api import schema

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(name)s:%(levelname)s: %(message)s"
)

app = GraphQL(schema, websocket_handler=GraphQLTransportWSHandler(), debug=True)
