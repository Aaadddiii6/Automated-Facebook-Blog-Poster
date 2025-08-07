-- Fix Organizations Table
-- Add missing organization for testing

-- First, check if organizations table exists and has the required columns
DO $$
BEGIN
    -- Add description column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'organizations' AND column_name = 'description') THEN
        ALTER TABLE public.organizations ADD COLUMN description text;
    END IF;
    
    -- Add created_at column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'organizations' AND column_name = 'created_at') THEN
        ALTER TABLE public.organizations ADD COLUMN created_at timestamp with time zone DEFAULT now();
    END IF;
END $$;

-- Insert default organization if it doesn't exist
INSERT INTO public.organizations (id, name, description, created_at)
VALUES (
    '123e4567-e89b-12d3-a456-426614174000',
    'Default Organization',
    'Default organization for testing',
    '2024-01-01T00:00:00Z'
)
ON CONFLICT (id) DO NOTHING;

-- Verify the organization was created
SELECT * FROM public.organizations WHERE id = '123e4567-e89b-12d3-a456-426614174000'; 