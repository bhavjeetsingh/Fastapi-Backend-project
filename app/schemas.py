from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from fastapi_users import schemas
import uuid
class PostCreate(BaseModel):
    title: str
    content:str
class PostResponse(BaseModel):
    title:str
    content:str
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass
class UserCreate(schemas.BaseUserCreate):
    pass
class UserCreate(schemas.BaseUserCreate):
    pass
class UserUpdate(schemas.BaseUserUpdate):
    pass