-- Smart Donation Transparency Portal - Database Schema
-- Run: mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS smart_donation_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_donation_portal;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('donor', 'ngo', 'admin') NOT NULL DEFAULT 'donor',
    is_verified TINYINT(1) DEFAULT 0,        -- For NGOs: admin must verify
    is_active TINYINT(1) DEFAULT 1,
    organization_name VARCHAR(200),           -- NGO-specific
    registration_number VARCHAR(100),         -- NGO-specific
    phone VARCHAR(20),
    address TEXT,
    profile_image VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default admin
INSERT INTO users (name, email, password_hash, role, is_verified)
VALUES ('Admin', 'admin@portal.com', 'pbkdf2:sha256:260000$admin_hash_placeholder', 'admin', 1);

-- Campaigns Table
CREATE TABLE IF NOT EXISTS campaigns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ngo_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category ENUM('education','health','environment','disaster_relief','poverty','animal_welfare','other') NOT NULL,
    target_amount DECIMAL(12,2) NOT NULL,
    current_amount DECIMAL(12,2) DEFAULT 0.00,
    total_expenses DECIMAL(12,2) DEFAULT 0.00,
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('active','paused','completed','cancelled') DEFAULT 'active',
    image VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ngo_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Donations Table
CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    donor_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_method ENUM('bank_transfer','upi','cheque','cash','online') NOT NULL,
    transaction_id VARCHAR(100),
    payment_proof VARCHAR(255),              -- Uploaded file path
    status ENUM('pending','approved','rejected') DEFAULT 'pending',
    admin_note TEXT,
    approved_by INT,
    approved_at DATETIME,
    is_anonymous TINYINT(1) DEFAULT 0,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Expenses Table
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    ngo_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    amount DECIMAL(12,2) NOT NULL,
    category ENUM('salaries','supplies','infrastructure','transport','communication','events','miscellaneous') NOT NULL,
    expense_date DATE NOT NULL,
    proof_document VARCHAR(255),             -- Uploaded file path
    vendor_name VARCHAR(200),
    status ENUM('pending','approved','rejected') DEFAULT 'pending',
    admin_note TEXT,
    approved_by INT,
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (ngo_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Activity Log (for suspicious activity detection)
CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_campaigns_ngo ON campaigns(ngo_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_donations_campaign ON donations(campaign_id);
CREATE INDEX idx_donations_donor ON donations(donor_id);
CREATE INDEX idx_donations_status ON donations(status);
CREATE INDEX idx_expenses_campaign ON expenses(campaign_id);
CREATE INDEX idx_expenses_status ON expenses(status);
CREATE INDEX idx_activity_user ON activity_log(user_id);
CREATE INDEX idx_activity_created ON activity_log(created_at);
