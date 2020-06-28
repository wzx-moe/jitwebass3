DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS seller;
DROP TABLE IF EXISTS buyer;
DROP TABLE IF EXISTS orders;

CREATE TABLE buyer
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT        NOT NULL,
    email    TEXT        NOT NULL
);
CREATE TABLE seller
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT        NOT NULL,
    email    TEXT        NOT NULL,
    phone    INTEGER     NOT NULL
);

CREATE TABLE post
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER   NOT NULL,
    book_id   INTEGER   NOT NULL,
    created   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title     TEXT      NOT NULL,
    body      TEXT      NOT NULL,
    FOREIGN KEY (author_id) REFERENCES buyer (id),
    FOREIGN KEY (book_id) REFERENCES book (id)
);

CREATE TABLE book
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id   INTEGER   NOT NULL,
    author      TEXT      NOT NULL,
    created     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title       TEXT      NOT NULL,
    detail      TEXT      NOT NULL,
    category    TEXT      NOT NULL,
    picture     TEXT      NOT NULL,
    price       INTEGER   NOT NULL,
    sell_number INTEGER   NOT NULL DEFAULT '0',
    inventory   INTEGER   NOT NULL,
    FOREIGN KEY (author_id) REFERENCES seller (id)
);

CREATE TABLE orders
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id  INTEGER   NOT NULL,
    seller_id INTEGER   NOT NULL,
    book_id   INTEGER   NOT NULL,
    created   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name      TEXT      NOT NULL,
    address   TEXT      NOT NULL,
    address2  TEXT,
    city      TEXT      NOT NULL,
    zip       TEXT      NOT NULL,
    phone     INTEGER   NOT NULL,
    number    INTEGER   NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES seller (id),
    FOREIGN KEY (buyer_id) REFERENCES buyer (id),
    FOREIGN KEY (book_id) REFERENCES book (id)
);