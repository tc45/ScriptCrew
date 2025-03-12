#!/bin/bash

# Server control script for scriptcrew environments
# Usage: ./server_control.sh [dev|prod|test] [start|stop|restart|status|log]

ENV=$1
ACTION=$2
LOG_FILE="/var/log/scriptcrew/server_control.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log messages
log_message() {
    local message=$1
    echo "[$TIMESTAMP] $message" | tee -a "$LOG_FILE"
}

# Create log directory if it doesn't exist
if [ ! -d "/var/log/scriptcrew" ]; then
    sudo mkdir -p /var/log/scriptcrew
    sudo chown root:www-data /var/log/scriptcrew
    sudo chmod 755 /var/log/scriptcrew
fi

# Check if environment and action are provided
if [ -z "$ENV" ] || [ -z "$ACTION" ]; then
    log_message "Error: Missing required parameters"
    echo "Usage: $0 [dev|prod|test] [start|stop|restart|status|log]"
    exit 1
fi

# Validate environment
if [[ ! "$ENV" =~ ^(dev|prod|test)$ ]]; then
    log_message "Error: Invalid environment '$ENV'. Use dev, prod, or test"
    echo "Invalid environment. Use dev, prod, or test"
    exit 1
fi

# Validate action
if [[ ! "$ACTION" =~ ^(start|stop|restart|status|log)$ ]]; then
    log_message "Error: Invalid action '$ACTION'. Use start, stop, restart, status, or log"
    echo "Invalid action. Use start, stop, restart, status, or log"
    exit 1
fi

# Service names
GUNICORN_SERVICE="scriptcrew-${ENV}.service"
NGINX_CONFIG="scriptcrew-${ENV}.conf"

# Function to check if file exists and is readable
check_log_file() {
    local file=$1
    local description=$2
    if [ ! -f "$file" ]; then
        echo "Warning: $description not found at $file"
        return 1
    elif [ ! -r "$file" ]; then
        echo "Warning: $description exists but is not readable at $file"
        return 1
    fi
    return 0
}

# Function to safely display log file
display_log() {
    local file=$1
    local lines=${2:-50}
    local description=$3
    
    if check_log_file "$file" "$description"; then
        echo "=== $description (last $lines lines) ==="
        tail -n "$lines" "$file" || echo "Error reading log file"
        echo
    fi
}

# Function to view logs
view_logs() {
    local gunicorn_access="/var/log/gunicorn/${ENV}_access.log"
    local gunicorn_error="/var/log/gunicorn/${ENV}_error.log"
    local nginx_access="/var/log/nginx/${ENV}.scriptcrew.access.log"
    local nginx_error="/var/log/nginx/${ENV}.scriptcrew.error.log"
    
    echo "=== Viewing logs for $ENV environment ==="
    echo

    # Gunicorn Logs
    echo "=== Gunicorn Service Logs ==="
    display_log "$gunicorn_access" 50 "Gunicorn Access Log"
    display_log "$gunicorn_error" 50 "Gunicorn Error Log"
    
    # Nginx Logs
    echo "=== Nginx Logs ==="
    display_log "$nginx_access" 50 "Nginx Access Log"
    display_log "$nginx_error" 50 "Nginx Error Log"
    
    # System Journal
    echo "=== System Journal (last 50 lines) ==="
    if ! journalctl -u "scriptcrew-${ENV}" -n 50 --no-pager; then
        echo "Warning: Unable to retrieve journal logs for scriptcrew-${ENV}"
    fi
    echo
    
    # Server Control Script Logs
    echo "=== Server Control Script Logs (last 50 lines) ==="
    if check_log_file "$LOG_FILE" "Server control script log"; then
        grep "environment: $ENV" "$LOG_FILE" | tail -n 50 || echo "No matching log entries found"
    fi
    
    # Summary of warnings if any files were missing
    local missing_files=()
    check_log_file "$gunicorn_access" "Gunicorn Access Log" || missing_files+=("$gunicorn_access")
    check_log_file "$gunicorn_error" "Gunicorn Error Log" || missing_files+=("$gunicorn_error")
    check_log_file "$nginx_access" "Nginx Access Log" || missing_files+=("$nginx_access")
    check_log_file "$nginx_error" "Nginx Error Log" || missing_files+=("$nginx_error")
    check_log_file "$LOG_FILE" "Server Control Script Log" || missing_files+=("$LOG_FILE")
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo
        echo "=== Missing or Unreadable Log Files ==="
        echo "The following log files were not accessible:"
        printf '%s\n' "${missing_files[@]}"
        echo
        echo "This might be normal if services haven't been started yet or if logs haven't been rotated."
        echo "Make sure the services are running and log directories have correct permissions."
    fi
}

# Function to manage services
manage_services() {
    local action=$1
    
    log_message "=== Managing $ENV environment ==="
    echo "=== Managing $ENV environment ==="
    
    # Gunicorn
    log_message "Managing Gunicorn service: $GUNICORN_SERVICE ($action)"
    echo "Managing Gunicorn..."
    if sudo systemctl $action $GUNICORN_SERVICE; then
        log_message "Gunicorn $action completed successfully"
    else
        log_message "Error: Gunicorn $action failed"
    fi
    
    # Nginx
    if [ "$action" == "restart" ]; then
        log_message "Testing Nginx configuration"
        echo "Testing Nginx configuration..."
        if sudo nginx -t; then
            log_message "Nginx configuration test passed"
            echo "Reloading Nginx..."
            if sudo systemctl reload nginx; then
                log_message "Nginx reload completed successfully"
            else
                log_message "Error: Nginx reload failed"
                exit 1
            fi
        else
            log_message "Error: Nginx configuration test failed"
            echo "Nginx configuration test failed!"
            exit 1
        fi
    elif [ "$action" == "start" ]; then
        log_message "Starting Nginx service"
        echo "Starting Nginx..."
        if sudo systemctl start nginx; then
            log_message "Nginx start completed successfully"
        else
            log_message "Error: Nginx start failed"
        fi
    elif [ "$action" == "stop" ]; then
        log_message "Stopping Nginx service"
        echo "Stopping Nginx..."
        if sudo systemctl stop nginx; then
            log_message "Nginx stop completed successfully"
        else
            log_message "Error: Nginx stop failed"
        fi
    fi
}

# Function to check service status
check_status() {
    log_message "=== Checking status for $ENV environment ==="
    echo "=== Status for $ENV environment ==="
    
    echo "Gunicorn status:"
    if systemctl_output=$(sudo systemctl status $GUNICORN_SERVICE); then
        log_message "Gunicorn status: Active"
        echo "$systemctl_output"
    else
        log_message "Gunicorn status: Inactive or failed"
        echo "$systemctl_output"
    fi
    
    echo "Nginx status:"
    if systemctl_output=$(sudo systemctl status nginx); then
        log_message "Nginx status: Active"
        echo "$systemctl_output"
    else
        log_message "Nginx status: Inactive or failed"
        echo "$systemctl_output"
    fi
}

# Execute requested action
log_message "Executing action: $ACTION for environment: $ENV"
case $ACTION in
    start)
        manage_services "start"
        ;;
    stop)
        manage_services "stop"
        ;;
    restart)
        manage_services "restart"
        ;;
    status)
        check_status
        ;;
    log)
        view_logs
        ;;
esac

log_message "Script execution completed"
exit 0 