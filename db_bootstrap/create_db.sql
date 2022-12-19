CREATE DATABASE cool_db;
CREATE USER 'webapp'@'%' IDENTIFIED BY 'abc123';
GRANT ALL PRIVILEGES ON cool_db.* TO 'webapp'@'%';
FLUSH PRIVILEGES;

-- Move into the database we just created.
-- TODO: If you changed the name of the
-- database above, you need to change it here too.

USE cool_db;

-- Put your DDL
CREATE TABLE test_table (
    name VARCHAR(20),
    color VARCHAR(10)
);
-- Add sample data.
INSERT INTO test_table
    (name, color)
VALUES
    ('dev', 'blue'),
    ('pro', 'yellow'),
    ('junior', 'red');
