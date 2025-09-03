# API Documentation

This document provides detailed information about the Secure Azure AI Agent API endpoints and usage.

## Base URL

- Local Development: `http://localhost:8000`
- Production: Your deployed Azure App Service URL

## Authentication

The API uses Azure AD authentication for enterprise deployments. For local development, ensure your Azure credentials are properly configured.

## Endpoints

### Health Check

**GET** `/health`

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-03T10:00:00Z"
}
```

### Chat Completion

**POST** `/chat`

Send a message to the Azure troubleshooting agent and receive a response.

**Request Body:**
```json
{
  "message": "I'm having issues with my Azure App Service deployment",
  "session_id": "optional-session-identifier"
}
```

**Response (Streaming):**
The endpoint returns a streaming response with Server-Sent Events (SSE) format.

**Example Response Stream:**
```
data: {"type": "start", "message": "Processing your request..."}

data: {"type": "content", "message": "I can help you troubleshoot your Azure App Service deployment. Let me analyze the common issues..."}

data: {"type": "content", "message": "Based on your description, here are the most likely causes..."}

data: {"type": "end", "message": ""}
```

### Chat History

**GET** `/chat/history/{session_id}`

Retrieve chat history for a specific session.

**Response:**
```json
{
  "session_id": "session-identifier",
  "messages": [
    {
      "role": "user",
      "content": "I'm having issues with my Azure App Service deployment",
      "timestamp": "2025-09-03T10:00:00Z"
    },
    {
      "role": "assistant", 
      "content": "I can help you troubleshoot your Azure App Service deployment...",
      "timestamp": "2025-09-03T10:00:30Z"
    }
  ]
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad Request - Invalid input parameters
- `401`: Unauthorized - Authentication required
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server-side error

**Error Response Format:**
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request message is required",
    "details": "Additional error context"
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Per User**: 100 requests per minute
- **Per Session**: 10 concurrent streaming connections

## Agent Types

The system includes multiple specialized agents:

1. **Triage Agent**: Initial request classification and routing
2. **Technical Support Agent**: General Azure troubleshooting
3. **Escalation Agent**: Complex issue handling
4. **Foundry Technical Support Agent**: Azure AI Foundry specific issues

## Telemetry

All API calls are tracked using OpenTelemetry for monitoring and observability. Telemetry data includes:

- Request/response times
- Agent invocation metrics
- Error rates and types
- User interaction patterns

## Best Practices

1. **Session Management**: Use consistent session IDs for conversation continuity
2. **Error Handling**: Implement proper error handling for streaming responses
3. **Rate Limiting**: Respect rate limits and implement exponential backoff
4. **Security**: Never log or expose sensitive Azure credentials
5. **Monitoring**: Monitor API health and performance metrics
