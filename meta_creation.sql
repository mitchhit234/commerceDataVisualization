/* This table for is just used for storing our starting balance,
so the user doesn't have to keep inputing their current balance,
and we dont have to keep calculating the starting balance */
CREATE TABLE IF NOT EXISTS META (
  date DATE NOT NULL,
  balance INT UNSIGNED NOT NULL,
  PRIMARY KEY (date,balance)
)