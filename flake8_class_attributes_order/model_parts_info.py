import ast
from typing import Dict, Mapping, Optional, Set, Union


def get_model_parts_info(model_ast, weights: Mapping[str, int]):
    parts_info = []
    for child_node in model_ast.body:
        node_type = get_model_node_type(child_node)
        if node_type and node_type in weights:
            parts_info.append({
                'model_name': model_ast.name,
                'node': child_node,
                'type': node_type,
                'weight': weights[node_type],
            })
    return parts_info


def get_model_node_type(child_node) -> Optional[str]:
    direct_node_types_mapping = [
        (ast.If, lambda n: 'if'),
        (ast.Pass, lambda n: 'pass'),
        ((ast.Assign, ast.AnnAssign), lambda n: get_assighment_type(n)),
        ((ast.FunctionDef, ast.AsyncFunctionDef), lambda n: get_funcdef_type(n)),
        (ast.Expr, lambda n: 'docstring' if isinstance(n.value, ast.Constant) else 'expression'),
        (ast.ClassDef, lambda n: 'meta_class' if child_node.name == 'Meta' else 'nested_class'),
    ]
    for type_or_type_tuple, type_getter in direct_node_types_mapping:
        if isinstance(child_node, type_or_type_tuple):  # type: ignore
            return type_getter(child_node)


def get_assighment_type(child_node) -> str:
    assignee_node = child_node.target if isinstance(child_node, ast.AnnAssign) else child_node.targets[0]
    assighment_type = 'field'
    if isinstance(assignee_node, ast.Subscript):
        assighment_type = 'expression'
    if isinstance(assignee_node, ast.Name) and is_caps_lock_str(assignee_node.id):
        assighment_type = 'constant'
    if isinstance(child_node.value, ast.Call):
        dump_callable = ast.dump(child_node.value.func)
        if (
            'ForeignKey' in dump_callable
            or 'ManyToManyField' in dump_callable
            or 'OneToOneField' in dump_callable
            or 'GenericRelation' in dump_callable
        ):
            assighment_type = 'outer_field'
    return assighment_type


def get_funcdef_type(child_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
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
        'setter': 'property_method',
        'deleter': 'property_method',
        'staticmethod': 'static_method',
        'classmethod': 'class_method',

        'protected_property': 'protected_property_method',
        'protected_cached_property': 'protected_property_method',
        'protected_setter': 'protected_property_method',
        'protected_deleter': 'protected_property_method',
        'protected_staticmethod': 'protected_static_method',
        'protected_classmethod': 'protected_class_method',

        'private_property': 'private_property_method',
        'private_cached_property': 'private_property_method',
        'private_setter': 'private_property_method',
        'private_deleter': 'private_property_method',
        'private_staticmethod': 'private_static_method',
        'private_classmethod': 'private_class_method',
    }
    funcdef = get_funcdef_type_by_decorator_info(child_node, decorator_names_to_types_map)
    if not funcdef:
        funcdef = get_funcdef_type_by_node_name(child_node, special_methods_names)
    return funcdef


def get_funcdef_type_by_decorator_info(  # noqa: CFQ004
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    decorator_names_to_types_map: Dict[str, str],
) -> Union[str, None]:
    for decorator_info in node.decorator_list:
        if isinstance(decorator_info, ast.Name):
            decorator_id = decorator_info.id
        elif isinstance(decorator_info, ast.Attribute):
            decorator_id = decorator_info.attr
        else:
            continue

        if decorator_id in decorator_names_to_types_map:
            if node.name.startswith('__'):
                return decorator_names_to_types_map[f'private_{decorator_id}']
            if node.name.startswith('_'):
                return decorator_names_to_types_map[f'protected_{decorator_id}']
            return decorator_names_to_types_map[decorator_id]
    return None


def get_funcdef_type_by_node_name(  # noqa: CFQ004
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    special_methods_names: Set[str],
    default_type: str = 'method',
) -> str:
    if node.name in special_methods_names:
        return node.name
    if node.name.startswith('__') and node.name.endswith('__'):
        return 'magic_method'
    if node.name.startswith('__'):
        return 'private_method'
    if node.name.startswith('_'):
        return 'protected_method'
    return default_type


def is_caps_lock_str(var_name: str) -> bool:
    return var_name.upper() == var_name
