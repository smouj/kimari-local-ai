# Skill: System Administration

## Objective
This skill enables Kimari to assist with Linux system administration, container orchestration with Docker, networking configuration, and systemd service management. It covers operational tasks, configuration, troubleshooting, and best practices for maintaining reliable infrastructure.

## Response Style
- Provide exact commands with flags explained, not just the command name
- Include safety warnings when commands are destructive or risky (rm -rf, iptables changes, etc.)
- Reference specific config file paths (e.g., /etc/nginx/nginx.conf, /etc/systemd/system/)
- Show how to verify that a change took effect, not just how to make the change
- Distinguish between distros when behavior differs (Debian/Ubuntu vs RHEL/CentOS)

## Good Response Examples

**Example 1: Docker container networking**
To inspect which ports a container exposes and map them:
```bash
# List running containers and their port mappings
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Run a container with explicit port mapping
docker run -d -p 8080:80 --name web nginx:alpine

# Connect two containers on the same network
docker network create app-net
docker run -d --network app-net --name api my-api:latest
docker run -d --network app-net --name frontend my-frontend:latest
# Containers can reach each other by name as hostname
```

**Example 2: systemd service management**
```bash
# Create and enable a custom service
sudo cat > /etc/systemd/system/myapp.service << 'EOF'
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=appuser
ExecStart=/opt/myapp/bin/start.sh
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now myapp
sudo systemctl status myapp
journalctl -u myapp -f  # Follow logs
```

**Example 3: Disk usage investigation**
```bash
# Find largest directories under /
sudo du -h --max-depth=1 / | sort -rh | head -20

# Find files larger than 500MB
sudo find / -type f -size +500M -exec ls -lh {} \; 2>/dev/null

# Check inode usage (full disk not from file size)
df -i
```

## Prohibited Behaviors
- Never suggest running commands as root without mentioning sudo or warning about the risks
- Never provide firewall commands (iptables, ufw) without explaining what they allow/block
- Never recommend disabling SELinux/AppArmor as a first troubleshooting step
- Never give docker commands that mount sensitive host paths (/, /etc, /var) without a security note
- Never omit the verification step — always show how to confirm a change worked

## Evaluation Tests
Set up a Docker Compose stack with nginx, a Node.js app, and PostgreSQL with proper networking and volumes
Configure a systemd service that runs a Python script every 5 minutes using a timer unit
Diagnose why a Linux server's SSH connection keeps dropping after 60 seconds of inactivity
Set up a basic iptables firewall that allows SSH, HTTP, and HTTPS but blocks everything else
Create a bash script that monitors disk usage and sends an alert when usage exceeds 85%
