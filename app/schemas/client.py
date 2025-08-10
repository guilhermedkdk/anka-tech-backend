from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.db.models import ClientStatus


# Classe base — campos comuns de entrada/saída
class ClientBase(BaseModel):
    name: str
    email: EmailStr
    status: Optional[ClientStatus] = ClientStatus.active


# Schema de criação — herda da base, mas não inclui campos do banco como id ou created_at
class ClientCreate(ClientBase):
    pass


# Schema de atualização — todos os campos opcionais (para PATCH/PUT)
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[ClientStatus] = None


# Schema de leitura (resposta) — inclui campos gerados pelo banco
class ClientRead(ClientBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
