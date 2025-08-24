from common import slugify, generate_string, generate_code_challange
import pytest

def test_slugify():
    assert slugify("Hi My App") == "hi-my-app"
    assert slugify("#my new _app") == "my-new-app"


def test_generate_string():
    assert generate_string(16).__len__() == 16
    
def test_generate_code_challange():
    code_verifier = generate_string(k=16)
    code_challange = generate_code_challange(code_verifier=code_verifier)
    print(code_challange)
    assert type(code_challange) == 'str'