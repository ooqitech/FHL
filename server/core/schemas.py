import coreapi
import django.utils.six.moves.urllib.parse as urlparse
import yaml
from rest_framework.schemas import AutoSchema

MEDIA_TYPES = {
    'json': 'application/json',
    'form-urlencoded': 'application/x-www-form-urlencoded',
    'multipart': 'multipart/form-data',
    'bin': 'application/octet-stream'
}


class CustomSchema(AutoSchema):
    def get_link(self, path, method, base_url):

        view = self.view
        method_name = getattr(view, 'action', method.lower())
        method_docstring = getattr(view, method_name, None).__doc__
        _method_desc = ''
        _encoding = None

        fields = self.get_path_fields(path, method)

        if not method_docstring:
            return super().get_link(path, method, base_url)
        else:
            yaml_doc = None
            if method_docstring:
                try:
                    yaml_doc = yaml.safe_load(method_docstring)
                except yaml.error.MarkedYAMLError:
                    yaml_doc = None

            # Extract schema information from yaml

            if yaml_doc and type(yaml_doc) != str:
                _desc = yaml_doc.get('desc', '')
                _ret = yaml_doc.get('ret', '')
                _err = yaml_doc.get('err', '')
                _encoding = yaml_doc.get('encoding', None)
                _method_desc = _desc
                if _ret:
                    _method_desc += '\n<br/>' + 'return: ' + _ret
                if _err:
                    _method_desc += '<br/>' + 'error: ' + _err
                params = yaml_doc.get('input', [])

                for i in params:
                    _name = i.get('name')
                    _desc = i.get('desc')
                    _required = i.get('required', False)
                    _type = i.get('type', 'string')
                    _location = i.get('location', 'form')
                    field = coreapi.Field(
                        name=_name,
                        location=_location,
                        required=_required,
                        description=_desc,
                        type=_type
                    )
                    fields.append(field)
            else:
                _method_desc = method_docstring
                fields += self.get_serializer_fields(path, method)

        fields += self.get_pagination_fields(path, method)
        fields += self.get_filter_fields(path, method)

        manual_fields = self.get_manual_fields(path, method)
        fields = self.update_fields(fields, manual_fields)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method)
        else:
            encoding = None

        if _encoding:
            encoding = MEDIA_TYPES.get(_encoding, _encoding)

        if base_url and path.startswith('/'):
            path = path[1:]

        return coreapi.Link(
            url=urlparse.urljoin(base_url, path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=_method_desc
        )
