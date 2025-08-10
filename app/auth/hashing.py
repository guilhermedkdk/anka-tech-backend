from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return _pwd.hash(password)

def get_password_hash(password: str) -> str:
    return hash_password(password)

def verify_password(password: str, hashed: str) -> bool:
    return _pwd.verify(password, hashed)
