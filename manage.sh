#!/bin/bash

# Telegram Bot Management Script
# Provides commands to install, start, stop, and manage the bot

set -e

# Configuration
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_NAME="iprn-telegram-bot"
BOT_SCRIPT="$BOT_DIR/bot.py"
VENV_DIR="$BOT_DIR/venv"
PID_FILE="$BOT_DIR/bot.pid"
LOG_FILE="$BOT_DIR/bot.log"
SERVICE_NAME="iprn-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root (needed for systemd operations)
check_root() {
    if [ "$EUID" -ne 0 ]; then
        return 1
    fi
    return 0
}

# Install dependencies and setup virtual environment
install() {
    print_info "Installing Telegram bot..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment and install dependencies
    print_info "Installing Python dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r "$BOT_DIR/requirements.txt"
    deactivate
    print_success "Dependencies installed"
    
    # Check if .env file exists
    if [ ! -f "$BOT_DIR/.env" ]; then
        print_warning ".env file not found"
        print_info "Please create .env file from .env.example and add your bot token:"
        print_info "  cp .env.example .env"
        print_info "  nano .env"
    else
        print_success ".env file found"
    fi
    
    # Make bot.py executable
    chmod +x "$BOT_SCRIPT"
    
    print_success "Installation completed!"
    print_info "Next steps:"
    print_info "  1. Configure your bot token in .env file"
    print_info "  2. Run './manage.sh start' to start the bot"
}

# Start the bot
start() {
    print_info "Starting Telegram bot..."
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Bot is already running (PID: $PID)"
            return 0
        else
            print_info "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi
    
    # Check if .env file exists
    if [ ! -f "$BOT_DIR/.env" ]; then
        print_error ".env file not found. Please create it from .env.example"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found. Please run './manage.sh install' first"
        exit 1
    fi
    
    # Export environment variables from .env
    export $(cat "$BOT_DIR/.env" | grep -v '^#' | xargs)
    
    # Start the bot in background
    source "$VENV_DIR/bin/activate"
    nohup python3 "$BOT_SCRIPT" >> "$LOG_FILE" 2>&1 &
    BOT_PID=$!
    echo $BOT_PID > "$PID_FILE"
    deactivate
    
    # Wait a moment and check if it's still running
    sleep 2
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        print_success "Bot started successfully (PID: $BOT_PID)"
        print_info "Log file: $LOG_FILE"
    else
        print_error "Bot failed to start. Check log file: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Stop the bot
stop() {
    print_info "Stopping Telegram bot..."
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "Bot is not running (no PID file found)"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID"
        
        # Wait for process to stop
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Bot did not stop gracefully, forcing..."
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        print_success "Bot stopped"
    else
        print_warning "Bot process not found (removing stale PID file)"
        rm -f "$PID_FILE"
    fi
}

# Restart the bot
restart() {
    print_info "Restarting Telegram bot..."
    stop
    sleep 2
    start
}

# Check bot status
status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_success "Bot is running (PID: $PID)"
            
            # Show process info
            ps -p "$PID" -o pid,ppid,cmd,%mem,%cpu,etime
            
            # Show last few log lines if log file exists
            if [ -f "$LOG_FILE" ]; then
                echo ""
                print_info "Recent logs:"
                tail -n 10 "$LOG_FILE"
            fi
        else
            print_warning "Bot is not running (stale PID file found)"
            return 1
        fi
    else
        print_info "Bot is not running"
        return 1
    fi
}

# View logs
logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_warning "Log file not found: $LOG_FILE"
        return 1
    fi
    
    if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
        print_info "Following log file (Ctrl+C to stop)..."
        tail -f "$LOG_FILE"
    else
        print_info "Showing last 50 lines of log file..."
        tail -n 50 "$LOG_FILE"
    fi
}

# Setup autostart with systemd
autostart() {
    print_info "Setting up autostart..."
    
    if ! check_root; then
        print_error "This command requires root privileges"
        print_info "Please run with sudo: sudo ./manage.sh autostart"
        exit 1
    fi
    
    # Create systemd service file
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=IPRN Telegram Bot
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$BOT_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$BOT_DIR/.env
ExecStart=$VENV_DIR/bin/python3 $BOT_SCRIPT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable the service
    systemctl enable "$SERVICE_NAME"
    
    print_success "Autostart enabled"
    print_info "Service will start automatically on system boot"
    print_info "You can start it now with: sudo systemctl start $SERVICE_NAME"
}

# Check autostart status
autostart_status() {
    if ! check_root; then
        # Try to check without root if possible
        if [ -f "$SERVICE_FILE" ]; then
            print_info "Service file exists: $SERVICE_FILE"
            systemctl is-enabled "$SERVICE_NAME" 2>/dev/null && \
                print_success "Autostart is enabled" || \
                print_info "Autostart is disabled"
            
            systemctl is-active "$SERVICE_NAME" 2>/dev/null && \
                print_success "Service is active" || \
                print_info "Service is not active"
        else
            print_info "Service is not configured"
        fi
    else
        if [ -f "$SERVICE_FILE" ]; then
            print_success "Service file exists: $SERVICE_FILE"
            systemctl status "$SERVICE_NAME" --no-pager
        else
            print_info "Service is not configured"
            print_info "Run 'sudo ./manage.sh autostart' to enable autostart"
        fi
    fi
}

# Disable autostart
disable_autostart() {
    print_info "Disabling autostart..."
    
    if ! check_root; then
        print_error "This command requires root privileges"
        print_info "Please run with sudo: sudo ./manage.sh disable-autostart"
        exit 1
    fi
    
    if [ ! -f "$SERVICE_FILE" ]; then
        print_warning "Service is not configured"
        return 0
    fi
    
    # Stop the service if running
    systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    
    # Disable the service
    systemctl disable "$SERVICE_NAME"
    
    # Remove service file
    rm -f "$SERVICE_FILE"
    
    # Reload systemd
    systemctl daemon-reload
    
    print_success "Autostart disabled"
}

# Show help
show_help() {
    echo "Telegram Bot Management Script"
    echo ""
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install              Install dependencies and setup environment"
    echo "  start                Start the bot"
    echo "  stop                 Stop the bot"
    echo "  restart              Restart the bot"
    echo "  status               Check bot status"
    echo "  logs [-f]            Show logs (-f to follow)"
    echo "  autostart            Enable autostart (requires sudo)"
    echo "  autostart-status     Check autostart status"
    echo "  disable-autostart    Disable autostart (requires sudo)"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./manage.sh install"
    echo "  ./manage.sh start"
    echo "  ./manage.sh logs -f"
    echo "  sudo ./manage.sh autostart"
}

# Main script
case "${1:-}" in
    install)
        install
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    autostart)
        autostart
        ;;
    autostart-status)
        autostart_status
        ;;
    disable-autostart)
        disable_autostart
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        print_error "No command specified"
        echo ""
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
