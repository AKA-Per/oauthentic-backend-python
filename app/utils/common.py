import uuid
import re
import unidecode
import random
import string

def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def slugify(text: str) -> str:
    text_ = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '-', text_).strip("-")

def generate_string(k:int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=k))