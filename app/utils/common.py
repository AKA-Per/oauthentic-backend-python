import uuid
def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())