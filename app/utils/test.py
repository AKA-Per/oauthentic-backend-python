from common import generate_string, generate_code_challange

print(generate_string(32))
print(generate_string(64))


code_verifier = generate_string(k=16)
code_challange = generate_code_challange(code_verifier=code_verifier)
print(code_challange)
