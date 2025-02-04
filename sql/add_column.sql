-- ALTER TABLE project_files
-- ADD COLUMN project_id varchar(50);


-- UPDATE project_files
-- SET project_id = (SELECT project_number FROM projects WHERE project_files.project_number = projects.project_number);



-- ALTER TABLE project_files
-- ALTER COLUMN project_id SET NOT NULL;

ALTER TABLE project_files
ADD CONSTRAINT fk_project_id FOREIGN KEY (project_id) REFERENCES projects(project_number);

