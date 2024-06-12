CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(50) UNIQUE NOT NULL ,
    created_at timestamp
);