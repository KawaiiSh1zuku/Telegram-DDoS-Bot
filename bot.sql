PRAGMA foreign_keys = false;
DROP TABLE IF EXISTS "method";
DROP TABLE IF EXISTS "user";
DROP TABLE IF EXISTS "blacklist";
CREATE TABLE "method" (
  "name" TEXT,
  "api_url" TEXT,
  "description" TEXT,
  "token" TEXT,
  "visible" INTEGER
);
CREATE TABLE "user" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "telegram_id" INTEGER,
  "credit" INTEGER,
  "cooldown" INTEGER,
  "register_time" INTEGER,
  "last_signed_time" INTEGER,
  "last_finish_time" INTEGER,
  "banned" INTEGER
);
CREATE TABLE "blacklist" (
  "keyword" TEXT
);
PRAGMA foreign_keys = true;