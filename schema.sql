-- Create the Users table
CREATE TABLE Users
(
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Create the FlightDetails table
CREATE TABLE FlightDetails
(
    flight_id INTEGER PRIMARY KEY (AUTOINCREMENT),
    flight_number VARCHAR(20) UNIQUE NOT NULL,
    departure_location VARCHAR(100) NOT NULL,
    arrival_location VARCHAR(100) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    capacity INT NOT NULL,
    available_seats INT NOT NULL,
    flight_date DATE NOT NULL,
    flight_name VARCHAR(100) NOT NULL
);


CREATE TABLE BookingDetails
(
    booking_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    flight_id INTEGER,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num_tickets INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (flight_id) REFERENCES FlightDetails(flight_id)
);