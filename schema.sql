drop table if exists links;
drop table if exists cookies;

create table links (
    alias text,
    url text,
    expires timestamp,
    cookie_id integer
);

create table cookies (
    id integer primary key autoincrement,
    expires timestamp
);
