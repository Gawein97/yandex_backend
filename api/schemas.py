import json
import re
from datetime import datetime

from aiohttp import web
from marshmallow import (
    Schema, fields, validate, post_dump, pre_load, validates_schema,
    ValidationError, RAISE
)


class CitizenSchema(Schema):
    citizen_id = fields.Integer(validate=lambda x: x >= 0, required=True)
    town = fields.String(validate=lambda x: bool(re.search(r'\w', x)), required=True)
    street = fields.String(validate=lambda x: bool(re.search(r'\w', x)), required=True)
    building = fields.String(validate=lambda x: bool(re.search(r'\w', x)), required=True)
    apartment = fields.Integer(validate=lambda x: x >= 0, required=True)
    name = fields.String(required=True)
    birth_date = fields.Date(required=True)
    gender = fields.String(validate=validate.OneOf(['male', 'female']), required=True)
    relatives = fields.List(fields.Integer(), validate=lambda x: len(set(x)) == len(x), required=True)

    @pre_load
    def load_date(self, in_data, **kwargs):
        if 'birth_date' not in in_data:
            return in_data
        try:
            in_data['birth_date'] = datetime.strptime(in_data['birth_date'], '%d.%m.%Y').date().isoformat()
        except ValueError:
            raise ValidationError('Date are incorrect')
        return in_data

    @post_dump
    def get_relatives(self, in_data, **kwargs):
        in_data['relatives'] = list(filter(None, in_data['relatives']))
        return in_data

    @post_dump
    def process_date(self, in_data, **kwargs):
        in_data['birth_date'] = datetime.strptime(in_data['birth_date'], '%Y-%m-%d').strftime('%d.%m.%Y')
        return in_data

    @validates_schema(pass_many=True, skip_on_field_errors=True)
    def check_unique_citizen_id(self, data, **kwargs):
        """Проверяем что id пользователя в импорте уникален."""
        if type(data) != list:
            return

        if len({i['citizen_id'] for i in data}) != len(data):
            raise ValidationError('Citizen must be unic')

    @validates_schema(pass_many=True, skip_on_field_errors=True)
    def check_user_not_in_relatives(self, data, **kwargs):
        """Проверяет нет ли пользователя в массвие родственников"""
        if type(data) != list:
            return
        citizens_dict = {i['citizen_id']: set(i['relatives']) for i in data}
        for citizen_id, relatives in citizens_dict.items():
            if citizen_id in relatives:
                raise ValidationError('Citizen can\'t be relative to themself')
            for relative in relatives:
                if relative not in citizens_dict:
                    raise ValidationError('Relative doesn\'t exist')
                if citizen_id not in citizens_dict[relative]:
                    raise ValidationError('Broken relatives connect')

    class Meta:
        unknown = RAISE


class ImportsSchema(Schema):
    citizens = fields.Nested(CitizenSchema, many=True, required=True)

    class Meta:
        unknown = RAISE


# Кастомный обработчик ошибок для aiohttp-apispec

def my_error_handler(
        error: ValidationError,
        req: web.Request,
        schema: Schema,
        error_status_code=400,
        error_headers=None,
):
    """Кастомный api-spec обработчик ошибок"""
    raise web.HTTPBadRequest(
        body=json.dumps(error.messages),
        headers=error_headers,
        content_type='application/json',
    )
