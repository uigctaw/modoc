import ast
import inspect
import textwrap

_INDENT = "    "


def get_doc(obj):
    if inspect.isclass(obj):
        return _get_code(obj)
    return _get_fn_doc(obj)


def _get_protocol_doc(obj):
    return _get_code(obj)


def _get_code(obj):
    return textwrap.dedent(inspect.getsource(obj)).strip()


def _get_fn_doc(obj):
    code = _get_code(obj)
    (thing,) = ast.parse(code).body
    code_lines = code.splitlines()
    first_body_thing = thing.body[0]  # type: ignore[attr-defined]
    if obj.__doc__:
        doclines = len(obj.__doc__.splitlines())
        suffix = ""
    else:
        doclines = 0
        suffix = "\n" + _INDENT + "..."
    signature_lines = code_lines[: first_body_thing.lineno - 1 + doclines]
    signature = "\n".join(signature_lines)
    return signature + suffix
