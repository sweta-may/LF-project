CREATE DATABASE lostfound_db
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    created_at DATETIME DEFAULT NOW()
);

CREATE TABLE LostReports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    item_name VARCHAR(100),
    description TEXT,
    location_reported VARCHAR(100),
    time_reported DATETIME DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE DetectedItems (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_type VARCHAR(100),
    location_detected VARCHAR(100),
    time_detected DATETIME DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'Unclaimed'
);

CREATE TABLE Matches (
    match_id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT,
    item_id INT,
    confidence_score FLOAT DEFAULT 0.0,
    matched_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (report_id) REFERENCES LostReports(report_id),
    FOREIGN KEY (item_id) REFERENCES DetectedItems(item_id)
);
