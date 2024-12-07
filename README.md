# Error Management System

A secure, containerized system for autonomous error detection and fixing in development projects, featuring a real-time monitoring dashboard.

## Features

- Real-time error detection and fixing
- Multi-project support
- Secure containerized environment
- Interactive dashboard
- Agent-based architecture
- Comprehensive monitoring

## Prerequisites

- Docker Desktop with Kubernetes enabled
- Node.js 14+ and npm
- Python 3.8+
- OpenSSL for certificate generation

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/error-management-system.git
cd error-management-system
```

2. Setup the system:
```bash
chmod +x scripts/*.sh
./scripts/setup_dashboard.sh
```

3. Start the system:
```bash
# Production mode
./scripts/run_system.sh

# OR Development mode
./scripts/dev.sh
```

The dashboard will be available at:
- Production: http://localhost:8080
- Development: http://localhost:3000

## System Architecture

### Components

1. **Error Management Service**
   - Real-time error detection
   - Automated fixing
   - Project isolation
   - Security management

2. **Dashboard**
   - System monitoring
   - Project management
   - Agent control
   - Security metrics

3. **Agent System**
   - Distributed error handling
   - Resource management
   - Context-aware fixes
   - Automatic scaling

### Security Features

- Containerized isolation
- Certificate-based authentication
- Network policies
- Access control
- Audit logging

## Usage

### Adding Projects

1. Open the dashboard
2. Click "Add Project"
3. Enter the project path
4. Configure monitoring settings

### Managing Agents

1. Navigate to Agent Manager
2. Create/remove agents
3. Monitor agent status
4. View resource usage

### System Controls

- Start/Stop system
- Manage environments
- Configure settings
- View metrics

### Security Monitoring

- View security score
- Monitor access attempts
- Check certificate status
- View audit logs

## Development

### Local Development

```bash
# Start in development mode
./scripts/dev.sh

# Run tests
make test

# Run security checks
make security-check

# Build container
make build
```

### Project Structure

```
.
├── src/
│   ├── error_management/    # Core error management system
│   └── dashboard/          # Web dashboard
├── kubernetes/            # Kubernetes configurations
├── scripts/              # Utility scripts
└── tests/               # Test suite
```

## Configuration

### Environment Variables

```bash
# Required
PROJECT_PATH=/path/to/project
ANTHROPIC_API_KEY=your-api-key

# Optional
SECURE_MODE=1
LOG_LEVEL=INFO
```

### Kubernetes ConfigMap

```yaml
monitoring:
  enabled: true
  interval: 30
  metrics_port: 8080

security:
  secure_mode: true
  token_expiry: 3600
```

## Monitoring

### Metrics

- CPU/Memory usage
- Error counts
- Fix success rate
- Response times

### Logging

View logs:
```bash
# System logs
kubectl logs -f deployment/error-management -n cursor-agent

# Dashboard logs
kubectl logs -f deployment/dashboard -n cursor-agent
```

## Troubleshooting

### Common Issues

1. **Container startup fails**
   - Check Docker status
   - Verify Kubernetes configuration
   - Check resource limits

2. **Dashboard not loading**
   - Verify service status
   - Check browser console
   - Verify network connectivity

3. **Agent connection issues**
   - Check network policies
   - Verify certificates
   - Check agent logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support:
1. Check the documentation
2. Search existing issues
3. Create a new issue

## Security

Report security issues to security@your-org.com

## Acknowledgments

- Cursor AI Team
- Contributors
- Open source community

Last verified: Sun Dec  8 05:49:14 AEDT 2024

