# scriptcrew Deployment Guide

This directory contains all the necessary configuration files and scripts for deploying scriptcrew in development, test, and production environments.

## Directory Structure

```
deployment/
├── nginx/                  # Nginx virtual host configurations
│   ├── dev.scriptcrew.ai-scientia.com.conf
│   ├── test.scriptcrew.ai-scientia.com.conf
│   └── www.scriptcrew.ai-scientia.com.conf
├── gunicorn/              # Gunicorn configurations and service files
│   ├── gunicorn_dev.py
│   ├── gunicorn_prod.py
│   ├── gunicorn_test.py
│   ├── scriptcrew-dev.service
│   ├── scriptcrew-prod.service
│   └── scriptcrew-test.service
└── scripts/               # Utility scripts
    └── server_control.sh  # Service management script
```

## Initial Setup

1. Install required packages:
   ```bash
   apt-get update
   apt-get install -y nginx
   ```

2. Create necessary directories:
   ```bash
   mkdir -p /var/log/gunicorn /var/run/gunicorn
   chown -R root:www-data /var/log/gunicorn /var/run/gunicorn
   ```

3. Set up SSL certificates:
   ```bash
   # For development (self-signed)
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
   -keyout /etc/ssl/private/scriptcrew-dev.key \
   -out /etc/ssl/certs/scriptcrew-dev.crt \
   -subj "/C=US/ST=State/L=City/O=Organization/CN=dev.scriptcrew.ai-scientia.com"

   # For production (use Let's Encrypt or your SSL provider)
   # Place certificates in:
   # - /etc/ssl/private/scriptcrew.key
   # - /etc/ssl/certs/scriptcrew.crt
   ```

4. Configure Nginx:
   ```bash
   # Copy configuration files
   cp nginx/*.conf /etc/nginx/sites-available/

   # Enable sites (example for dev)
   ln -sf /etc/nginx/sites-available/dev.scriptcrew.ai-scientia.com.conf /etc/nginx/sites-enabled/
   
   # Remove default site
   rm -f /etc/nginx/sites-enabled/default

   # Test configuration
   nginx -t

   # Reload Nginx
   systemctl reload nginx
   ```

5. Configure Gunicorn services:
   ```bash
   # Copy service files
   cp gunicorn/scriptcrew-*.service /etc/systemd/system/

   # Reload systemd
   systemctl daemon-reload
   ```

## Service Management

### Using the Control Script

The `server_control.sh` script provides a unified interface for managing services:

```bash
./scripts/server_control.sh [dev|prod|test] [start|stop|restart|status|log]
```

Examples:
```bash
# Start development environment
./scripts/server_control.sh dev start

# Check production status
./scripts/server_control.sh prod status

# Restart test environment
./scripts/server_control.sh test restart

# View all logs for development environment
./scripts/server_control.sh dev log
```

The `log` action shows:
- Last 50 lines of Gunicorn access and error logs
- Last 50 lines of Nginx access and error logs
- Last 50 lines of systemd journal entries
- Last 50 lines of server control script logs for the environment

The script also automatically logs all operations to `/var/log/scriptcrew/server_control.log` with timestamps and detailed status information.

Additional log analysis commands:
```bash
# View server control script logs
tail -f /var/log/scriptcrew/server_control.log

# View last 50 log entries
tail -n 50 /var/log/scriptcrew/server_control.log

# Search logs for specific environment
grep "environment: dev" /var/log/scriptcrew/server_control.log

# Search for errors in logs
grep "Error:" /var/log/scriptcrew/server_control.log
```

### Manual Service Management

#### Gunicorn Services

```bash
# Start service
systemctl start scriptcrew-[dev|prod|test]

# Stop service
systemctl stop scriptcrew-[dev|prod|test]

# Restart service
systemctl restart scriptcrew-[dev|prod|test]

# Check status
systemctl status scriptcrew-[dev|prod|test]

# Enable at boot
systemctl enable scriptcrew-[dev|prod|test]

# Disable at boot
systemctl disable scriptcrew-[dev|prod|test]
```

#### Nginx Service

```bash
# Start Nginx
systemctl start nginx

# Stop Nginx
systemctl stop nginx

# Reload configuration
systemctl reload nginx

# Check status
systemctl status nginx
```

## Logging and Monitoring

### Gunicorn Logs

Each environment has its own log files:

```bash
# Development logs
tail -f /var/log/gunicorn/dev_access.log
tail -f /var/log/gunicorn/dev_error.log

# Production logs
tail -f /var/log/gunicorn/prod_access.log
tail -f /var/log/gunicorn/prod_error.log

# Test logs
tail -f /var/log/gunicorn/test_access.log
tail -f /var/log/gunicorn/test_error.log
```

### Nginx Logs

```bash
# Development environment
tail -f /var/log/nginx/dev.scriptcrew.access.log
tail -f /var/log/nginx/dev.scriptcrew.error.log

# Production environment
tail -f /var/log/nginx/scriptcrew.access.log
tail -f /var/log/nginx/scriptcrew.error.log

# Test environment
tail -f /var/log/nginx/test.scriptcrew.access.log
tail -f /var/log/nginx/test.scriptcrew.error.log
```

### System Journal Logs

View service logs using journalctl:

```bash
# View Gunicorn service logs
journalctl -u scriptcrew-dev
journalctl -u scriptcrew-prod
journalctl -u scriptcrew-test

# Follow logs in real-time
journalctl -u scriptcrew-dev -f

# View logs since last boot
journalctl -u scriptcrew-dev -b

# View logs with timestamps
journalctl -u scriptcrew-dev --output=short-precise
```

## Environment-Specific Notes

### Development Environment
- Runs on port 8000 (Gunicorn) behind Nginx
- Uses self-signed SSL certificates
- Debug mode enabled
- Accessible at https://dev.scriptcrew.ai-scientia.com

### Test Environment
- Runs on port 8001 (Gunicorn) behind Nginx
- Uses self-signed SSL certificates
- Basic authentication enabled
- Accessible at https://test.scriptcrew.ai-scientia.com

### Production Environment
- Uses Unix socket for Gunicorn
- Requires valid SSL certificates
- Enhanced security settings
- Rate limiting enabled
- Accessible at https://www.scriptcrew.ai-scientia.com

## Troubleshooting

1. Check service status:
   ```bash
   systemctl status scriptcrew-[dev|prod|test]
   ```

2. View recent logs:
   ```bash
   journalctl -u scriptcrew-[dev|prod|test] -n 50
   ```

3. Test Nginx configuration:
   ```bash
   nginx -t
   ```

4. Check for port conflicts:
   ```bash
   netstat -tulpn | grep -E ':80|:443|:8000|:8001'
   ```

5. Verify SSL certificates:
   ```bash
   openssl x509 -in /etc/ssl/certs/scriptcrew-[dev|prod|test].crt -text -noout
   ```

## Security Considerations

1. Keep SSL certificates up to date
2. Regularly rotate log files
3. Monitor system resources
4. Keep all packages updated
5. Review Nginx access logs for suspicious activity
6. Maintain proper file permissions
7. Use strong passwords for basic authentication 