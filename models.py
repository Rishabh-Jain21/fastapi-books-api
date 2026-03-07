from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String,Boolean
from database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    author: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    is_deleted:Mapped[bool]=mapped_column(Boolean,default=False)