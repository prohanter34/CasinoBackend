

CREATE DATABASE casino;

\c casino

CREATE TABLE users (
    id serial,
    login VARCHAR(20) PRIMARY KEY NOT NULL,
    email VARCHAR(50) UNIQUE,
    password VARCHAR(50) NOT NULL,
    cash INTEGER DEFAULT 0 CHECK (cash >= 0),
    verify boolean DEFAULT FALSE
);

CREATE TABLE rouletteGames (
    id serial PRIMARY KEY,
    number INTEGER NOT NULL,
    cashOnGreen INTEGER NOT NULL CHECK (cashOnGreen >= 0),
    cashOnGreen INTEGER NOT NULL CHECK (cashOnRed >= 0),
    cashOnBlack INTEGER NOT NULL CHECK (cashOnBlack >= 0),
    data date DEFAULT current_date NOT NULL,
    createTime time DEFAULT current_time NOT NULL
);

INSERT INTO rouletteGames (number, cashOnGreen, cashOnRed, cashOnBlack, data, createTime) VALUES(0, 0, 0, 0, '27-05-2024', '00:00:00');

CREATE TABLE rouletteBetType (
     type VARCHAR(10) PRIMARY KEY NOT NULL
);

INSERT INTO rouletteBetType (type) VALUES ('black');
INSERT INTO rouletteBetType (type) VALUES ('green');
INSERT INTO rouletteBetType (type) VALUES ('red');

CREATE TABLE rouletteBet (
    id serial PRIMARY KEY,
    login VARCHAR(20) NOT NULL REFERENCES users(login),
    bet INTEGER NOT NULL CHECK (bet >= 0),
    betType VARCHAR(10) NOT NULL REFERENCES rouletteBetType(type),
    gameId INTEGER NOT NULL REFERENCES rouletteGames(id)
);

CREATE TABLE promotionalCode (
    id serial,
    login VARCHAR(20) REFERENCES users(login),
    code VARCHAR(20) PRIMARY KEY NOT NULL,
    coefficient FLOAT NOT NULL CHECK (coefficient >= 1)
);



--test


INSERT INTO users (login, email, password, cash) VALUES ('prohanter', 'fkdsf@gg.f', 'admin', 1000);

INSERT INTO promotionalCode (login, code, coefficient) VALUES ('prohanter', 'supercode', 1.20);

