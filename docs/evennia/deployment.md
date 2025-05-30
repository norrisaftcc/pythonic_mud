# Deployment Guide

## Recommended VPS Providers

For deployment, a VPS (Virtual Private Server) is recommended due to websocket requirements:

- **DigitalOcean**: $5/month basic droplet
- **Linode**: $5/month entry-level plan
- **AWS Lightsail**: Starting at $3.50/month

## Basic Deployment Process

1. Set up a VPS with Python 3.10+
2. Clone the repository
3. Install requirements
4. Configure the server for production use
5. Run as a service using systemd

## Connection Information

- **Web client**: http://localhost:4001
- **Telnet client**: localhost:4000
- **Admin interface**: http://localhost:4001/admin/

## Production Considerations

- Configure proper firewall rules
- Set up SSL certificates for web access
- Use a process manager (systemd recommended)
- Configure database backups
- Monitor server resources