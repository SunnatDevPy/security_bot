from sqlalchemy import BIGINT, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import CreateModel


class User(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=True)
    flud: Mapped[bool] = mapped_column(default=False)
    ban: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    count: Mapped[int] = mapped_column(default=0)


class Words(CreateModel):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    text: Mapped[str] = mapped_column(String)
