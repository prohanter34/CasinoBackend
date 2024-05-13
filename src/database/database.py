import os

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import registry, Session

from src.database.models import AbstractModel, UserModel


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
        res = self.session.execute(select(UserModel.id).order_by(UserModel.id))
        id = res.scalar()
        print(id)
        if id:
            user = UserModel(id=(id + 1), login=login, email=email, password=password, cash=0, verify=False)
        else:
            user = UserModel(id=(1), login=login, email=email, password=password, cash=0, verify=False)
        self.session.add(user)
        self.session.commit()

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
        user = self.get_user(login)
        # with self.session.begin():
            # self.session.
        cash = 0
        pass
