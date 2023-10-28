CREATE TABLE players(
   username type text,
   suds type integer,
   bonus type integer,
   penalty type integer,
   inventory type text, score_7d number, dailysuds number, safemode int default 1 not null, safemode_timer TEXT default "2023-05-10 23:59:59" not null,
   UNIQUE (username)
);
CREATE TABLE items (
   primary_key INTEGER PRIMARY KEY,
   name type text,
   price type integer,
   description type text
, stock type integer default 0, forsale type integer default 0, unlimited integer default 0 not null, tags text);
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
