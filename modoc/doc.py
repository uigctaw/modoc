import ast
import dataclasses
import inspect
import textwrap
from typing import Protocol

_INDENT = "    "


def get_doc(obj):
    if inspect.isclass(obj):
        if (
            issubclass(obj, Protocol)  # type: ignore[arg-type]
            or dataclasses.is_dataclass(obj)
        ):
            return _get_code(obj)
        return _get_class_doc(obj)
    return _get_fn_doc(obj)


def _get_class_doc(obj):
    public_attrs = [
        attr
        for attr in dir(obj)
        if not attr.startswith("_") and callable(getattr(obj, attr))
    ]

    header = _get_header_doc(obj, no_docstring_suffix="")
    body = "\n\n".join(
        _get_fn_doc(getattr(obj, attr)) for attr in public_attrs
    )
    if not body:
        return header
    return header + "\n\n" + textwrap.indent(body, prefix=_INDENT)


def _get_code(obj):
    return textwrap.dedent(inspect.getsource(obj)).strip()


def _get_fn_doc(obj):
    return _get_header_doc(obj, no_docstring_suffix="\n" + _INDENT + "...")


def _get_header_doc(obj, *, no_docstring_suffix):
    code = _get_code(obj)
    (thing,) = ast.parse(code).body
    code_lines = code.splitlines()
    first_body_thing = thing.body[0]  # type: ignore[attr-defined]
    if obj.__doc__:
        doclines = len(obj.__doc__.splitlines())
        suffix = ""
    else:
        doclines = 0
        suffix = no_docstring_suffix
    end_lineno = first_body_thing.lineno - 1 + doclines
    if inspect.isclass(obj) and getattr(
        first_body_thing,
        "decorator_list",
        [],
    ):
        dec_start = min(d.lineno for d in first_body_thing.decorator_list)
        end_lineno = dec_start - 1 + doclines
    signature_lines = code_lines[:end_lineno]
    signature = "\n".join(signature_lines)
    return signature + suffix
