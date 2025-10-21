-- FortiDesk Database Initialization Script

USE fortidesk;

-- Wait for tables to be created by SQLAlchemy
-- This script runs after the Flask app creates the tables

-- Add additional indexes for better performance (only if they don't exist)

-- Users table indexes (only if table exists)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE table_schema = 'fortidesk'
     AND table_name = 'users') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
     WHERE table_schema = 'fortidesk'
     AND table_name = 'users'
     AND index_name = 'idx_email') = 0,
    'ALTER TABLE users ADD INDEX idx_email (email)',
    'SELECT "Users table does not exist or index idx_email already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE table_schema = 'fortidesk'
     AND table_name = 'users') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
     WHERE table_schema = 'fortidesk'
     AND table_name = 'users'
     AND index_name = 'idx_username') = 0,
    'ALTER TABLE users ADD INDEX idx_username (username)',
    'SELECT "Users table does not exist or index idx_username already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Athletes table indexes (if table exists)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE table_schema = 'fortidesk'
     AND table_name = 'athletes') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
     WHERE table_schema = 'fortidesk'
     AND table_name = 'athletes'
     AND index_name = 'idx_athletes_fiscal_code') = 0,
    'ALTER TABLE athletes ADD INDEX idx_athletes_fiscal_code (fiscal_code)',
    'SELECT "Athletes table or index already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE table_schema = 'fortidesk'
     AND table_name = 'athletes') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
     WHERE table_schema = 'fortidesk'
     AND table_name = 'athletes'
     AND index_name = 'idx_athletes_name') = 0,
    'ALTER TABLE athletes ADD INDEX idx_athletes_name (last_name, first_name)',
    'SELECT "Athletes table or index already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Guardians table indexes (if table exists)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE table_schema = 'fortidesk'
     AND table_name = 'guardians') > 0 AND
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
     WHERE table_schema = 'fortidesk'
     AND table_name = 'guardians'
     AND index_name = 'idx_guardians_email') = 0,
    'ALTER TABLE guardians ADD INDEX idx_guardians_email (email)',
    'SELECT "Guardians table or index already exists"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Insert default admin user (password: admin123) - only if not exists and table exists
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE table_schema = 'fortidesk'
     AND table_name = 'users') > 0,
    "INSERT IGNORE INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at) VALUES ('admin', 'admin@fortitudo1901.it', '$2b$12$8YrKKtzk5KrZJGMZfJ6aFO7sGM8D5lMQpL4K5QJ8.6J4K5QJ8.6J4K', 'Admin', 'FortiDesk', 'admin', 1, NOW())",
    'SELECT "Users table does not exist yet"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Insert sample coach user (password: coach123) - only if not exists and table exists
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
     WHERE table_schema = 'fortidesk'
     AND table_name = 'users') > 0,
    "INSERT IGNORE INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at) VALUES ('coach', 'coach@fortitudo1901.it', '$2b$12$GhAQT9vT.AqZnNJ4K5QJ8.6J4K5QJ8.6J4K5QJ8.6J4K5QJ8.6J4K5', 'Coach', 'Example', 'coach', 1, NOW())",
    'SELECT "Users table does not exist yet"'));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Set proper character set and collation
ALTER DATABASE fortidesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;