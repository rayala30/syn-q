ALTER TABLE projects DROP COLUMN file_name;
ALTER TABLE projects DROP COLUMN file_type;

ALTER TABLE projects ADD COLUMN project_name VARCHAR(255) NOT NULL;
