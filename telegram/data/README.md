# Token Storage Directory

This directory is used to store user authentication tokens locally.

## Files:
- `user_tokens.json` - Stores user JWT tokens (access and refresh tokens)

## Security Note:
In production, consider using a more secure storage solution like:
- Redis
- Encrypted database
- Secure key-value store

The current file-based approach is suitable for development and small deployments.
