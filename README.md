# flake8-class-attributes-order

[![Build Status](https://github.com/best-doctor/flake8-class-attributes-order/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/best-doctor/flake8-class-attributes-order/actions/workflows/build.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/28b7cd9d0714ec4b93a3/maintainability)](https://codeclimate.com/github/best-doctor/flake8-class-attributes-order/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/28b7cd9d0714ec4b93a3/test_coverage)](https://codeclimate.com/github/best-doctor/flake8-class-attributes-order/test_coverage)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flake8-class-attributes-order)

An extension for flake8 to report on wrong class attributes order and
class level logic.

The validator can extract class attribute type: docstring, property,
nested class, `GLOBAL_VAR`, etc.
If django model fields are detected, the validator can detect,
if the field is link to another table (foreign key, generic key, etc)
or not.

After resolving each attribute type, validator checks attributes order.

Default configuration checks for the following order of attributes:

- `__new__`
- `__init__`
- `__post_init__`
- other magic methods
- `@property`
- `@staticmethod`
- `@classmethod`
- other methods
- protected methods
- private methods

If the order is broken, validator will report on it.

Besides methods, the validator checks other attributes methods:
docstrings, nested classes, constants, attributes, and so on.

Also validator checks, if class has no class level logic and report
if any. Here is an example:

```python
class PhoneForm(forms.Form):
    phone = forms.CharField(17, label='Телефон'.upper())

    # this should happen in __init__!
    phone.widget.attrs.update({'class': 'form-control phone'})

```

## Installation

```terminal
pip install flake8-class-attributes-order
```

## Configuration

### Strict mode

There is another preconfigured order that is more strict on private subtypes:

- `__new__`
- `__init__`
- `__post_init__`
- other magic method
- `@property`
- `@staticmethod`
- `@classmethod`
- other methods
- protected `@property`
- protected `@staticmethod`
- protected `@classmethod`
- other protected methods
- private `@property`
- private `@staticmethod`
- private `@classmethod`
- other private methods

To enable strict validation, please set the flag in your config file:

```ini
[flake8]
use_class_attributes_order_strict_mode = True
```

### Manual order configuration

Order can be manually configured via `class_attributes_order` config setting.

For example, if you prefer to put `class Meta` after constants and fields:

```ini
[flake8]
class_attributes_order =
    field,
    meta_class,
    nested_class,
    magic_method,
    property_method,
    static_method,
    class_method,
    method,
    protected_method,
    private_method
```

Configurable options:

|          Option           |              Description               | Fallbacks to\*  |
|:-------------------------:|:--------------------------------------:|:---------------:|
|        meta_class         | class Meta: (e.g. in Django projects)  |  nested_class   |
|       nested_class        |          Other nested classes          |     None\*      |
|         constant          |             SOME_CONSTANTS             |      field      |
|        outer_field        |     some = models.ForeignKey etc.      |      field      |
|           field           |              Other fields              |      None       |
|      protected field      |      Other field starting with _       |      field      |
|       private field       |      Other field starting with __      |      field      |
|         `__new__`         |               `__new__`                |  magic_method   |
|        `__init__`         |               `__init__`               |  magic_method   |
|      `__post_init__`      |            `__post_init__`             |  magic_method   |
|         `__str__`         |               `__str__`                |  magic_method   |
|       magic_method        |          Other magic methods           |     method      |
|           save            |             def save(...)              |     method      |
|          delete           |            def delete(...)             |     method      |
|      property_method      |    @property/@cached_property etc.     |     method      |
| protected_property_method | @property/@cached_property etc. with _ | property_method |
|  private_property_method  |   @property/@cached_property with __   | property_method |
|       static_method       |             @staticmethod              |     method      |
|  protected_static_method  |     @staticmethod beginning with _     |  static_method  |
|   private_static_method   |    @staticmethod beginning with __     |  static_method  |
|       class_method        |              @classmethod              |     method      |
|  protected_class_method   |     @classmethod beginning with _      |  class_method   |
|   private_class_method    |     @classmethod beginning with __     |  class_method   |
|      private_method       |    other methods beginning with __     |     method      |
|     protected_method      |     other methods beginning with _     |     method      |
|          method           |             other methods              |      None       |

\* if not provided, will use its supertype order

\*\* if not defined, such base types and all their subtypes (unless defined)
will be ignored during validation. It's recommended
to set at least `nested_class`, `field` and `method`

You choose how detailed your configuration is.
For example, you can define order of each supported magic method
(`__new__`, `__str__`, etc.), or set `magic_method`
to allow any order among them or even just use `method`

## Example

```python
DEBUG = True


class User:
    def fetch_info_from_crm(self):
        pass

    LOGIN_FIELD = 'email'  # wtf? this should be on top of class definition!


class UserNode:
    class Meta:
        model = User

    if DEBUG:  # not great idea at all
        def is_synced_with_crm(self):
            pass

```

Usage:

```terminal
$ flake8 test.py
test.py:5:5: CCE001 User.fetch_info_from_crm should be after User.LOGIN_FIELD
test.py:15:5: CCE002 Class level expression detected model UserNode, line 15
```

Tested on Python 3.7.x and flake8 3.7.5.

## Error codes

| Error code |                     Description                          |
|:----------:|:--------------------------------------------------------:|
|   CCE001   | Wrong class attributes order (`XXX should be after YYY`) |
|   CCE002   | Class level expression detected                          |

## Contributing

We would love you to contribute to our project. It's simple:

- Create an issue with bug you found or proposal you have.
  Wait for approve from maintainer.
- Create a pull request. Make sure all checks are green.
- Fix review comments if any.
- Be awesome.

Here are useful tips:

- You can run all checks and tests with `make check`. Please do it
  before TravisCI does.
- We use
  [BestDoctor python styleguide](https://github.com/best-doctor/guides/blob/master/guides/en/python_styleguide.md).
- We respect [Django CoC](https://www.djangoproject.com/conduct/).
  Make soft, not bullshit.
