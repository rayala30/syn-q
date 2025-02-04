-- Insert Organization
-- INSERT INTO organization (name, admin_email, password, org_passcode, email_domain)
-- VALUES ('SynQ Test Org', 'admin@synqtest.com', 'testpass', 'ABCD1234', '@synctest.com')
-- RETURNING id;

-- Use the returned ID for the organization in the next inserts
-- Replace {SynQ_Test_Org_ID} with the actual returned ID

-- -- Insert User
INSERT INTO users (name, email, organization_id, is_admin, password)
VALUES ('Test Admin', 'admin@synqtest.com', (SELECT id FROM organization WHERE name = 'SynQ Test Org'), TRUE, 'testadminpass');

-- -- Insert into projects
-- INSERT INTO projects (organization_id, project_number, client_name, project_name)
-- VALUES 
--     ((SELECT id FROM organization WHERE name = 'SynQ Test Org'), '0001', 'Test Client 1', 'Test Project 1'),
--     ((SELECT id FROM organization WHERE name = 'SynQ Test Org'), '0002', 'Test Client 2', 'Test Project 2');

-- -- Insert into project_files
-- INSERT INTO project_files (project_number, file_name, file_type)
-- VALUES 
--     ('0001', 'client_1_file_1.rvt', 'rvt'),
--     ('0001', 'client_1_file_2.rvt', 'rvt'),
--     ('0002', 'client_2_file_1.rvt', 'rvt');
