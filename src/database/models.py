import datetime

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
        return User(login=self.login, email=self.email, password=None, cash=self.cash)


class RouletteGamesModel(AbstractModel):
    __tablename__ = 'roulettegames'
    number: Mapped[int] = mapped_column()
    cashOnGreen: Mapped[int] = mapped_column()
    cashOnBlack: Mapped[int] = mapped_column()
    cashOnRed: Mapped[int] = mapped_column()
    data: Mapped[datetime.datetime] = mapped_column()


@as_declarative()
class RouletteBetTypeModel:
    __tablename__ = 'roulettebettype'
    type: Mapped[str] = mapped_column(primary_key=True)


class RouletteBet(AbstractModel):
    __tablename__ = 'roulettebet'
    login: Mapped[str] = mapped_column(ForeignKey('users.login'))
    bet: Mapped[int] = mapped_column()
    betType: Mapped[str] = mapped_column(ForeignKey('roulettebettype.type'))
    gameId: Mapped[int] = mapped_column()

