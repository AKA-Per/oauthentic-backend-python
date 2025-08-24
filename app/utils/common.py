import uuid
import re
import unidecode
import random
import string
import hashlib
import base64

def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def slugify(text: str) -> str:
    text_ = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '-', text_).strip("-")

def generate_string(k:int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=k))

def generate_code_challange(code_verifier: str) -> str:
    code_verifier_bytes = code_verifier.encode('utf-8')
    sha256_digest = hashlib.sha256(code_verifier_bytes).digest()
    code_challange = base64.urlsafe_b64encode(sha256_digest).rstrip(b'=').decode('utf-8')
    return code_challange