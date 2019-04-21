# flake8-class-attributes-order

[![Build Status](https://travis-ci.org/best-doctor/flake8-class-attributes-order.svg?branch=master)](https://travis-ci.org/best-doctor/flake8-class-attributes-order)
[![Maintainability](https://api.codeclimate.com/v1/badges/28b7cd9d0714ec4b93a3/maintainability)](https://codeclimate.com/github/best-doctor/flake8-class-attributes-order/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/28b7cd9d0714ec4b93a3/test_coverage)](https://codeclimate.com/github/best-doctor/flake8-class-attributes-order/test_coverage)


An extension for flake8 to report on wrong class attributes order and class level logic.

The validator can extract class attribute type: docstring, property, nested class,
`GLOBAL_VAR`, etc.
If django model fields are detected, the validator can detect,
if the field is link to another table (foreign key, generic key, etc) or not.

After resolving each attribute type, validator checks attributes order.
For example, here are default methods order: `__init__`, `__str__`, `save`, `delete`, `@property`,
`@staticmethod`, `@classmethod`, other methods, underscored methods.
If the order is broken, validator will report on it.

Besides methods, the validator checks other attributes methods: docstrings, nested classes,
constants, attributes, and so on.

Also validator checks, if class has no class level logic and report if any. Here is an example:

```python
class PhoneForm(forms.Form):
    phone = forms.CharField(17, label='Телефон'.upper())
    phone.widget.attrs.update({'class': 'form-control phone'})  # this should happens in __init__!

```


## Installation

    pip install flake8-class-attributes-order


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

Tested on Python 3.6 and 3.7.2 and flake8 3.7.5.


## Error codes

| Error code |                     Description                          |
|:----------:|:--------------------------------------------------------:|
|   CCE001   | Wrong class attributes order (`XXX should be after YYY`) |
|   CCE002   | Class level expression detected                          |


## Contributing

We would love you to contribute to our project. It's simple:

1. Create an issue with bug you found or proposal you have. Wait for approve from maintainer.
2. Create a pull request. Make sure all checks are green.
3. Fix review comments if any.
4. Be awesome.

Here are useful tips:

- You can run all checks and tests with `make check`. Please do it before TravisCI does.
- We use [BestDoctor python styleguide](https://github.com/best-doctor/guides/blob/master/guides/python_styleguide.md). Sorry, styleguide is available only in Russian for now.
- We respect [Django CoC](https://www.djangoproject.com/conduct/). Make soft, not bullshit.
