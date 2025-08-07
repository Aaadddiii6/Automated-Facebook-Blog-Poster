# Dual Flow System Documentation

## Overview

The system now supports two different workflows for content generation:

1. **Video Upload Flow** (Original): Upload video → Cloudinary → Assembly API → OpenAI → Facebook
2. **Meeting ID Flow** (New): Meeting ID → Supabase → OpenAI → Facebook

## Architecture

### Video Upload Flow

```
Frontend → Backend → Cloudinary → Assembly API → Make.com → OpenAI → Facebook
```

### Meeting ID Flow

```
Frontend → Backend → Supabase → Make.com → OpenAI → Facebook
```

## API Endpoints

### Video Upload Flow

- **POST** `/api/upload` - Upload video file
- **GET** `/api/upload/status/<meeting_id>` - Get processing status

### Meeting ID Flow

- **POST** `/api/process-meeting` - Process meeting ID from Supabase

### Shared Endpoints

- **POST** `/api/webhook` - Make.com webhook handler (supports both flows)
- **GET** `/api/meetings` - List all meetings
- **GET** `/api/meetings/<meeting_id>` - Get meeting details

## Database Schema Changes

### Meetings Table

- Added `supabase_meeting_id` (UUID) - Links to Supabase meeting
- Added unique constraint to prevent duplicate processing

### Processing Logs Table

- Added `source` (VARCHAR) - Tracks flow type ('video_upload' or 'meeting_id')

## Environment Variables

### New Variables

```bash
# Supabase Configuration
SUPABASE_SERVICE_KEY=your-service-key-here
```

### Required Variables for Meeting ID Flow

```bash
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here
MAKE_WEBHOOK_URL=https://hook.eu1.make.com/your-webhook-url
```

## Make.com Webhook Integration

### Video Upload Flow Webhook

```json
{
  "meeting_id": "uuid",
  "video_id": "uuid",
  "step": "transcription_complete",
  "data": {
    "transcript": "...",
    "summary": "..."
  }
}
```

### Meeting ID Flow Webhook

```json
{
  "meeting_id": "uuid",
  "step": "transcription_complete",
  "data": {
    "transcript": "...",
    "summary": "...",
    "source": "supabase",
    "supabase_meeting_id": "uuid"
  }
}
```

## Frontend Implementation

### Mode Toggle

The frontend now includes a toggle between:

- 📹 Video Upload
- 🆔 Meeting ID

### Video Upload Form

- File drag & drop
- Meeting title, description, organization ID
- Zoom meeting ID (optional)

### Meeting ID Form

- Meeting ID input
- Organization ID
- Fetches transcript from Supabase

## Supabase Integration

### Required Supabase Table Structure

```sql
CREATE TABLE meetings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT,
  description TEXT,
  transcript TEXT,
  summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### API Endpoint

The system expects Supabase to have a REST API endpoint:

```
GET /rest/v1/meetings?id=eq.{meeting_id}&select=*
```

## Error Handling

### Video Upload Flow Errors

- File size exceeded
- Invalid file type
- Cloudinary upload failure
- Assembly API failure

### Meeting ID Flow Errors

- Invalid meeting ID format
- Meeting not found in Supabase
- No transcript available
- Supabase API failure

## Monitoring and Logging

### Processing Logs

All processing steps are logged with:

- Meeting ID
- Step type
- Status
- Source (video_upload or meeting_id)
- Timestamp
- Additional details

### Database Views

```sql
-- View meetings with their flow source
SELECT * FROM meetings_with_source;
```

## Security Considerations

### API Keys

- Supabase service key should have minimal required permissions
- Make.com webhook should be secured with authentication
- All API keys should be stored in environment variables

### Data Validation

- Meeting ID format validation (UUID)
- Organization ID validation
- Transcript content validation

## Deployment

### Database Migration

Run the migration script:

```bash
psql -d your_database -f scripts/add-meeting-id-support.sql
```

### Environment Setup

1. Add `SUPABASE_SERVICE_KEY` to environment variables
2. Configure Supabase URL and API key
3. Update Make.com webhook to handle both flow types

### Testing

1. Test video upload flow (existing functionality)
2. Test meeting ID flow with valid Supabase meeting
3. Test error handling for invalid meeting IDs
4. Test webhook processing for both flows

## Troubleshooting

### Common Issues

1. **Meeting not found in Supabase**

   - Verify meeting ID exists in Supabase
   - Check Supabase API permissions
   - Verify table name and column names

2. **Webhook processing errors**

   - Check Make.com webhook URL
   - Verify webhook payload format
   - Check database connection

3. **Transcript not available**
   - Ensure meeting has transcript in Supabase
   - Check transcript column name

### Debug Logs

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

## Future Enhancements

1. **Batch Processing** - Process multiple meeting IDs
2. **Transcript Validation** - Quality checks for transcripts
3. **Caching** - Cache frequently accessed meeting data
4. **Analytics** - Track usage of both flows
5. **Notifications** - Email/SMS notifications for processing status
