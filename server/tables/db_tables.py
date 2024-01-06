from typing import Any
from sqlalchemy import Float, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    ...


class NextEvent(Base):
    __tablename__ = "next_event"
    date: Mapped[Any] = mapped_column()
    location: Mapped[Any] = mapped_column(String(250))
    red_fighter: Mapped[Any] = mapped_column(String(250))
    blue_fighter: Mapped[Any] = mapped_column(String(250))
    weight_class: Mapped[Any] = mapped_column(String(250))
    title_bout: Mapped[Any] = mapped_column(String(250))
    red_sig_str_average: Mapped[Any] = mapped_column(Float)
    blue_sig_str_average: Mapped[Any] = mapped_column(Float)
    red_sig_strike_defence_average: Mapped[Any] = mapped_column(Float)
    blue_sig_strike_defence_average: Mapped[Any] = mapped_column(Float)
    red_td_average: Mapped[Any] = mapped_column(Float)
    blue_td_average: Mapped[Any] = mapped_column(Float)
    red_td_defence_average: Mapped[Any] = mapped_column(Float)
    blue_td_defence_average: Mapped[Any] = mapped_column(Float)
    red_stance: Mapped[Any] = mapped_column()
    blue_stance: Mapped[Any] = mapped_column()
    red_DOB: Mapped[Any] = mapped_column()
    blue_DOB: Mapped[Any] = mapped_column()
    red_Height: Mapped[Any] = mapped_column(Float)
    blue_Height: Mapped[Any] = mapped_column(Float)
    red_Reach: Mapped[Any] = mapped_column(Float)
    blue_Reach: Mapped[Any] = mapped_column(Float)
    red_record: Mapped[Any] = mapped_column()
    blue_record: Mapped[Any] = mapped_column()
    height_diff: Mapped[Any] = mapped_column(Float)
    reach_diff: Mapped[Any] = mapped_column(Float)
