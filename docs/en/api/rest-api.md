---
title: REST API Overview
description: Complete REST API documentation for omegaUp
icon: bootstrap/cloud
---

# omegaUp REST API

omegaUp provides a comprehensive REST API that can be accessed directly. All endpoints use standard HTTP methods (`GET` or `POST`) and return JSON-formatted responses.

## Base URL

All API endpoints are prefixed with:

```
https://omegaup.com/api/
```

In this documentation, only the part of the URL **after** this prefix is shown.

## Authentication

!!! warning "HTTPS Required"
    Only HTTPS connections are allowed. HTTP requests will return `HTTP 301 Permanent Redirect`.

Some endpoints are public and require no authentication. Protected endpoints require authentication via an `auth_token` obtained from the [`user/login`](users.md#login) endpoint.

The token must be included in a cookie named `ouat` (omegaUp Auth Token) for authenticated requests.

!!! important "Single Session"
    omegaUp supports only one active session at a time. Logging in programmatically will invalidate your browser session, and vice versa.

## Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "status": "ok",
  "data": { ... }
}
```

### Error Response

```json
{
  "status": "error",
  "error": "Error message",
  "errorcode": 400
}
```

## API Categories

- **[Contests API](contests.md)** - Contest management and participation
- **[Problems API](problems.md)** - Problem creation and management
- **[Users API](users.md)** - User management and authentication
- **[Runs API](runs.md)** - Submission handling and results
- **[Clarifications API](clarifications.md)** - Contest clarifications

## Example: Get Server Time

This is a public endpoint that doesn't require authentication:

**Request:**
```bash
GET https://omegaup.com/api/time/get/
```

**Response:**
```json
{
  "time": 1436577101,
  "status": "ok"
}
```

### Endpoint Details

**`GET time/get/`**

Returns the current UNIX timestamp according to the server's internal clock. Useful for synchronizing local clocks.

| Field   | Type   | Description                                      |
|---------|--------|--------------------------------------------------|
| status  | string | Returns `"ok"` if the request was successful |
| time    | int    | UNIX timestamp representing the server time      |

**Required Permissions:** None

## Complete endpoint catalog

For an **exhaustive** list of API methods grouped by controller, see the auto-generated **[Controllers README](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/README.md)** in the omegaUp repository. The human-written pages here (`users.md`, `contests.md`, …) focus on the most common flows; the README is the best reference when you need a specific `apiSomething` name.

## Rate Limiting

Some endpoints have rate limits:

- **Submissions**: One submission per problem every 60 seconds
- **API Calls**: Varies by endpoint

Rate limit exceeded responses:

```json
{
  "status": "error",
  "error": "Rate limit exceeded",
  "errorcode": 429
}
```

## Related Documentation

- **[Authentication Guide](authentication.md)** - Detailed authentication flow
- **[Architecture Overview](../architecture/index.md)** - System architecture
- **[Development Guides](../development/index.md)** - Using the API in development

---

**Ready to use the API?** Browse the [API categories](#api-categories) or start with [Authentication](authentication.md).
