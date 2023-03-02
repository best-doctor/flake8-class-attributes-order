import ast
from typing import Generator, Tuple, List

from flake8_class_attributes_order import __version__ as version
from flake8_class_attributes_order.node_type_weights import get_node_weights
from flake8_class_attributes_order.model_parts_info import get_model_parts_info
from flake8_class_attributes_order.ordering_errors import get_ordering_errors


class ClassAttributesOrderChecker:

    name = 'flake8-class-attributes-order'
    version = version
    options = None

    def __init__(self, tree, filename: str):
        self.filename = filename
        self.tree = tree

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
        parser.add_option(
            '--ignore-docstring',
            action='store_true',
            parse_from_config=True,
            help='Ignore docstring errors whenever they appear',
        )

    @classmethod
    def parse_options(cls, options: str) -> None:
        cls.options = options

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        weight_info = get_node_weights(self.options)
        classes = [n for n in ast.walk(self.tree) if isinstance(n, ast.ClassDef)]
        errors: List[Tuple[int, int, str]] = []

        for class_def in classes:
            model_parts_info = get_model_parts_info(class_def, weight_info)
            errors += get_ordering_errors(model_parts_info)

        for lineno, col_offset, error_msg in errors:
            yield lineno, col_offset, error_msg, type(self)
