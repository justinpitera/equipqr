from faker import Faker
from starlette.applications import Starlette

fake: Faker

def init_asgi() -> Starlette: ...
