CREATE TABLE players(
   username type text,
   suds type integer,
   bonus type integer,
   penalty type integer,
   inventory type text,
   UNIQUE (username)
);
CREATE TABLE items (
   primary_key INTEGER PRIMARY KEY,
   name type text,
   price type integer,
   description type text,
   stock type integer default 0,
   forsale type integer default 0
);
CREATE TABLE submissions (
   id type text,
   UNIQUE (id)
);
CREATE TABLE comments (
   id type text,
   UNIQUE (id)
);
CREATE TABLE stats (
   name text primary key,
   lifetime integer default 0,
   week integer default 0,
   day integer default 0
);
