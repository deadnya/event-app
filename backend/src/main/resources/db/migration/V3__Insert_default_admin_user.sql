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
