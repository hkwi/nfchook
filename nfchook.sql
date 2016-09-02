CREATE TABLE pin (
 tag VARCHAR(255) PRIMARY KEY,
 pass VARCHAR(255),
 tm DATETIME
);
CREATE TABLE hook (
 tag VARCHAR(255),
 url VARCHAR(255)
);
CREATE UNIQUE INDEX uniq_hook on hook(tag,url);
