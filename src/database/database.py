import os
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import registry, Session
from datetime import date
from datetime import datetime
from src.database.models import AbstractModel, UserModel, RouletteGamesModel, RouletteBetModel, RouletteBetTypeModel
import random
from time import sleep

from src.schemas.schemas import BetHistory

RED_NUMBERS = [1, 3 ,5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13 ,15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

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
        try:
            res = self.session.execute(select(UserModel).where(UserModel.login == login))
            user = res.scalar()
            self.session.commit()
            return user
        except:
            self.session.rollback()
            return self.get_user(login)

    def change_user_cash(self, login, delta):
        try:
            user = self.get_user(login)
            user.cash += delta
            self.session.commit()
            return True
        except:
            self.session.rollback()
            return False

    # ROULETTE METHODS
    def create_roulette_game(self):
        self._make_payments_last_roulette()
        number = random.randint(0, 36)
        current_data = date.today()
        current_time = datetime.now().strftime("%H:%M:%S")
        roulette_game = RouletteGamesModel(number=number, cashongreen=0, cashonblack=0, cashonred=0, data=current_data, createtime=current_time)
        self.session.add(roulette_game)
        self.session.commit()

    def get_roulette_game(self):
        try:
            res = self.session.execute(select(RouletteGamesModel.id).order_by(RouletteGamesModel.id.desc()))
            id = res.scalar()
            res = self.session.execute(select(RouletteGamesModel).where(RouletteGamesModel.id == id))
            game = res.scalar()
            self.session.commit()
            return game
        except:
            sleep(2)
            return self.get_roulette_game()

    def create_roulette_bet(self, login, cash, bet_type, game_id):
        bet = RouletteBetModel(login=login, bet=cash, gameid=game_id, bettype=bet_type, )
        self.session.add(bet)
        self.session.commit()

    def _make_payments_last_roulette(self):
        last_game = self.get_roulette_game()
        bets = self.session.execute(select(RouletteBetModel.login, RouletteBetModel.bet, RouletteBetModel.bettype)
                                    .where(RouletteBetModel.gameid == last_game.id))
        bets = list(bets.fetchall())
        for bet in bets:
            print(bet)
            is_win_x2 = (bet.bettype == "red" and last_game.number in RED_NUMBERS) or\
                     (bet.bettype == "black" and last_game.number in BLACK_NUMBERS)
            is_win_x35 = bet.bettype == "green" and last_game.number == 0
            if is_win_x2:
                self.change_user_cash(login=bet.login, delta=bet.bet * 2)
            elif is_win_x35:
                self.change_user_cash(login=bet.login, delta=bet.bet * 35)

    def get_bet_history(self, login):
        # try:
        res = self.session.execute(select(RouletteBetModel.bet, RouletteBetModel.bettype, RouletteBetModel.gameid, RouletteBetModel.id)
                                   .where(RouletteBetModel.login == login).order_by(RouletteBetModel.id.desc()).limit(50))
        bets = list(res.fetchall())
        # bets.reverse()
        betHistory = []
        for bet in bets:
            res = self.session.execute(select(RouletteGamesModel).where(RouletteGamesModel.id == bet.gameid))
            game = res.scalar()
            is_win_x2 = (bet.bettype == "red" and game.number in RED_NUMBERS) or \
                        (bet.bettype == "black" and game.number in BLACK_NUMBERS)
            is_win_x35 = bet.bettype == "green" and game.number == 0
            if is_win_x2:
                gain = bet.bet
            elif is_win_x35:
                gain = bet.bet * 34
            else:
                gain = -bet.bet
            betHistory.append(BetHistory(bet=bet.bet, gain=gain, game="roulette"))
        self.session.commit()
        return betHistory
        # except:
            # self.session.rollback()
            # return self.get_bet_history(login)

