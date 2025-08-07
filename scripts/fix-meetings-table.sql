-- Fix for missing transcription_status column in meetings table
-- Run this in your Supabase SQL Editor

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