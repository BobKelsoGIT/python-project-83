DROP TABLE IF EXISTS urls;

DROP TABLE IF EXISTS  url_checks;

CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE NOT NULL ,
    created_at timestamp
);

CREATE TABLE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint,
    status_code int,
    h1 varchar(50),
    title varchar(50),
    description text,
    created_at timestamp
);