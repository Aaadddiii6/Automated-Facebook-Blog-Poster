-- Add transcription_status column to meetings table
ALTER TABLE public.meetings 
ADD COLUMN IF NOT EXISTS transcription_status character varying DEFAULT 'pending';

-- Add other missing columns that might be needed
ALTER TABLE public.meetings 
ADD COLUMN IF NOT EXISTS blog_status character varying DEFAULT 'pending';

ALTER TABLE public.meetings 
ADD COLUMN IF NOT EXISTS poster_status character varying DEFAULT 'pending';

ALTER TABLE public.meetings 
ADD COLUMN IF NOT EXISTS facebook_post_status character varying DEFAULT 'pending';

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_meetings_transcription_status ON public.meetings(transcription_status);
CREATE INDEX IF NOT EXISTS idx_meetings_blog_status ON public.meetings(blog_status);
CREATE INDEX IF NOT EXISTS idx_meetings_poster_status ON public.meetings(poster_status);
CREATE INDEX IF NOT EXISTS idx_meetings_facebook_post_status ON public.meetings(facebook_post_status);

-- Add missing columns to video_files table
ALTER TABLE public.video_files 
ADD COLUMN IF NOT EXISTS duration integer;

ALTER TABLE public.video_files 
ADD COLUMN IF NOT EXISTS filename character varying;

ALTER TABLE public.video_files 
ADD COLUMN IF NOT EXISTS original_filename character varying;

ALTER TABLE public.video_files 
ADD COLUMN IF NOT EXISTS file_size bigint;

-- Add description column to organizations table if it doesn't exist
ALTER TABLE public.organizations 
ADD COLUMN IF NOT EXISTS description text;

-- Add created_at column to organizations table if it doesn't exist
ALTER TABLE public.organizations 
ADD COLUMN IF NOT EXISTS created_at timestamp with time zone DEFAULT now();

-- Insert a default organization for testing
INSERT INTO public.organizations (id, name, description) 
VALUES (
  '123e4567-e89b-12d3-a456-426614174000',
  'Default Organization',
  'Default organization for testing purposes'
) ON CONFLICT (id) DO NOTHING;

-- Enable RLS on organizations table
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for organizations (allow all operations for now)
DROP POLICY IF EXISTS "Allow all operations on organizations" ON public.organizations;
CREATE POLICY "Allow all operations on organizations" ON public.organizations
  FOR ALL USING (true) WITH CHECK (true); 