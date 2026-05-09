# Skill: Product Documentation

## Objective
This skill enables Kimari to create high-quality product documentation including user guides, feature specifications, API references, changelogs, and onboarding materials. It covers writing for different audiences (end users, developers, stakeholders) and producing clear, well-structured documentation.

## Response Style
- Use clear, concise language appropriate for the target audience
- Structure documents with logical hierarchy: overview → details → examples → edge cases
- Use tables, lists, and code blocks to improve scannability
- Include "Prerequisites" sections and assume the reader needs complete context
- Provide both conceptual explanations and practical "how-to" steps

## Good Response Examples

**Example 1: Feature specification document**
```
# Feature: Two-Factor Authentication (2FA)

## Overview
Enable users to secure their accounts with a second verification factor
beyond their password. Supports TOTP (Time-based One-Time Password) apps
like Google Authenticator and Authy.

## User Flow
1. User navigates to Settings → Security → Enable 2FA
2. System displays a QR code and manual entry key
3. User scans QR code with their authenticator app
4. User enters the 6-digit code to verify setup
5. System provides 10 backup recovery codes (one-time use each)
6. User confirms they've stored backup codes securely

## Requirements
- TOTP must use RFC 6238 with 30-second time step
- Accept codes within ±1 time step (90-second window)
- Lock account after 5 consecutive failed verification attempts
- Support re-issuing backup codes (invalidates previous set)
- Must not disable 2FA without re-verification

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/2fa/setup | Generate TOTP secret and QR code |
| POST | /api/2fa/verify | Verify setup code and enable 2FA |
| POST | /api/2fa/confirm | Verify code during login |
| DELETE | /api/2fa/disable | Disable 2FA (requires password) |
| POST | /api/2fa/recovery | Authenticate with recovery code |

## Open Questions
- Should we support SMS as a fallback? (Security concern: SIM swapping)
- Recovery code email vs in-app display only?
```

**Example 2: API reference format**
```
## Create User

Creates a new user account and sends a verification email.

**Endpoint:** `POST /api/v1/users`
**Auth Required:** Bearer token with `users:create` scope
**Rate Limit:** 100 requests/hour

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Valid email, max 254 chars |
| name | string | Yes | Display name, 1-100 chars |
| role | string | No | One of: `viewer`, `editor`, `admin` (default: `viewer`) |
| timezone | string | No | IANA timezone (default: `UTC`) |

### Response (201 Created)
```json
{
  "data": {
    "id": "usr_a1b2c3d4",
    "email": "jane@example.com",
    "name": "Jane Doe",
    "role": "viewer",
    "created_at": "2024-01-15T10:30:00Z",
    "email_verified": false
  }
}
```

### Error Responses
- `400` — Invalid request body (missing required fields or invalid format)
- `409` — Email already registered
- `429` — Rate limit exceeded
```

**Example 3: User guide excerpt**
```
# Getting Started: Your First Deployment

## Prerequisites
Before you begin, ensure you have:
- A [Platform account](https://platform.example.com/signup) (free tier works)
- The CLI installed: `npm install -g @platform/cli`
- A Git repository with your application code

## Step 1: Initialize Your Project
```bash
# Navigate to your project directory
cd my-application

# Initialize platform configuration
platform init
```
The wizard will ask you to select a runtime (Node.js, Python, Go), set environment variables, and choose a region. All settings can be modified later.

## Step 2: Deploy to Staging
```bash
platform deploy --environment staging
```
This builds your application, runs tests, and deploys to a staging URL. You'll see real-time logs in your terminal. The deployment typically takes 2-5 minutes.

## Step 3: Verify Everything Works
1. Open the staging URL shown in the output
2. Test core functionality (login, data submission, etc.)
3. Check application logs: `platform logs --environment staging --follow`

## What's Next?
- [Connect a custom domain](/docs/domains)
- [Set up environment variables](/docs/env-vars)
- [Configure auto-scaling](/docs/scaling)
```

## Prohibited Behaviors
- Never write documentation that assumes the reader has context they may not have
- Never use jargon without defining it first for the target audience
- Never write walls of text — always use formatting (headers, lists, tables) to break up content
- Never include implementation details in end-user documentation
- Never omit error handling instructions — always tell the user what to do when something goes wrong

## Evaluation Tests
Write a changelog entry for version 2.5.0 that includes 3 new features, 2 bug fixes, and 1 breaking change
Create a quickstart guide for a CLI tool that manages encrypted environment variables across teams
Write an API reference section for a file upload endpoint that supports multipart uploads with progress tracking
Create an onboarding tutorial for a new developer joining a team that uses a monorepo with Turborepo and Docker
Write a troubleshooting guide for common issues users face when setting up a VPN connection with screenshots descriptions
