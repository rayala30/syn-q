-- Ensure tables are created in the correct order
-- CREATE TABLE organization (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) UNIQUE NOT NULL,
--     admin_email VARCHAR(255) UNIQUE NOT NULL,
--     password TEXT NOT NULL, -- Admin password
--     org_passcode TEXT NOT NULL  -- Passcode for employees
-- );

-- CREATE TABLE projects (
--     id SERIAL PRIMARY KEY,
--     organization_id INTEGER NOT NULL,
--     project_number VARCHAR(50) UNIQUE NOT NULL,
--     client_name VARCHAR(255) NOT NULL,
--     project_name VARCHAR(255) NOT NULL,
--     FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
-- );


-- Create Project Files Table
CREATE TABLE project_files (
    id SERIAL PRIMARY KEY,
    project_number VARCHAR(50) REFERENCES projects(project_number) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL
);

-- CREATE TABLE users (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     email VARCHAR(255) UNIQUE NOT NULL,
--     organization_id INTEGER NOT NULL,
--     FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
-- );

