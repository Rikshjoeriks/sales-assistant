-- Bootstrap script for local development databases.
-- Enables pgvector extension and creates the primary application database role.

CREATE EXTENSION IF NOT EXISTS vector;

DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sales_app') THEN
        CREATE ROLE sales_app LOGIN PASSWORD 'sales_app_password';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE sales_assistant TO sales_app;
