import datetime
import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import as_declarative, mapped_column, Mapped

from src.schemas.schemas import User


@as_declarative()
class AbstractModel:
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)


class UserModel(AbstractModel):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=False)
    login: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    cash: Mapped[int] = mapped_column()
    verify: Mapped[bool] = mapped_column()

    def to_schema(self):
        return User(login=self.login, email=self.email, cash=self.cash, verify=self.verify)


class RouletteGamesModel(AbstractModel):
    __tablename__ = 'roulettegames'
    number: Mapped[int] = mapped_column()
    cashongreen: Mapped[int] = mapped_column()
    cashonblack: Mapped[int] = mapped_column()
    cashonred: Mapped[int] = mapped_column()
    data: Mapped[datetime.datetime] = mapped_column()
    createtime: Mapped[datetime.time] = mapped_column()


@as_declarative()
class RouletteBetTypeModel:
    __tablename__ = 'roulettebettype'
    type: Mapped[str] = mapped_column(primary_key=True)


class RouletteBetModel(AbstractModel):
    __tablename__ = 'roulettebet'
    login: Mapped[str] = mapped_column(ForeignKey('users.login'))
    bet: Mapped[int] = mapped_column()
    bettype: Mapped[str] = mapped_column(ForeignKey(RouletteBetTypeModel.type), )
    gameid: Mapped[int] = mapped_column()


class PromotionalCodeModel(AbstractModel):
    __tablename__ = "promotionalcode"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=False)
    code: Mapped[str] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(ForeignKey('users.login'))
    coefficient: Mapped[float] = mapped_column()