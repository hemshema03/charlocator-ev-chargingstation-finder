CREATE DATABASE IF NOT EXISTS ev_db4;
USE ev_db4;

DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS user_dashboard;
DROP TABLE IF EXISTS contact_us;
DROP TABLE IF EXISTS admin_charging_station_list;
DROP TABLE IF EXISTS login;
DROP TABLE IF EXISTS user;

CREATE TABLE login (
  login_id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(50) NOT NULL,
  usertype ENUM('admin','user') NOT NULL DEFAULT 'user',
  PRIMARY KEY (login_id)
);

CREATE TABLE admin_charging_station_list (
  station_id INT NOT NULL AUTO_INCREMENT,
  station_name VARCHAR(50) NOT NULL,
  address VARCHAR(100) NOT NULL,
  city VARCHAR(50) NOT NULL,
  charger_type VARCHAR(50) NOT NULL,
  available_ports VARCHAR(50) NOT NULL,
  PRIMARY KEY (station_id)
);

CREATE TABLE contact_us (
  sl_no INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(50),
  email VARCHAR(80),
  feedback_date DATE,
  feedback VARCHAR(255),
  PRIMARY KEY (sl_no)
);

CREATE TABLE user_dashboard (
  id INT NOT NULL AUTO_INCREMENT,
  login_id INT NOT NULL UNIQUE,
  credit_points INT DEFAULT 0,
  reward_claimed TINYINT(1) DEFAULT 0,
  discount_percentage INT DEFAULT 0,
  PRIMARY KEY (id),
  FOREIGN KEY (login_id) REFERENCES login(login_id) ON DELETE CASCADE
);

CREATE TABLE booking (
  booking_id INT NOT NULL AUTO_INCREMENT,
  station_name VARCHAR(50) NOT NULL,
  city VARCHAR(50) NOT NULL,
  available_ports VARCHAR(11) NOT NULL,
  booking_date DATE NOT NULL,
  time_from TIME NOT NULL,
  time_to TIME NOT NULL,
  created_id TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  login_id INT NOT NULL,
  original_price DECIMAL(10,2) NOT NULL DEFAULT 0,
  total_price DECIMAL(10,2) NOT NULL DEFAULT 0,
  discount_applied TINYINT(1) NOT NULL DEFAULT 0,
  discount_percentage INT NOT NULL DEFAULT 0,
  PRIMARY KEY (booking_id),
  FOREIGN KEY (login_id) REFERENCES login(login_id) ON DELETE CASCADE
);

CREATE TABLE user (
  user_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(50),
  email VARCHAR(80),
  PRIMARY KEY (user_id)
);

INSERT INTO login (login_id, username, password, usertype) VALUES
(1, 'admin', '123', 'admin'),
(2, 'user', 'user', 'user');

INSERT INTO user_dashboard (login_id, credit_points, reward_claimed, discount_percentage) VALUES
(2, 0, 0, 0);

INSERT INTO admin_charging_station_list (station_name, address, city, charger_type, available_ports) VALUES
('Plugmart Charging Station', '2nd street, RS Puram', 'coimbatore', 'AC Level 1 Charging', '5'),
('Zeon Charging Station', 'DB Road, Brookefields', 'coimbatore', 'AC Level 2 Charging', '4'),
('TATA Charging Station', 'Singanallur Trichy Road', 'coimbatore', 'DC Fast Charging', '3'),
('Lectron Charging Station', 'Century Plaza, Anna Salai', 'chennai', 'AC Level 1 Charging', '3'),
('Revolt Charging Station', 'Tambaram', 'chennai', 'AC Level 2 Charging', '4'),
('Ather Charging Station', 'Azad Road', 'erode', 'DC Fast Charging', '5'),
('Zeon Charging Station', 'Anna Park Road', 'salem', 'AC Level 1 Charging', '5'),
('Tata Charging Station', 'Chettipalayam', 'thirupur', 'AC Level 2 Charging', '2');
