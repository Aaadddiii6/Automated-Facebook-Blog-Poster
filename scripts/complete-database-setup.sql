-- Complete Database Setup for Video-to-Blog Automation System
-- This script creates all necessary tables, indexes, and policies
-- Based on the current schema structure

-- =====================================================
-- 1. CORE TABLES (already exist in your schema)
-- =====================================================

-- meetings table (already exists)
-- blog_posts table (already exists)
-- organizations table (already exists)
-- contacts table (already exists)

-- =====================================================
-- 2. ADDITIONAL TABLES NEEDED FOR THE APPLICATION
-- =====================================================

-- Create video_files table (needed for the upload service)
CREATE TABLE IF NOT EXISTS public.video_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES public.meetings(id) ON DELETE CASCADE,
    file_name TEXT,
    original_filename TEXT,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    duration INTEGER,
    cloudinary_url TEXT,
    cloudinary_id TEXT,
    storage_type TEXT DEFAULT 'local',
    processing_status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create processing_logs table for tracking automation steps
CREATE TABLE IF NOT EXISTS public.processing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES public.meetings(id) ON DELETE CASCADE,
    step VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    details JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create social_media_posts table (more detailed than social_posts)
CREATE TABLE IF NOT EXISTS public.social_media_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_post_id UUID REFERENCES public.blog_posts(id) ON DELETE CASCADE,
    platform VARCHAR NOT NULL, -- 'facebook', 'linkedin', 'twitter', etc.
    post_id VARCHAR,
    post_url VARCHAR,
    content TEXT,
    status VARCHAR DEFAULT 'pending',
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create posters table for storing generated images/posters
CREATE TABLE IF NOT EXISTS public.posters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES public.meetings(id) ON DELETE CASCADE,
    blog_post_id UUID REFERENCES public.blog_posts(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    image_type VARCHAR DEFAULT 'poster', -- 'poster', 'infographic', 'quote', 'event_flyer'
    description TEXT,
    generation_prompt TEXT, -- The prompt used to generate the image
    platform_posted VARCHAR[], -- Array of platforms where this poster was posted
    status VARCHAR DEFAULT 'generated', -- 'generated', 'posted', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. ADD MISSING COLUMNS TO EXISTING TABLES
-- =====================================================

-- Add missing columns to blog_posts table
ALTER TABLE public.blog_posts 
ADD COLUMN IF NOT EXISTS keywords TEXT[],
ADD COLUMN IF NOT EXISTS facebook_post_id VARCHAR,
ADD COLUMN IF NOT EXISTS facebook_post_url VARCHAR,
ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'draft';

-- Add missing columns to meetings table
ALTER TABLE public.meetings 
ADD COLUMN IF NOT EXISTS blog_status VARCHAR DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS poster_status VARCHAR DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS facebook_post_status VARCHAR DEFAULT 'pending';

-- =====================================================
-- 4. CREATE INDEXES FOR BETTER PERFORMANCE
-- =====================================================

-- Indexes for meetings table
CREATE INDEX IF NOT EXISTS idx_meetings_organization_id ON public.meetings(organization_id);
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON public.meetings(created_at);
CREATE INDEX IF NOT EXISTS idx_meetings_transcription_status ON public.meetings(transcription_status);
CREATE INDEX IF NOT EXISTS idx_meetings_blog_status ON public.meetings(blog_status);
CREATE INDEX IF NOT EXISTS idx_meetings_poster_status ON public.meetings(poster_status);
CREATE INDEX IF NOT EXISTS idx_meetings_facebook_post_status ON public.meetings(facebook_post_status);

-- Indexes for blog_posts table
CREATE INDEX IF NOT EXISTS idx_blog_posts_meeting_id ON public.blog_posts(meeting_id);
CREATE INDEX IF NOT EXISTS idx_blog_posts_status ON public.blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_blog_posts_created_at ON public.blog_posts(created_at);

-- Indexes for video_files table
CREATE INDEX IF NOT EXISTS idx_video_files_meeting_id ON public.video_files(meeting_id);
CREATE INDEX IF NOT EXISTS idx_video_files_processing_status ON public.video_files(processing_status);
CREATE INDEX IF NOT EXISTS idx_video_files_created_at ON public.video_files(created_at);

-- Indexes for processing_logs table
CREATE INDEX IF NOT EXISTS idx_processing_logs_meeting_id ON public.processing_logs(meeting_id);
CREATE INDEX IF NOT EXISTS idx_processing_logs_step ON public.processing_logs(step);
CREATE INDEX IF NOT EXISTS idx_processing_logs_started_at ON public.processing_logs(started_at);

-- Indexes for social_media_posts table
CREATE INDEX IF NOT EXISTS idx_social_media_posts_blog_post_id ON public.social_media_posts(blog_post_id);
CREATE INDEX IF NOT EXISTS idx_social_media_posts_platform ON public.social_media_posts(platform);
CREATE INDEX IF NOT EXISTS idx_social_media_posts_status ON public.social_media_posts(status);

-- Indexes for posters table
CREATE INDEX IF NOT EXISTS idx_posters_meeting_id ON public.posters(meeting_id);
CREATE INDEX IF NOT EXISTS idx_posters_blog_post_id ON public.posters(blog_post_id);
CREATE INDEX IF NOT EXISTS idx_posters_image_type ON public.posters(image_type);

-- Indexes for organizations table
CREATE INDEX IF NOT EXISTS idx_organizations_name ON public.organizations(name);
CREATE INDEX IF NOT EXISTS idx_organizations_domain ON public.organizations(domain);

-- Indexes for contacts table
CREATE INDEX IF NOT EXISTS idx_contacts_organization_id ON public.contacts(organization_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON public.contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON public.contacts(status);

-- =====================================================
-- 5. ENABLE ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.video_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_media_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meeting_attendees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meeting_minutes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meeting_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_posts ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 6. CREATE RLS POLICIES
-- =====================================================

-- Basic policies for authenticated users (you can modify these based on your needs)
-- For now, allowing all operations for authenticated users

-- Meetings policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.meetings;
CREATE POLICY "Allow all operations for authenticated users" ON public.meetings
    FOR ALL USING (true);

-- Blog posts policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.blog_posts;
CREATE POLICY "Allow all operations for authenticated users" ON public.blog_posts
    FOR ALL USING (true);

-- Video files policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.video_files;
CREATE POLICY "Allow all operations for authenticated users" ON public.video_files
    FOR ALL USING (true);

-- Processing logs policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.processing_logs;
CREATE POLICY "Allow all operations for authenticated users" ON public.processing_logs
    FOR ALL USING (true);

-- Social media posts policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.social_media_posts;
CREATE POLICY "Allow all operations for authenticated users" ON public.social_media_posts
    FOR ALL USING (true);

-- Posters policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.posters;
CREATE POLICY "Allow all operations for authenticated users" ON public.posters
    FOR ALL USING (true);

-- Organizations policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.organizations;
CREATE POLICY "Allow all operations for authenticated users" ON public.organizations
    FOR ALL USING (true);

-- Contacts policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.contacts;
CREATE POLICY "Allow all operations for authenticated users" ON public.contacts
    FOR ALL USING (true);

-- Meeting attendees policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.meeting_attendees;
CREATE POLICY "Allow all operations for authenticated users" ON public.meeting_attendees
    FOR ALL USING (true);

-- Meeting minutes policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.meeting_minutes;
CREATE POLICY "Allow all operations for authenticated users" ON public.meeting_minutes
    FOR ALL USING (true);

-- Meeting videos policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.meeting_videos;
CREATE POLICY "Allow all operations for authenticated users" ON public.meeting_videos
    FOR ALL USING (true);

-- Social posts policies
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON public.social_posts;
CREATE POLICY "Allow all operations for authenticated users" ON public.social_posts
    FOR ALL USING (true);

-- =====================================================
-- 7. CREATE HELPER FUNCTIONS
-- =====================================================

-- Function to get meeting with all related data
CREATE OR REPLACE FUNCTION get_meeting_with_details(meeting_uuid uuid)
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  SELECT json_build_object(
    'meeting', m,
    'video_files', vf,
    'blog_posts', bp,
    'processing_logs', pl,
    'social_media_posts', smp,
    'posters', p,
    'meeting_minutes', mm,
    'meeting_videos', mv,
    'meeting_attendees', ma
  ) INTO result
  FROM public.meetings m
  LEFT JOIN (
    SELECT json_agg(video_files.*) as vf
    FROM public.video_files 
    WHERE meeting_id = meeting_uuid
  ) vf ON true
  LEFT JOIN (
    SELECT json_agg(blog_posts.*) as bp
    FROM public.blog_posts 
    WHERE meeting_id = meeting_uuid
  ) bp ON true
  LEFT JOIN (
    SELECT json_agg(processing_logs.*) as pl
    FROM public.processing_logs 
    WHERE meeting_id = meeting_uuid
    ORDER BY started_at DESC
  ) pl ON true
  LEFT JOIN (
    SELECT json_agg(social_media_posts.*) as smp
    FROM public.social_media_posts smp
    JOIN public.blog_posts bp ON smp.blog_post_id = bp.id
    WHERE bp.meeting_id = meeting_uuid
  ) smp ON true
  LEFT JOIN (
    SELECT json_agg(posters.*) as p
    FROM public.posters 
    WHERE meeting_id = meeting_uuid
  ) p ON true
  LEFT JOIN (
    SELECT json_agg(meeting_minutes.*) as mm
    FROM public.meeting_minutes 
    WHERE meeting_id = meeting_uuid
  ) mm ON true
  LEFT JOIN (
    SELECT json_agg(meeting_videos.*) as mv
    FROM public.meeting_videos 
    WHERE meeting_id = meeting_uuid
  ) mv ON true
  LEFT JOIN (
    SELECT json_agg(meeting_attendees.*) as ma
    FROM public.meeting_attendees 
    WHERE meeting_id = meeting_uuid
  ) ma ON true
  WHERE m.id = meeting_uuid;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update processing status
CREATE OR REPLACE FUNCTION update_processing_status(
  meeting_uuid uuid,
  step_name text,
  status text,
  data jsonb DEFAULT NULL,
  error_message text DEFAULT NULL
)
RETURNS void AS $$
BEGIN
  INSERT INTO public.processing_logs (
    meeting_id,
    step,
    status,
    details,
    error_message,
    completed_at
  ) VALUES (
    meeting_uuid,
    step_name,
    status,
    data,
    error_message,
    CASE WHEN status IN ('completed', 'failed') THEN now() ELSE NULL END
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create a poster record
CREATE OR REPLACE FUNCTION create_poster(
  meeting_uuid uuid,
  image_url_param text,
  blog_post_uuid uuid DEFAULT NULL,
  image_type_param character varying DEFAULT 'poster',
  description_param text DEFAULT NULL,
  generation_prompt_param text DEFAULT NULL
)
RETURNS uuid AS $$
DECLARE
  poster_id uuid;
BEGIN
  INSERT INTO public.posters (
    meeting_id,
    blog_post_id,
    image_url,
    image_type,
    description,
    generation_prompt
  ) VALUES (
    meeting_uuid,
    blog_post_uuid,
    image_url_param,
    image_type_param,
    description_param,
    generation_prompt_param
  ) RETURNING id INTO poster_id;
  
  RETURN poster_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 8. GRANT PERMISSIONS
-- =====================================================

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- =====================================================
-- 9. REFRESH SCHEMA CACHE
-- =====================================================

-- Force refresh the PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- =====================================================
-- 10. VERIFICATION QUERIES
-- =====================================================

-- Check that all tables exist
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'meetings', 'blog_posts', 'video_files', 'processing_logs',
    'social_media_posts', 'posters', 'organizations', 'contacts',
    'meeting_attendees', 'meeting_minutes', 'meeting_videos', 'social_posts'
)
ORDER BY table_name;

-- Check that all functions exist
SELECT 
    routine_name,
    routine_type
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name IN (
    'get_meeting_with_details', 'update_processing_status', 'create_poster'
)
ORDER BY routine_name; 