from sqlalchemy import Column, Integer, String
from app.database import Base

class NgrokURL(Base):
    __tablename__ = "ngrok_url"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
