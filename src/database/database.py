import os
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import registry, Session
from datetime import date
from datetime import datetime
from src.database.models import AbstractModel, UserModel, RouletteGamesModel, RouletteBetModel, RouletteBetTypeModel
import random


class Database:
    def __init__(self, URL):
        if "DB_PATH" in os.environ:
            self.URL = os.environ["DB_PATH"]
        self.URL = URL
        self.engine = create_engine(self.URL, echo=False)
        self.mapped_registry = registry()
        self.session = Session(self.engine)
        with self.session.begin():
            AbstractModel.metadata.create_all(self.engine)

    def add_user(self, login, email, password, ):
        res = self.session.execute(select(UserModel.id).order_by(UserModel.id.desc()))
        id = res.scalar()
        print(id)
        if id:
            user = UserModel(id=(id + 1), login=login, email=email, password=password, cash=0, verify=False)
        else:
            user = UserModel(id=(1), login=login, email=email, password=password, cash=0, verify=False)
        self.session.add(user)
        self.session.commit()

    # todo refactor (can use get_user)
    def check_email(self, email):
        res = self.session.execute(select(UserModel).where(UserModel.email == email))
        user = res.scalar()
        if not user:
            return True
        else:
            return False

    def verify_email(self, email):
        res = self.session.execute(select(UserModel).where(UserModel.email == email))
        user = res.scalar()
        user.verify = True
        self.session.commit()

    def get_user(self, login):
        res = self.session.execute(select(UserModel).where(UserModel.login == login))
        user = res.scalar()
        return user

    def change_user_cash(self, login, delta):
        try:
            user = self.get_user(login)
            user.cash += delta
            self.session.commit()
            return True
        except:
            return False

    # ROULETTE METHODS
    def create_roulette_game(self):
        number = random.randint(0, 36)
        current_data = date.today()
        current_time = datetime.now().strftime("%H:%M:%S")
        roulette_game = RouletteGamesModel(number=number, cashongreen=0, cashonblack=0, cashonred=0, data=current_data, createtime=current_time)
        self.session.add(roulette_game)
        self.session.commit()

    def get_roulette_game(self):
        res = self.session.execute(select(RouletteGamesModel.id).order_by(RouletteGamesModel.id.desc()))
        id = res.scalar()
        res = self.session.execute(select(RouletteGamesModel).where(RouletteGamesModel.id == id))
        game = res.scalar()
        return game

    def create_roulette_bet(self, login, cash, bet_type, game_id):
        bet = RouletteBetModel(login=login, bet=cash, gameid=game_id, bettype=bet_type, )
        self.session.add(bet)
        self.session.commit()

    # def get_roulette_bet(self, ):

