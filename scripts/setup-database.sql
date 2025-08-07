-- Video-to-Blog Automation System Database Setup
-- Additional tables for video processing and blog generation

-- Create blog_posts table
CREATE TABLE IF NOT EXISTS public.blog_posts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  meeting_id uuid,
  title character varying NOT NULL,
  content text NOT NULL,
  summary text,
  keywords text[],
  facebook_post_id character varying,
  facebook_post_url character varying,
  status character varying DEFAULT 'draft',
  published_at timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT blog_posts_pkey PRIMARY KEY (id),
  CONSTRAINT blog_posts_meeting_id_fkey FOREIGN KEY (meeting_id) REFERENCES public.meetings(id) ON DELETE CASCADE
);

-- Create video_files table
CREATE TABLE IF NOT EXISTS public.video_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES public.meetings(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    duration INTEGER,
    filename TEXT,
    original_filename TEXT,
    cloudinary_url TEXT,
    cloudinary_id TEXT,
    storage_type TEXT DEFAULT 'local',
    processing_status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create processing_logs table for tracking automation steps
CREATE TABLE IF NOT EXISTS public.processing_logs (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  meeting_id uuid,
  step_name character varying NOT NULL,
  status character varying NOT NULL,
  data jsonb,
  error_message text,
  started_at timestamp with time zone DEFAULT now(),
  completed_at timestamp with time zone,
  CONSTRAINT processing_logs_pkey PRIMARY KEY (id),
  CONSTRAINT processing_logs_meeting_id_fkey FOREIGN KEY (meeting_id) REFERENCES public.meetings(id) ON DELETE CASCADE
);

-- Create social_media_posts table for tracking all social media posts
CREATE TABLE IF NOT EXISTS public.social_media_posts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  blog_post_id uuid,
  platform character varying NOT NULL, -- 'facebook', 'linkedin', 'twitter', etc.
  post_id character varying,
  post_url character varying,
  content text,
  status character varying DEFAULT 'pending',
  published_at timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT social_media_posts_pkey PRIMARY KEY (id),
  CONSTRAINT social_media_posts_blog_post_id_fkey FOREIGN KEY (blog_post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE
);

-- Create posters table for storing generated images/posters
CREATE TABLE IF NOT EXISTS public.posters (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  meeting_id uuid,
  blog_post_id uuid,
  image_url text NOT NULL,
  image_type character varying DEFAULT 'poster', -- 'poster', 'infographic', 'quote', 'event_flyer'
  description text,
  generation_prompt text, -- The prompt used to generate the image
  platform_posted character varying[], -- Array of platforms where this poster was posted
  status character varying DEFAULT 'generated', -- 'generated', 'posted', 'failed'
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT posters_pkey PRIMARY KEY (id),
  CONSTRAINT posters_meeting_id_fkey FOREIGN KEY (meeting_id) REFERENCES public.meetings(id) ON DELETE CASCADE,
  CONSTRAINT posters_blog_post_id_fkey FOREIGN KEY (blog_post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_blog_posts_meeting_id ON public.blog_posts(meeting_id);
CREATE INDEX IF NOT EXISTS idx_blog_posts_status ON public.blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_video_files_meeting_id ON public.video_files(meeting_id);
CREATE INDEX IF NOT EXISTS idx_video_files_processing_status ON public.video_files(processing_status);
CREATE INDEX IF NOT EXISTS idx_processing_logs_meeting_id ON public.processing_logs(meeting_id);
CREATE INDEX IF NOT EXISTS idx_processing_logs_step_name ON public.processing_logs(step_name);
CREATE INDEX IF NOT EXISTS idx_social_media_posts_blog_post_id ON public.social_media_posts(blog_post_id);
CREATE INDEX IF NOT EXISTS idx_social_media_posts_platform ON public.social_media_posts(platform);
CREATE INDEX IF NOT EXISTS idx_posters_meeting_id ON public.posters(meeting_id);
CREATE INDEX IF NOT EXISTS idx_posters_blog_post_id ON public.posters(blog_post_id);
CREATE INDEX IF NOT EXISTS idx_posters_image_type ON public.posters(image_type);

-- Create RLS (Row Level Security) policies
ALTER TABLE public.blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.video_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_media_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posters ENABLE ROW LEVEL SECURITY;

-- Create policies for blog_posts
CREATE POLICY "Users can view blog posts for their organization" ON public.blog_posts
  FOR SELECT USING (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can insert blog posts for their organization" ON public.blog_posts
  FOR INSERT WITH CHECK (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can update blog posts for their organization" ON public.blog_posts
  FOR UPDATE USING (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

-- Create policies for video_files
CREATE POLICY "Users can view video files for their organization" ON public.video_files
  FOR SELECT USING (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can insert video files for their organization" ON public.video_files
  FOR INSERT WITH CHECK (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can update video files for their organization" ON public.video_files
  FOR UPDATE USING (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

-- Create policies for processing_logs
CREATE POLICY "Users can view processing logs for their organization" ON public.processing_logs
  FOR SELECT USING (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can insert processing logs for their organization" ON public.processing_logs
  FOR INSERT WITH CHECK (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

-- Create policies for social_media_posts
CREATE POLICY "Users can view social media posts for their organization" ON public.social_media_posts
  FOR SELECT USING (
    blog_post_id IN (
      SELECT id FROM public.blog_posts 
      WHERE meeting_id IN (
        SELECT id FROM public.meetings 
        WHERE organization_id IN (
          SELECT organization_id FROM public.contacts 
          WHERE id = auth.uid()
        )
      )
    )
  );

CREATE POLICY "Users can insert social media posts for their organization" ON public.social_media_posts
  FOR INSERT WITH CHECK (
    blog_post_id IN (
      SELECT id FROM public.blog_posts 
      WHERE meeting_id IN (
        SELECT id FROM public.meetings 
        WHERE organization_id IN (
          SELECT organization_id FROM public.contacts 
          WHERE id = auth.uid()
        )
      )
    )
  );

CREATE POLICY "Users can update social media posts for their organization" ON public.social_media_posts
  FOR UPDATE USING (
    blog_post_id IN (
      SELECT id FROM public.blog_posts 
      WHERE meeting_id IN (
        SELECT id FROM public.meetings 
        WHERE organization_id IN (
          SELECT organization_id FROM public.contacts 
          WHERE id = auth.uid()
        )
      )
    )
  );

-- Create policies for posters
CREATE POLICY "Users can view posters for their organization" ON public.posters
  FOR SELECT USING (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can insert posters for their organization" ON public.posters
  FOR INSERT WITH CHECK (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can update posters for their organization" ON public.posters
  FOR UPDATE USING (
    meeting_id IN (
      SELECT id FROM public.meetings 
      WHERE organization_id IN (
        SELECT organization_id FROM public.contacts 
        WHERE id = auth.uid()
      )
    )
  );

-- Create functions for common operations

-- Function to get meeting with all related data (updated to include posters)
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
    'posters', p
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
    step_name,
    status,
    data,
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

-- Function to update poster status after posting to social media
CREATE OR REPLACE FUNCTION update_poster_status(
  poster_uuid uuid,
  platform_posted_param character varying,
  status_param character varying DEFAULT 'posted'
)
RETURNS void AS $$
BEGIN
  UPDATE public.posters 
  SET 
    platform_posted = array_append(platform_posted, platform_posted_param),
    status = status_param
  WHERE id = poster_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated; 