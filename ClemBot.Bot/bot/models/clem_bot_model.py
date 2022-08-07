from humps import camel
from pydantic import BaseModel


class ClemBotModel(BaseModel):
    """Base model which adds support for camelCase"""

    class Config:
        alias_generator = camel.case
        allow_population_by_field_name = True
        use_enum_values = True
