# Video-to-Blog Automation System Setup Guide

## Overview
This guide will walk you through setting up the complete video-to-blog automation system that converts Zoom meeting videos into blog posts and social media content.

## Prerequisites

### Required Software
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/)
- **FFmpeg** (optional, for video processing) - [Download here](https://ffmpeg.org/)

### Required Accounts & API Keys
1. **Supabase Account** - [Sign up here](https://supabase.com/)
2. **Assembly AI Account** - [Sign up here](https://www.assemblyai.com/)
3. **OpenAI Account** - [Sign up here](https://openai.com/)
4. **Facebook Developer Account** - [Sign up here](https://developers.facebook.com/)
5. **Make.com Account** - [Sign up here](https://www.make.com/)

## Step 1: Project Setup

### Clone the Repository
```bash
git clone <your-repository-url>
cd MakeAutomation
```

### Install Dependencies
```bash
npm install
```

### Create Environment File
```bash
cp env.example .env
```

## Step 2: Supabase Setup

### 1. Create Supabase Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - Name: `video-blog-automation`
   - Database Password: (generate a strong password)
   - Region: (choose closest to you)

### 2. Get API Keys
1. Go to Settings → API
2. Copy the following:
   - Project URL
   - Anon public key
   - Service role key (keep this secret!)

### 3. Run Database Setup
1. Go to SQL Editor in Supabase
2. Copy and paste the contents of `scripts/setup-database.sql`
3. Execute the script

### 4. Update Environment Variables
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

## Step 3: Assembly AI Setup

### 1. Get API Key
1. Go to [Assembly AI Dashboard](https://www.assemblyai.com/app/account)
2. Copy your API key

### 2. Update Environment Variables
```env
ASSEMBLY_AI_API_KEY=your_assembly_ai_api_key_here
```

## Step 4: OpenAI Setup

### 1. Get API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key

### 2. Update Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 5: Facebook Setup

### 1. Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "Create App"
3. Choose "Business" type
4. Fill in app details

### 2. Add Facebook Pages Product
1. In your app dashboard, click "Add Product"
2. Add "Facebook Pages"
3. Follow the setup wizard

### 3. Get Page Access Token
1. Go to Tools → Graph API Explorer
2. Select your app and page
3. Generate access token with permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`

### 4. Get Page ID
1. Go to your Facebook page
2. Click "About"
3. Copy the Page ID

### 5. Update Environment Variables
```env
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here
```

## Step 6: Make.com Setup

### 1. Create Scenario
1. Go to [Make.com](https://www.make.com/)
2. Create a new scenario
3. Add a webhook trigger
4. Configure the webhook URL

### 2. Build Automation Flow
Follow the configuration in `make-automation/scenario.json`:

1. **Webhook Trigger**
   - Method: POST
   - URL: Your webhook URL

2. **Assembly AI Modules**
   - Upload video
   - Start transcription
   - Poll for completion

3. **OpenAI Modules**
   - Generate blog content
   - Create summary
   - Extract keywords

4. **Facebook Module**
   - Post to Facebook page

5. **Webhook Response**
   - Send results back to your server

### 3. Update Environment Variables
```env
MAKE_WEBHOOK_URL=https://hook.eu1.make.com/your_webhook_url_here
WEBHOOK_CALLBACK_URL=https://your-domain.com/api/webhook
```

## Step 7: Local Development Setup

### 1. Create Storage Directories
```bash
mkdir -p backend/storage/videos
mkdir -p logs
```

### 2. Set File Permissions
```bash
chmod 755 backend/storage/videos
chmod 755 logs
```

### 3. Install FFmpeg (Optional)
For video processing features:

**Windows:**
```bash
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Start Development Server
```bash
npm run dev
```

## Step 8: Testing the Setup

### 1. Test Upload Endpoint
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "video=@test-video.mp4" \
  -F "title=Test Meeting" \
  -F "description=Test description" \
  -F "organizationId=your-org-id"
```

### 2. Test Webhook Endpoint
```bash
curl -X POST http://localhost:3000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "test-id",
    "step": "transcription_complete",
    "data": {
      "transcript": "Test transcript",
      "summary": "Test summary"
    }
  }'
```

### 3. Check Health Endpoint
```bash
curl http://localhost:3000/health
```

## Step 9: Production Deployment

### 1. Environment Configuration
Update `.env` for production:
```env
NODE_ENV=production
PORT=3000
ALLOWED_ORIGINS=https://your-domain.com
```

### 2. SSL Certificate
Set up SSL for HTTPS:
```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### 3. Process Manager
Install PM2:
```bash
npm install -g pm2
pm2 start server.js --name "video-blog-automation"
pm2 save
pm2 startup
```

### 4. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Step 10: Monitoring & Maintenance

### 1. Log Monitoring
```bash
# View application logs
pm2 logs video-blog-automation

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Database Monitoring
- Monitor Supabase dashboard for usage
- Set up alerts for storage limits
- Regular backup verification

### 3. API Usage Monitoring
- Monitor Assembly AI usage
- Track OpenAI API costs
- Monitor Facebook API limits

### 4. File Storage Cleanup
Set up automated cleanup:
```bash
# Add to crontab
0 2 * * * find /path/to/videos -mtime +30 -delete
```

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size limits
   - Verify file permissions
   - Check disk space

2. **Webhook Not Triggering**
   - Verify Make.com webhook URL
   - Check network connectivity
   - Validate webhook payload

3. **Database Connection Issues**
   - Verify Supabase credentials
   - Check network connectivity
   - Validate RLS policies

4. **API Rate Limits**
   - Monitor API usage
   - Implement retry logic
   - Consider upgrading plans

### Support Resources
- [Supabase Documentation](https://supabase.com/docs)
- [Assembly AI Documentation](https://www.assemblyai.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Make.com Documentation](https://www.make.com/en/help)

## Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly

2. **File Security**
   - Validate file types
   - Implement virus scanning
   - Secure file storage

3. **Network Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Set up firewall rules

4. **Data Privacy**
   - Implement data retention policies
   - Secure video storage
   - Comply with GDPR/privacy laws

## Next Steps

1. **Customize the System**
   - Modify blog generation prompts
   - Add more social media platforms
   - Implement custom branding

2. **Scale the System**
   - Add load balancing
   - Implement caching
   - Optimize database queries

3. **Add Features**
   - User authentication
   - Multi-tenant support
   - Advanced analytics
   - Email notifications

4. **Integration Options**
   - Slack notifications
   - Google Drive integration
   - CRM integration
   - Analytics platforms 