import ast
import os
from argparse import Namespace

from flake8_class_attributes_order.checker import ClassAttributesOrderChecker


def run_validator_for_test_file(filename, max_annotations_complexity=None,
                                strict_mode=False, attributes_order=None):
    test_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'test_files',
        filename,
    )
    with open(test_file_path, 'r') as file_handler:
        raw_content = file_handler.read()
    tree = ast.parse(raw_content)

    options = Namespace()
    options.use_class_attributes_order_strict_mode = strict_mode
    options.class_attributes_order = attributes_order
    ClassAttributesOrderChecker.parse_options(options)

    checker = ClassAttributesOrderChecker(tree=tree, filename=filename)
    if max_annotations_complexity:
        checker.max_annotations_complexity = max_annotations_complexity

    return list(checker.run())
