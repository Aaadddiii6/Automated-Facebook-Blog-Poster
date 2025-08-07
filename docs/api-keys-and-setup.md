# API Keys and Setup Documentation

## 🔑 Required API Keys

### 1. Supabase Configuration

```bash
# Get these from your Supabase project dashboard
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**How to get Supabase keys:**

1. Go to [supabase.com](https://supabase.com)
2. Create a new project or select existing one
3. Go to Settings → API
4. Copy the Project URL and API keys

### 2. Assembly AI API Key

```bash
ASSEMBLY_AI_API_KEY=your-assembly-ai-api-key
```

**How to get Assembly AI key:**

1. Go to [assemblyai.com](https://assemblyai.com)
2. Sign up for an account
3. Go to API Keys section
4. Copy your API key
5. **Cost**: ~$0.25/hour of video

### 3. OpenAI API Key

```bash
OPENAI_API_KEY=your-openai-api-key
```

**How to get OpenAI key:**

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. **Cost**: ~$0.02-0.05 per blog post

### 4. Facebook Graph API

```bash
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token
FACEBOOK_PAGE_ID=your-facebook-page-id
```

**How to get Facebook keys:**

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new app
3. Add Facebook Login product
4. Get Page Access Token:
   - Go to Graph API Explorer
   - Select your app and page
   - Generate access token
5. Get Page ID from your Facebook page URL

### 5. Make.com Configuration

```bash
MAKE_WEBHOOK_URL=https://hook.eu1.make.com/your-webhook-url
MAKE_WEBHOOK_SECRET=your-webhook-secret
```

**How to set up Make.com:**

1. Go to [make.com](https://make.com)
2. Create a new scenario
3. Add Webhook trigger
4. Copy the webhook URL
5. **Cost**: ~$10-20/month

## 🛠️ Step-by-Step Setup

### Step 1: Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-username/module-2-routes.git
cd module-2-routes

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 2: Environment Configuration

```bash
# Copy environment template
cp backend/env.example backend/.env

# Edit the .env file with your API keys
# Use a text editor to fill in all the required values
```

### Step 3: Database Setup

1. **Create Supabase Project:**

   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Wait for setup to complete

2. **Run Database Schema:**

   - Go to SQL Editor in Supabase dashboard
   - Copy and paste the SQL from `scripts/setup-database.sql`
   - Execute the script

3. **Verify Tables:**
   - Go to Table Editor
   - Verify these tables exist:
     - `meetings`
     - `video_files`
     - `blog_posts`
     - `processing_logs`
     - `social_media_posts`

### Step 4: FFmpeg Installation

**Windows:**

```bash
# Download from https://ffmpeg.org/download.html
# Add to PATH environment variable
```

**Mac:**

```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install ffmpeg
```

### Step 5: Test Setup

```bash
# Run the test script
python test_supabase.py
```

### Step 6: Start Application

```bash
# Navigate to backend directory
cd backend

# Start the Flask application
python main.py
```

## 📊 Database Schema

### Tables Structure

#### `meetings`

```sql
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR NOT NULL,
    meeting_date TIMESTAMP,
    organization_id VARCHAR NOT NULL,
    transcript TEXT,
    summary TEXT,
    transcription_status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `video_files`

```sql
CREATE TABLE video_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id),
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size BIGINT,
    duration INTEGER,
    processing_status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `blog_posts`

```sql
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id),
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    keywords TEXT[],
    facebook_post_id VARCHAR,
    facebook_post_url VARCHAR,
    facebook_post_status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `processing_logs`

```sql
CREATE TABLE processing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID REFERENCES meetings(id),
    step VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔒 Security Considerations

### Environment Variables

- **NEVER commit `.env` file to Git**
- Use `.env.example` as template
- Keep API keys secure
- Rotate keys regularly

### File Upload Security

- Validate file types
- Limit file sizes
- Sanitize filenames
- Store files securely

### API Security

- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Log security events

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Start application
gunicorn -w 4 -b 0.0.0.0:3000 main:create_app()
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 3000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "main:create_app()"]
```

### Environment Variables for Production

```bash
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
```

## 📈 Monitoring and Logging

### Health Check Endpoint

```bash
GET /health
```

### Log Files

- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

### Monitoring Setup

```bash
# Install monitoring tools
pip install sentry-sdk

# Configure Sentry
SENTRY_DSN=your-sentry-dsn
```

## 🐛 Troubleshooting

### Common Issues

1. **Supabase Connection Failed**

   - Verify URL and API keys
   - Check network connectivity
   - Ensure project is active

2. **FFmpeg Not Found**

   - Install FFmpeg system-wide
   - Add to PATH environment variable
   - Verify installation: `ffmpeg -version`

3. **File Upload Errors**

   - Check file permissions
   - Verify storage directory exists
   - Check file size limits

4. **Webhook Failures**
   - Verify Make.com webhook URL
   - Check network connectivity
   - Review webhook logs

### Debug Mode

```bash
export FLASK_ENV=development
python main.py
```

## 💰 Cost Estimation

### Monthly Costs (Estimated)

- **Supabase**: $5-10/month (metadata only)
- **Assembly AI**: $0.25/hour of video processed
- **OpenAI**: $0.02-0.05 per blog post
- **Make.com**: $10-20/month
- **Total**: $15-35/month + processing costs

### Cost Optimization

- Store videos locally (no cloud storage costs)
- Batch process videos
- Use efficient video formats
- Monitor API usage

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review logs for error details
3. Test individual components
4. Contact support with error details

---

**Note**: Keep all API keys secure and never share them publicly. Rotate keys regularly for security.
