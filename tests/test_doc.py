import abc
import textwrap
from dataclasses import dataclass, field
from typing import Protocol

from modoc import get_doc


def _assert_doc(actual, indented_expected):
    expected = textwrap.dedent(indented_expected).strip()

    actual_lines = actual.splitlines()
    expected_lines = expected.splitlines()
    for i in range(max(len(actual_lines), len(expected_lines))):
        if i == len(actual_lines):
            raise AssertionError(f"Missing line: {expected_lines[i]}")
        if i == len(expected_lines):
            raise AssertionError(f"Unexpected line: {actual_lines[i]}")
        actual_line = actual_lines[i]
        expected_line = expected_lines[i]
        if actual_line != expected_line:
            raise AssertionError(
                f"Expected:\n{expected_line}\nGot:\n{actual_line}",
            )


def test_no_arg_function():
    def my_fn():
        pass

    doc = get_doc(my_fn)

    _assert_doc(
        doc,
        """
            def my_fn():
                ...
        """,
    )


def test_function_with_many_args():
    def myfn(
        a,
        /,
        b: int,
        c=5,
        d: str = "hi",
        *e: str,
        f,
        g: bool,
        h=1,
        i: float = 3.1,
        **j: bytes,
    ) -> tuple[int, float]:
        """And even a doc.

        Multiline, actually!
        """
        return (1, 2.0)

    doc = get_doc(myfn)

    _assert_doc(
        doc,
        '''
            def myfn(
                a,
                /,
                b: int,
                c=5,
                d: str = "hi",
                *e: str,
                f,
                g: bool,
                h=1,
                i: float = 3.1,
                **j: bytes,
            ) -> tuple[int, float]:
                """And even a doc.

                Multiline, actually!
                """
        ''',
    )


def test_function_with_kw_only_but_no_varargs():
    def hi_fn(
        foo,
        *,
        bar,
        baz: int,
        qux=5,
        quux: str = "doh!",
        **kwargs,
    ):
        pass

    doc = get_doc(hi_fn)

    _assert_doc(
        doc,
        """
            def hi_fn(
                foo,
                *,
                bar,
                baz: int,
                qux=5,
                quux: str = "doh!",
                **kwargs,
            ):
                ...
        """,
    )


def test_custom_types():
    class Hi:
        def __init__(self, x):
            self._x = x

        def __repr__(self):
            return f"Hi(x={self._x})"

    class Hello:
        pass

    def my_fn(a: Hi = Hi(x=5)) -> Hello:
        return Hello()

    doc = get_doc(my_fn)

    _assert_doc(
        doc,
        """
            def my_fn(a: Hi = Hi(x=5)) -> Hello:
                ...
        """,
    )


def test_protocol_doc():
    class MyProto(Protocol):
        def __call__(self, foo) -> int:
            pass

        def hi(self):
            """Greet everyone."""

        def bye(self):
            """Say bye.

            To everyone.
            """

    doc = get_doc(MyProto)

    _assert_doc(
        doc,
        '''
            class MyProto(Protocol):
                def __call__(self, foo) -> int:
                    pass

                def hi(self):
                    """Greet everyone."""

                def bye(self):
                    """Say bye.

                    To everyone.
                    """
        ''',
    )


def test_dataclass():
    @dataclass(frozen=True, kw_only=True, slots=True)
    class MyData:
        hi: int
        hello: str = "10"
        bye: list = field(default_factory=list)

    doc = get_doc(MyData)

    _assert_doc(
        doc,
        """
            @dataclass(frozen=True, kw_only=True, slots=True)
            class MyData:
                hi: int
                hello: str = "10"
                bye: list = field(default_factory=list)
        """,
    )


def test_class_doc():
    class MyClass(abc.ABC):
        def __init__(self):
            self._should_i_give_all_the_code = False

        @abc.abstractmethod
        def could_be_excessive(self):
            print("We'll see!")  # noqa: T201

    doc = get_doc(MyClass)

    _assert_doc(
        doc,
        """
            class MyClass(abc.ABC):

                @abc.abstractmethod
                def could_be_excessive(self):
                    ...
        """,
    )


def test_class_with_non_abstract_methods():
    class MyClass(abc.ABC):
        def __init__(self):
            self._should_i_give_all_the_code = False

        @abc.abstractmethod
        def could_be_excessive(self):
            """Hmmm..."""

        def _this_should_not_show(self):
            """Because it's protected."""
            return 1 + 2

        def this_should_show(self):
            """Because it's a public method.

            Ok?
            """
            _ = "But not the whole body!"

    doc = get_doc(MyClass)

    _assert_doc(
        doc,
        '''
            class MyClass(abc.ABC):

                @abc.abstractmethod
                def could_be_excessive(self):
                    """Hmmm..."""

                def this_should_show(self):
                    """Because it's a public method.

                    Ok?
                    """
        ''',
    )
