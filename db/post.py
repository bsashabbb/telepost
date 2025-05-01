from sqlalchemy import Column, Integer, String, Text
from . import Base

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, index=True)
    author = Column(String)
    title = Column(String)
    content = Column(Text)
