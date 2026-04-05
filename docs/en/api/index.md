---
title: API Reference
description: Complete REST API documentation for omegaUp
icon: bootstrap/api
---

# API Reference

omegaUp provides a comprehensive REST API that can be accessed directly. All endpoints use standard HTTP methods (`GET` or `POST`) and return JSON responses.

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

## API Categories

<div class="grid cards" markdown>

-   :material-trophy:{ .lg .middle } __[Contests API](contests.md)__

    ---

    Create, manage, and participate in programming contests.

    [:octicons-arrow-right-24: Browse](contests.md)

-   :material-puzzle:{ .lg .middle } __[Problems API](problems.md)__

    ---

    Create, update, and manage programming problems.

    [:octicons-arrow-right-24: Browse](problems.md)

-   :material-account:{ .lg .middle } __[Users API](users.md)__

    ---

    User management, authentication, and profile operations.

    [:octicons-arrow-right-24: Browse](users.md)

-   :material-code-braces:{ .lg .middle } __[Runs API](runs.md)__

    ---

    Submit code, check status, and retrieve submission results.

    [:octicons-arrow-right-24: Browse](runs.md)

-   :material-message-text:{ .lg .middle } __[Clarifications API](clarifications.md)__

    ---

    Ask and answer questions during contests.

    [:octicons-arrow-right-24: Browse](clarifications.md)

</div>

## Quick Example

Get the current server time (public endpoint):

```bash
curl https://omegaup.com/api/time/get/
```

Response:

```json
{
  "time": 1436577101,
  "status": "ok"
}
```

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "ok",
  "data": { ... }
}
```

Error responses:

```json
{
  "status": "error",
  "error": "Error message",
  "errorcode": 400
}
```

## Complete endpoint catalog

This site documents the main API **categories** in detail. The wiki used to duplicate a very long flat list of every `/api/...` path; the **generated, authoritative index** of controllers and routes lives in the main repository:

**[frontend/server/src/Controllers/README.md](https://github.com/omegaup/omegaup/blob/main/frontend/server/src/Controllers/README.md)**

Routing convention: a request to `/api/<segment>/<action>/` is handled by `<Segment>Controller::api<Action>` in `frontend/server/src/Controllers/` (with the usual PHP naming adjustments). Use the generated README for exact method names and parameters while developing.

## Rate Limiting

Some endpoints have rate limits to prevent abuse:

- **Submissions**: One submission per problem every 60 seconds
- **API Calls**: Varies by endpoint

Rate limit exceeded responses include:

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

**Ready to use the API?** Start with [Authentication](authentication.md) or browse the [API categories](#api-categories) above.
