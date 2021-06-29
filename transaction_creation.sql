/* Column num is a value that is left blank in the original csv, so I decided 
to make num a counter that increases by 1 for each transation
This will make it easier for us to determine which transactions happened in what
order, since datetime is not used by commerce and we could have transactions
on the same date */

CREATE TABLE IF NOT EXISTS TRANSACTIONS (
  date DATE NOT NULL,
  num INT UNSIGNED NOT NULL,
  description CHAR NOT NULL,
  debit INT UNSIGNED,
  credit INT UNSIGNED,
  CONSTRAINT CHK_NET CHECK (debit IS NULL or credit IS NULL),
  PRIMARY KEY (date,num)
);