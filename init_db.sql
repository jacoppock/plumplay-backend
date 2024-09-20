-- Check if the user already exists before creating it
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'plumplay_user') THEN
        CREATE USER plumplay_user WITH PASSWORD 'plumplay_password';
    END IF;
END $$;