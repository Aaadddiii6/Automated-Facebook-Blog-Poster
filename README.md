# Content Generation Automation System (Python/Flask)

A comprehensive system that automates the conversion of videos and meeting transcripts into blog posts and social media content. Built with Python Flask, Supabase, and Make.com automation.

## 🎯 Dual Flow Support

The system now supports two different workflows:

1. **Video Upload Flow**: Upload video → Cloudinary → Assembly API → OpenAI → Facebook → Instagram
2. **Meeting ID Flow**: Meeting ID → Supabase → OpenAI → Facebook → Instagram

Users can choose between uploading a video file or providing a meeting ID to fetch existing transcripts from Supabase. Both flows now support posting to both Facebook and Instagram.

## 🚀 System Architecture

### Technology Stack

- **Backend**: Python Flask API
- **Database**: Supabase (PostgreSQL)
- **File Storage**: Local storage (cost-effective for large videos)
- **Automation**: Make.com (webhook-triggered workflows)
- **AI Services**: Assembly AI (transcription), OpenAI (content generation)
- **Social Media**: Facebook Graph API

### File Structure

```
MAKESUPABASE/
├── backend/
│   ├── main.py                      # Main Flask application
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # Environment variables
│   ├── api/
│   │   ├── upload_routes.py         # Video upload endpoints
│   │   └── webhook_routes.py        # Make.com webhook handler
│   ├── utils/
│   │   ├── meeting_processor_service.py  # Meeting ID processing
│   │   ├── upload_service.py        # Video upload processing
│   │   ├── cloudinary_service.py    # Cloudinary integration
│   │   └── file_manager.py          # File management utilities
│   └── storage/
│       └── videos/                  # Local video storage
├── frontend/
│   ├── index.html                   # Main upload interface
│   └── static/                      # CSS, JS, and assets
└── docs/                            # Documentation
```

## 🔄 Complete Workflows

### Video Upload Flow

1. **Video Upload**: User uploads video through web interface
2. **Local Storage**: Video saved to server's local storage (cost-effective)
3. **Database Record**: Meeting and video metadata stored in Supabase
4. **Cloudinary Upload**: Video uploaded to Cloudinary for processing
5. **Make.com Trigger**: Webhook triggers automation workflow
6. **Assembly AI**: Video transcribed using Assembly AI API
7. **OpenAI Processing**: Transcript converted to blog content
8. **Facebook Post**: Blog posted to Facebook page via Graph API
9. **Instagram Post**: Blog posted to Instagram via Graph API
10. **Status Updates**: Progress tracked and logged in database

### Meeting ID Flow

1. **Meeting ID Input**: User provides meeting ID from Supabase
2. **Supabase Fetch**: System fetches transcript from Supabase
3. **Database Record**: Meeting record created/updated in local database
4. **Make.com Trigger**: Webhook triggers content generation workflow
5. **OpenAI Processing**: Transcript converted to blog content
6. **Facebook Post**: Blog posted to Facebook page via Graph API
7. **Instagram Post**: Blog posted to Instagram via Graph API
8. **Status Updates**: Progress tracked and logged in database

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- Supabase account
- Make.com account
- API keys (Assembly AI, OpenAI, Facebook, Instagram, Cloudinary)

### Quick Start

1. **Clone and Setup**:

