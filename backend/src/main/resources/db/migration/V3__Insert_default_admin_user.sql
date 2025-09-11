INSERT INTO users (
    id,
    email,
    password,
    surname,
    name,
    is_approved
) VALUES (
    'admin-user-id-default',
    'admin@admin.com',
    '$2a$12$udksNZyPoMH02HwgCaTtnOUvbt1mxgn76FpUx9NJn7qx6/4.ril5S',
    'Admin',
    'User',
    true
);

INSERT INTO users_roles (user_id, role_id) 
VALUES ('admin-user-id-default', 'admin-role-id');

INSERT INTO companies (id, name) VALUES 
('company-1', 'Tech Solutions Inc'),
('company-2', 'Digital Innovation Corp'),
('company-3', 'Software Development Ltd');

INSERT INTO users (
    id,
    email,
    password,
    surname,
    name,
    patronymic,
    company_id,
    is_approved
) VALUES 
(
    'manager-1',
    'manager1@techsolutions.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Johnson',
    'Alice',
    'Marie',
    'company-1',
    true
),
(
    'manager-2',
    'manager2@digitalinnovation.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Smith',
    'Robert',
    'James',
    'company-2',
    true
),
(
    'manager-3',
    'manager3@softwaredev.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Brown',
    'Emily',
    'Catherine',
    'company-3',
    true
);

INSERT INTO users_roles (user_id, role_id) VALUES 
('manager-1', 'manager-role-id'),
('manager-2', 'manager-role-id'),
('manager-3', 'manager-role-id');

INSERT INTO users (
    id,
    email,
    password,
    surname,
    name,
    patronymic,
    "group",
    is_approved
) VALUES 
(
    'student-1',
    'student1@mail.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Wilson',
    'Michael',
    'David',
    'CS-2023-1',
    true
),
(
    'student-2',
    'student2@mail.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Davis',
    'Sarah',
    'Elizabeth',
    'CS-2023-1',
    true
),
(
    'student-3',
    'student3@mail.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Garcia',
    'Carlos',
    'Antonio',
    'CS-2023-2',
    true
),
(
    'student-4',
    'student4@mail.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Miller',
    'Jessica',
    'Rose',
    'CS-2023-2',
    true
),
(
    'student-5',
    'student5@mail.com',
    '$2a$12$wN4xvGXre2Hp26pNPklQmuyGz.6w8AcXESNaKVLilYmjJ.iLwPiW6',
    'Martinez',
    'Daniel',
    'Jose',
    'CS-2024-1',
    true
);

INSERT INTO users_roles (user_id, role_id) VALUES 
('student-1', 'student-role-id'),
('student-2', 'student-role-id'),
('student-3', 'student-role-id'),
('student-4', 'student-role-id'),
('student-5', 'student-role-id');
