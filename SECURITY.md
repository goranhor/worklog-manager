# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.4.x   | :white_check_mark: |
| 1.3.x   | :white_check_mark: |
| < 1.3   | :x:                |

## Reporting a Vulnerability

We take the security of Worklog Manager seriously. If you have discovered a security vulnerability, we appreciate your help in disclosing it to us in a responsible manner.

### Please do the following:

1. **DO NOT** open a public issue or pull request
2. **Email** security details to the project maintainers
3. **Include** the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

### What to expect:

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
2. **Investigation**: We will investigate the issue and determine its severity
3. **Resolution**: We will work on a fix and notify you of the timeline
4. **Disclosure**: Once patched, we will publicly disclose the vulnerability with credit to you (if desired)

## Security Best Practices

### For Users

When using Worklog Manager, follow these security best practices:

1. **Keep Updated**: Always use the latest version of the application
2. **File Permissions**: Ensure proper file permissions on the database and config files
3. **Backup Data**: Regularly backup your worklog data
4. **Local Storage**: Keep the database file in a secure location
5. **Access Control**: Limit access to the application directory on shared systems

### For Developers

If you're contributing to Worklog Manager:

1. **Input Validation**: Always validate and sanitize user input
2. **SQL Injection**: Use parameterized queries (already implemented via SQLAlchemy)
3. **File Operations**: Validate file paths to prevent directory traversal
4. **Dependencies**: Keep dependencies updated and monitor for vulnerabilities
5. **Sensitive Data**: Never commit sensitive data (passwords, keys) to the repository
6. **Code Review**: All code changes should be reviewed before merging

## Known Security Considerations

### Data Storage

- **SQLite Database**: Stored locally without encryption by default
  - Consider disk-level encryption for sensitive environments
  - Database file is not password-protected
  
- **Log Files**: May contain sensitive information
  - Stored in plain text in `logs/` directory
  - Automatically rotated daily
  - Consider log retention policies

- **Backup Files**: Contain complete database copies
  - Stored unencrypted in `backups/` directory
  - Should be protected at the file system level

### Configuration

- **config.ini**: Contains application settings
  - No sensitive credentials by default
  - File permissions should restrict access on shared systems

### Export Files

- **Exported Reports**: May contain sensitive work data
  - CSV, JSON, PDF files stored in `exports/` directory
  - Users should manage export file security based on data sensitivity

## Security Features

### Implemented Protections

1. **Input Validation**: All user inputs are validated before processing
2. **SQL Injection Protection**: Using parameterized queries via SQLAlchemy ORM
3. **Path Traversal Protection**: File paths are validated and sanitized
4. **State Validation**: Application state transitions are validated to prevent data corruption
5. **Error Handling**: Comprehensive error handling prevents information leakage
6. **Audit Trail**: Complete action logging for accountability

### Recommendations for Production Use

For organizations deploying Worklog Manager in production:

1. **Implement file-level or disk-level encryption** for sensitive data
2. **Configure backup retention policies** appropriate for your environment
3. **Set restrictive file permissions** on application directories
4. **Monitor log files** for suspicious activity
5. **Implement network isolation** if running on shared systems
6. **Regular updates**: Subscribe to release notifications
7. **Access control**: Limit user access to the application directory

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported releases
4. Release new versions as soon as possible
5. Publicly announce the vulnerability after patch is available

## Contact

For security concerns, please contact the project maintainers through GitHub issues (for non-sensitive matters) or via direct communication for sensitive security issues.

## Acknowledgments

We would like to thank the following individuals for responsibly disclosing security vulnerabilities:

*(List will be updated as security reports are received and resolved)*

---

**Last Updated**: October 21, 2025
