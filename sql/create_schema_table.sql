-- -- Create Schemas
-- CREATE SCHEMA auth_schema;
-- CREATE SCHEMA project_schema;

-- Create Organization Table
CREATE TABLE organization (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    org_passcode TEXT NOT NULL -- Passcode for employees, set by the organization admin
);

-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hashed password
    is_admin BOOLEAN DEFAULT FALSE,
    organization_id INTEGER NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organization(id)
);

-- Create Projects Table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    project_number VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
);

-- Create Project Files Table
CREATE TABLE project_files (
    id SERIAL PRIMARY KEY,
    project_number VARCHAR(50) REFERENCES projects(project_number) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL
);
