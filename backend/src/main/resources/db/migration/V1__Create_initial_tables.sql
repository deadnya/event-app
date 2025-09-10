CREATE TABLE companies (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE roles (
    id VARCHAR(32) PRIMARY KEY,
    role VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE users (
    id VARCHAR(32) PRIMARY KEY,
    gender VARCHAR(10),
    surname VARCHAR(255),
    name VARCHAR(255),
    patronymic VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    "group" VARCHAR(255),
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    telegram_chat_id BIGINT UNIQUE,
    telegram_username VARCHAR(255),
    google_access_token VARCHAR(2048),
    google_refresh_token VARCHAR(512),
    google_token_expiry TIMESTAMP,
    google_calendar_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    company_id VARCHAR(32),
    CONSTRAINT fk_users_company FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE users_roles (
    user_id VARCHAR(32) NOT NULL,
    role_id VARCHAR(32) NOT NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_users_roles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_users_roles_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE events (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(3000),
    date TIMESTAMP NOT NULL,
    location VARCHAR(255) NOT NULL,
    company_id VARCHAR(32),
    CONSTRAINT fk_events_company FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE event_registrations (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    event_id VARCHAR(32) NOT NULL,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    google_event_id VARCHAR(255),
    CONSTRAINT fk_event_registrations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_event_registrations_event FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE(user_id, event_id)
);

CREATE TABLE tokens (
    id VARCHAR(32) PRIMARY KEY,
    access_token VARCHAR(512) UNIQUE,
    refresh_token VARCHAR(512) UNIQUE,
    is_logged_out BOOLEAN DEFAULT FALSE,
    user_id VARCHAR(32),
    expiration_date TIMESTAMP,
    CONSTRAINT fk_tokens_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_telegram_chat_id ON users(telegram_chat_id);
CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_tokens_access_token ON tokens(access_token);
CREATE INDEX idx_tokens_refresh_token ON tokens(refresh_token);
CREATE INDEX idx_tokens_user_id ON tokens(user_id);
CREATE INDEX idx_events_company_id ON events(company_id);
CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_event_registrations_user_id ON event_registrations(user_id);
CREATE INDEX idx_event_registrations_event_id ON event_registrations(event_id);