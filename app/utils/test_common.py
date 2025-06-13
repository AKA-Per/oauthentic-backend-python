from common import slugify, generate_string
import pytest

def test_slugify():
    assert slugify("Hi My App") == "hi-my-app"
    assert slugify("#my new _app") == "my-new-app"


def test_generate_string():
    assert generate_string(16).__len__() == 16 