```bash
git clone <repository>
cd MAKESUPABASE
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. **Environment Configuration**:

```bash
# Copy and edit the .env file in backend directory
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys and configuration
```

3. **Database Setup**:

```sql
-- Run the SQL script in Supabase SQL Editor
-- See the schema provided in the project documentation
```

4. **Start Application**:

```bash
cd backend
python main.py
```

5. **Access Application**:

- Upload Interface: http://localhost:3000
- Health Check: http://localhost:3000/health

## 📡 API Endpoints

### Upload Endpoints

- `POST /api/upload/` - Upload video file
- `GET /api/upload/status/<meeting_id>` - Check processing status

### Meeting ID Endpoints

- `POST /api/process-meeting/` - Process meeting ID from Supabase

### Webhook Endpoints

- `POST /api/webhook/` - Make.com callback handler

### Health & Monitoring

- `GET /health` - Application health check

## 🔒 Security Features

- **Rate Limiting**: Configurable request limits
- **File Validation**: Type, size, and content validation
- **CORS Protection**: Configurable cross-origin policies
- **Input Sanitization**: All inputs validated and sanitized
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed audit trails

## 💰 Cost Optimization

### Hybrid Storage Strategy

- **Videos**: Stored locally on server (no cloud storage costs)
- **Metadata**: Stored in Supabase (minimal database costs)
- **Processing**: On-demand via Make.com (pay per use)

### Estimated Costs

- **Supabase**: ~$5-10/month (metadata only)
- **Assembly AI**: ~$0.25/hour of video
- **OpenAI**: ~$0.02-0.05 per blog post
- **Make.com**: ~$10-20/month (automation)
- **Cloudinary**: ~$5-15/month (video storage)
- **Instagram API**: Free (with rate limits)

## 🚀 Production Deployment

### ⚠️ IMPORTANT: Current Development Setup

**Current Status**: Using ngrok for local development webhook callbacks

**What's Currently Configured:**

- **Local Server**: `http://localhost:3000`
- **Ngrok Tunnel**: `https://[ngrok-subdomain].ngrok.io`
- **Webhook Endpoint**: `/api/webhook`

### 🔧 Deployment Requirements

**For Production Deployment, the following URLs need to be updated:**

1. **Environment Variables** (`backend/.env`):

```bash
# Current (local development):
MAKE_MEETING_ID_WEBHOOK_URL=https://hook.eu2.make.com/bwoe7zsdf5b771pzxrsxdq1xcjo5c69y

# For Production/Deployment, this will need to be updated to:
MAKE_MEETING_ID_WEBHOOK_URL=https://your-deployed-domain.com/api/webhook
```

2. **Make.com Webhook Response URLs**:

- **Current**: Using ngrok URLs for webhook responses
- **Deployment**: Will need to be updated to production domain

**Required Information for Deployment:**

- Production domain/URL where the backend will be deployed
- Webhook endpoint path (e.g., `/api/webhook` or `/webhook/callback`)

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3000 main:app
```

### Using PM2 (with Python)

```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring & Logging

- **Application Logs**: Structured logging with rotation
- **Health Checks**: Automated health monitoring
- **Error Tracking**: Comprehensive error reporting
- **Performance Metrics**: Request timing and resource usage

## 🔧 Configuration

### Environment Variables

See `backend/.env` for all available configuration options:

- **Flask Configuration**: Environment, secret key, port
- **Supabase**: Database connection details
- **API Keys**: Assembly AI, OpenAI, Facebook, Instagram, Cloudinary
- **Make.com**: Webhook URLs and secrets
- **Storage**: File paths and size limits
- **Security**: CORS, rate limiting, origins

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**: Install FFmpeg system-wide
2. **Supabase connection**: Verify URL and API keys
3. **File permissions**: Ensure storage directory is writable
4. **Rate limiting**: Check Make.com webhook limits
5. **Ngrok tunnel**: Ensure ngrok is running for local development

### Debug Mode

```bash
export FLASK_ENV=development
cd backend
python main.py
```

## 📈 Scaling Considerations

- **Horizontal Scaling**: Multiple Flask instances behind load balancer
- **File Storage**: Consider distributed file system for multiple servers
- **Database**: Supabase handles scaling automatically
- **Processing**: Make.com handles workflow scaling

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 📱 Instagram Integration

For detailed Instagram integration instructions, see:

- [Instagram Integration Guide](docs/instagram-integration-guide.md)

## 🆘 Support

For issues and questions:

- Check the troubleshooting section
- Review the setup guide in `docs/`
- Open an issue on GitHub

---

**Note**: This system is designed for cost-effective processing of large video files while maintaining full automation capabilities through Make.com integration. Currently configured for local development with ngrok - deployment requires URL updates as noted above.
