#!/usr/bin/env bash
# Harden Ubuntu server for AI Social Media Post Generator
set -euxo pipefail

# UFW rules
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80
ufw allow 443
ufw deny 5000
ufw --force enable

# Fail2ban install & enable
apt-get update -y
apt-get install -y fail2ban
cat >/etc/fail2ban/jail.local <<'EOF'
[sshd]
enabled = true
port    = ssh
logpath = /var/log/auth.log
maxretry = 5
bantime  = 1h
EOF
systemctl enable --now fail2ban

# Disable password auth over SSH (assumes key already installed)
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl reload sshd

echo "Security hardening complete."
