import ast
from typing import Generator, Tuple, List, Union, Mapping


from flake8_class_attributes_order import __version__ as version
from flake8_class_attributes_order.node_type_weights import ClassNodeTypeWeights


class ClassAttributesOrderChecker:

    name = 'flake8-class-attributes-order'
    version = version

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

        special_methods_names = (
            '__new__',
            '__init__',
            '__post_init__',
            '__str__',
            'save',
            'delete',
        )
        name_getters_by_type = [
            ('docstring', lambda n: 'docstring'),
            ('meta_class', lambda n: 'Meta'),
            ('constant', lambda n: n.target.id if isinstance(n, ast.AnnAssign) else n.targets[0].id),  # type: ignore
            ('field', cls.__get_name_for_field_node_type),
            (('method',) + special_methods_names, lambda n: n.name),
            ('nested_class', lambda n: n.name),
            ('expression', lambda n: '<class_level_expression>'),
            ('if', lambda n: 'if ...'),
        ]
        for type_postfix, name_getter in name_getters_by_type:
            if node_type.endswith(type_postfix):  # type: ignore
                return name_getter(node)

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            '--use-class-attributes-order-strict-mode',
            action='store_true',
            parse_from_config=True,
            help='Require more strict order of private class members',
        )
        parser.add_option(
            '--class-attributes-order',
            comma_separated_list=True,
            parse_from_config=True,
            help='Comma-separated list of class attributes to '
                 'configure order manually',
        )

    @classmethod
    def _get_model_parts_info(cls, model_ast, weights: Mapping[str, int]):
        parts_info = []
        for child_node in model_ast.body:
            node_type = cls._get_model_node_type(child_node)
            if node_type in weights:
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
            (ast.Expr, lambda n: 'docstring' if isinstance(n.value, ast.Str) else 'expression'),
            (ast.ClassDef, lambda n: 'meta_class' if child_node.name == 'Meta' else 'nested_class'),
        ]
        for type_or_type_tuple, type_getter in direct_node_types_mapping:
            if isinstance(child_node, type_or_type_tuple):  # type: ignore
                return type_getter(child_node)

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

    def run(self, options) -> Generator[Tuple[int, int, str, type], None, None]:
        weight_info = ClassNodeTypeWeights.get_node_weights(options)
        classes = [n for n in ast.walk(self.tree) if isinstance(n, ast.ClassDef)]
        errors: List[Tuple[int, int, str]] = []
        for class_def in classes:
            model_parts_info = self._get_model_parts_info(class_def, weight_info)
            errors += self._get_ordering_errors(model_parts_info)

        for lineno, col_offset, error_msg in errors:
            yield lineno, col_offset, error_msg, type(self)
