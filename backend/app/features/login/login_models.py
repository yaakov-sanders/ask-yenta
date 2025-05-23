from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str


class NewPassword(SQLModel):
    token: str
    new_password: str
