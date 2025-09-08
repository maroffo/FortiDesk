-- FortiDesk Database Initialization Script

USE fortidesk;

-- Wait for tables to be created by SQLAlchemy
-- This script runs after the Flask app creates the tables

-- Add additional indexes for better performance (only if they don't exist)

-- Users table indexes
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'users' 
     AND index_name = 'idx_email') = 0,
    'ALTER TABLE users ADD INDEX idx_email (email)',
    'SELECT "Index idx_email already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'users' 
     AND index_name = 'idx_username') = 0,
    'ALTER TABLE users ADD INDEX idx_username (username)',
    'SELECT "Index idx_username already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Bambini table indexes (if table exists)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'bambini') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'bambini' 
     AND index_name = 'idx_bambini_codice_fiscale') = 0,
    'ALTER TABLE bambini ADD INDEX idx_bambini_codice_fiscale (codice_fiscale)',
    'SELECT "Bambini table or index already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'bambini') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'bambini' 
     AND index_name = 'idx_bambini_nome_cognome') = 0,
    'ALTER TABLE bambini ADD INDEX idx_bambini_nome_cognome (cognome, nome)',
    'SELECT "Bambini table or index already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Genitori table indexes (if table exists)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'genitori') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE table_schema = 'fortidesk' 
     AND table_name = 'genitori' 
     AND index_name = 'idx_genitori_email') = 0,
    'ALTER TABLE genitori ADD INDEX idx_genitori_email (email)',
    'SELECT "Genitori table or index already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Insert default admin user (password: admin123) - only if not exists
INSERT IGNORE INTO users (
    username, 
    email, 
    password_hash, 
    nome, 
    cognome, 
    ruolo, 
    is_active, 
    data_creazione
) VALUES (
    'admin',
    'admin@fortitudo1901.it',
    '$2b$12$8YrKKtzk5KrZJGMZfJ6aFO7sGM8D5lMQpL4K5QJ8.6J4K5QJ8.6J4K',
    'Admin',
    'FortiDesk',
    'admin',
    1,
    NOW()
);

-- Insert sample allenatore user (password: coach123) - only if not exists
INSERT IGNORE INTO users (
    username, 
    email, 
    password_hash, 
    nome, 
    cognome, 
    ruolo, 
    is_active, 
    data_creazione
) VALUES (
    'coach',
    'coach@fortitudo1901.it',
    '$2b$12$GhAQT9vT.AqZnNJ4K5QJ8.6J4K5QJ8.6J4K5QJ8.6J4K5QJ8.6J4K5',
    'Allenatore',
    'Esempio',
    'allenatore',
    1,
    NOW()
);

-- Set proper character set and collation
ALTER DATABASE fortidesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;