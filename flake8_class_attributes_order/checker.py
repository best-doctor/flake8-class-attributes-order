import ast
from typing import Generator, Tuple, List, Union, Mapping

from typing_extensions import Final

from flake8_class_attributes_order import __version__ as version


class ClassAttributesOrderChecker:
    NON_STRICT_NODE_TYPE_WEIGHTS: Final[Mapping[str, int]] = {
        'docstring': 0,
        'pass': 1,
        'meta_class': 2,
        'nested_class': 3,

        'constant': 4,
        'field': 5,
        'outer_field': 6,

        'if': 7,
        'expression': 8,

        '__new__': 9,
        '__init__': 10,
        '__post_init__': 11,
        '__str__': 12,

        'save': 13,
        'delete': 14,

        'property_method': 20,
        'private_property_method': 20,
        'static_method': 22,
        'private_static_method': 22,
        'class_method': 24,
        'private_class_method': 24,
        'method': 26,
        'magic_method': 27,
        'private_method': 27,
    }

    STRICT_NODE_TYPE_WEIGHTS: Final[Mapping[str, int]] = {
        'docstring': 0,
        'pass': 1,
        'meta_class': 2,
        'nested_class': 3,

        'constant': 4,
        'field': 5,
        'outer_field': 6,

        'if': 7,
        'expression': 8,

        '__new__': 9,
        '__init__': 10,
        '__post_init__': 11,
        '__str__': 12,

        'save': 13,
        'delete': 14,

        'property_method': 20,
        'private_property_method': 21,
        'static_method': 22,
        'private_static_method': 23,
        'class_method': 24,
        'private_class_method': 25,
        'method': 26,
        'magic_method': 27,
        'private_method': 28,
    }

    name = 'flake8-class-attributes-order'
    version = version

    use_strict_mode = False

    def __init__(self, tree, filename: str):
        self.filename = filename
        self.tree = tree

    @staticmethod
    def _get_funcdef_type(child_node) -> str:
        special_methods_names = {
            '__new__',
            '__init__',
            '__post_init__',
            '__str__',
            'save',
            'delete',
        }
        decorator_names_to_types_map = {
            'property': 'property_method',
            'cached_property': 'property_method',
            'staticmethod': 'static_method',
            'classmethod': 'class_method',

            'private_property': 'private_property_method',
            'private_cached_property': 'private_property_method',
            'private_staticmethod': 'private_static_method',
            'private_classmethod': 'private_class_method',
        }
        for decorator_info in child_node.decorator_list:
            if (
                isinstance(decorator_info, ast.Name)
                and decorator_info.id in decorator_names_to_types_map
            ):

                if child_node.name.startswith('_'):
                    return decorator_names_to_types_map[f'private_{decorator_info.id}']

                return decorator_names_to_types_map[decorator_info.id]
        if child_node.name in special_methods_names:
            return child_node.name
        if child_node.name.startswith('__') and child_node.name.endswith('__'):
            return 'magic_method'
        if child_node.name.startswith('_'):
            return 'private_method'
        return 'method'

    @staticmethod
    def _is_caps_lock_str(var_name: str) -> bool:
        return var_name.upper() == var_name

    @staticmethod
    def __get_name_for_field_node_type(node: Union[ast.Assign, ast.AnnAssign]) -> str:
        default_name = '<class_level_assignment>'
        if isinstance(node, ast.AnnAssign):
            return node.target.id if isinstance(node.target, ast.Name) else default_name
        elif isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
        elif hasattr(node.targets[0], 'attr'):
            return node.targets[0].attr  # type: ignore
        elif isinstance(node.targets[0], ast.Tuple):
            return ', '.join([e.id for e in node.targets[0].elts if isinstance(e, ast.Name)])
        else:
            return default_name

    @classmethod
    def _get_node_name(cls, node, node_type: str):
        name_getters_by_type = [
            ('docstring', lambda n: 'docstring'),
            ('meta_class', lambda n: 'Meta'),
            ('constant', lambda n: n.target.id if isinstance(n, ast.AnnAssign) else n.targets[0].id),  # type: ignore
            ('field', cls.__get_name_for_field_node_type),
            ('method', lambda n: n.name),
            ('nested_class', lambda n: n.name),
            ('expression', lambda n: '<class_level_expression>'),
            ('if', lambda n: 'if ...'),
        ]
        for type_postfix, name_getter in name_getters_by_type:
            if node_type.endswith(type_postfix):
                return name_getter(node)

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            '--use-class-attributes-order-strict-mode',
            action='store_true',
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options) -> None:
        cls.use_strict_mode = bool(options.use_class_attributes_order_strict_mode)

    @classmethod
    def _get_model_parts_info(cls, model_ast, weights: Mapping[str, int]):
        parts_info = []
        for child_node in model_ast.body:
            node_type = cls._get_model_node_type(child_node)
            parts_info.append({
                'model_name': model_ast.name,
                'node': child_node,
                'type': node_type,
                'weight': weights[node_type],
            })
        return parts_info

    @classmethod
    def _get_model_node_type(cls, child_node) -> str:
        direct_node_types_mapping = [
            (ast.If, lambda n: 'if'),
            (ast.Pass, lambda n: 'pass'),
            ((ast.Assign, ast.AnnAssign), lambda n: cls._get_assighment_type(n)),
            ((ast.FunctionDef, ast.AsyncFunctionDef), lambda n: cls._get_funcdef_type(n)),
        ]
        for type_or_type_tuple, type_getter in direct_node_types_mapping:
            if isinstance(child_node, type_or_type_tuple):  # type: ignore
                return type_getter(child_node)

        if isinstance(child_node, ast.Expr):
            if isinstance(child_node.value, ast.Str):
                return 'docstring'
            else:
                return 'expression'
        elif isinstance(child_node, ast.ClassDef):
            if child_node.name == 'Meta':
                return 'meta_class'
            else:
                return 'nested_class'

    @classmethod
    def _get_assighment_type(cls, child_node) -> str:
        assignee_node = child_node.target if isinstance(child_node, ast.AnnAssign) else child_node.targets[0]
        if isinstance(assignee_node, ast.Subscript):
            return 'expression'
        if isinstance(assignee_node, ast.Name) and cls._is_caps_lock_str(assignee_node.id):
            return 'constant'
        if isinstance(child_node.value, ast.Call):
            dump_callable = ast.dump(child_node.value.func)
            if (
                'ForeignKey' in dump_callable
                or 'ManyToManyField' in dump_callable
                or 'OneToOneField' in dump_callable
                or 'GenericRelation' in dump_callable
            ):
                return 'outer_field'
        return 'field'

    @classmethod
    def _get_ordering_errors(cls, model_parts_info) -> List[Tuple[int, int, str]]:
        errors = []
        for model_part, next_model_part in zip(model_parts_info, model_parts_info[1:] + [None]):
            if (
                next_model_part
                and model_part['model_name'] == next_model_part['model_name']
                and model_part['weight'] > next_model_part['weight']
            ):
                errors.append((
                    model_part['node'].lineno,
                    model_part['node'].col_offset,
                    'CCE001 {0}.{1} should be after {0}.{2}'.format(
                        model_part['model_name'],
                        cls._get_node_name(model_part['node'], model_part['type']),
                        cls._get_node_name(next_model_part['node'], next_model_part['type']),
                    ),
                ))
            if model_part['type'] in ['expression', 'if']:
                errors.append((
                    model_part['node'].lineno,
                    model_part['node'].col_offset,
                    'CCE002 Class level expression detected in class {0}, line {1}'.format(
                        model_part['model_name'],
                        model_part['node'].lineno,
                    ),
                ))
        return errors

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        weight_info = (
            self.STRICT_NODE_TYPE_WEIGHTS
            if ClassAttributesOrderChecker.use_strict_mode
            else self.NON_STRICT_NODE_TYPE_WEIGHTS
        )
        classes = [n for n in ast.walk(self.tree) if isinstance(n, ast.ClassDef)]
        errors: List[Tuple[int, int, str]] = []
        for class_def in classes:
            model_parts_info = self._get_model_parts_info(class_def, weight_info)
            errors += self._get_ordering_errors(model_parts_info)

        for lineno, col_offset, error_msg in errors:
            yield lineno, col_offset, error_msg, type(self)
