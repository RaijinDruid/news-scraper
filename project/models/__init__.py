from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app import db

class Article(BaseModel):
    headline: str
    company_name: str
    body: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[datetime] = None

