from pydantic import BaseModel
from humps import camel


class ClemBotModel(BaseModel):
    """Base model which adds support for camelCase"""

    class Config:
        alias_generator = camel.case
        allow_population_by_field_name = True
