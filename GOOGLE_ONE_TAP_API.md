# Google One Tap Sign-In API

## Overview

The Google One Tap sign-in endpoint provides a streamlined authentication flow for Google One Tap integration. Unlike the traditional OAuth flow, this endpoint accepts a Google ID token directly and handles user authentication/registration without requiring redirects.

## Endpoint

```
POST /api/v1/auth/google/one-tap
```

## Request Body

```json
{
  "id_token": "google_id_token_here",
  "anonymous_user_id": "optional_anonymous_user_id"
}
```

### Fields

- **`id_token`** (required): The Google ID token received from Google One Tap
- **`anonymous_user_id`** (optional): If provided, this anonymous user will be converted to a social user

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "access_token": "jwt_access_token_here",
  "refresh_token": "jwt_refresh_token_here",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_email": "user@example.com"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid ID token: [error details]"
}
```

#### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "id_token"],
      "msg": "Field required",
      "input": {},
      "url": "https://errors.pydantic.dev/2.5/v/missing"
    }
  ]
}
```

#### 500 Internal Server Error

```json
{
  "detail": "Failed to process Google One Tap sign-in: [error details]"
}
```

#### 501 Not Implemented

```json
{
  "detail": "Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
}
```

## How It Works

1. **Token Verification**: The endpoint verifies the Google ID token using Google's public keys
2. **User Lookup**: Checks if a user with the email exists in the database
3. **Profile Update**: If user exists, updates their profile with latest Google information
4. **Social Account Management**: Ensures the user has a Google social account
5. **Authentication**: Generates and returns JWT access and refresh tokens

## Use Cases

### Frontend Integration

```javascript
// Example frontend implementation
async function handleGoogleOneTap(idToken, anonymousUserId = null) {
  try {
    const response = await fetch("/api/v1/auth/google/one-tap", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_token: idToken,
        anonymous_user_id: anonymousUserId,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      // Store tokens and redirect user
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      // Handle successful sign-in
    } else {
      // Handle error
      const error = await response.json();
      console.error("Sign-in failed:", error);
    }
  } catch (error) {
    console.error("Network error:", error);
  }
}
```

### Anonymous User Conversion

```javascript
// Convert anonymous user to social user
const anonymousUserId = getAnonymousUserId(); // Get from current session
handleGoogleOneTap(googleIdToken, anonymousUserId);
```

## Security Features

- **ID Token Verification**: Uses Google's public keys to verify token authenticity
- **CSRF Protection**: No redirects, direct token exchange
- **Input Validation**: Pydantic schema validation for all inputs
- **Error Handling**: Comprehensive error handling and logging

## Differences from Traditional OAuth

| Feature         | Traditional OAuth      | One Tap                      |
| --------------- | ---------------------- | ---------------------------- |
| Flow            | Redirect-based         | Direct token exchange        |
| User Experience | Multiple redirects     | Single API call              |
| Implementation  | Complex PKCE flow      | Simple ID token verification |
| Use Case        | Full OAuth integration | Quick sign-in                |

## Configuration

Ensure the following environment variables are set:

```bash
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## Testing

### Valid Request

```bash
curl -X POST "http://localhost:8000/api/v1/auth/google/one-tap" \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "valid_google_id_token",
    "anonymous_user_id": "optional_anon_id"
  }'
```

### Invalid Request (Missing Token)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/google/one-tap" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Error Handling

The endpoint handles various error scenarios:

- **Invalid ID Token**: Returns 400 with detailed error message
- **Missing Configuration**: Returns 501 if Google OAuth not configured
- **Database Errors**: Returns 500 with error details
- **Validation Errors**: Returns 422 for malformed requests

## Logging

All operations are logged with appropriate log levels:

- `INFO`: Successful operations and important steps
- `ERROR`: Failed operations with error details
- `DEBUG`: Detailed debugging information

## Rate Limiting

Consider implementing rate limiting for this endpoint to prevent abuse:

- Limit requests per IP address
- Implement exponential backoff for failed attempts
- Monitor for suspicious activity patterns

## Best Practices

1. **Frontend**: Always handle errors gracefully and provide user feedback
2. **Security**: Never log or expose ID tokens in production
3. **User Experience**: Implement loading states during authentication
4. **Fallback**: Provide alternative sign-in methods if One Tap fails
5. **Monitoring**: Track success/failure rates and response times
