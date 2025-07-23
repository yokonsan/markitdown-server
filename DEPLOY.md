# Docker deployment documentation

## Quick Start

1. **Environment Setup**
   ```bash
   cp env.example .env
   # Edit .env file with your configurations
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Check service status**
   ```bash
   docker-compose ps
   ```

4. **View logs**
   ```bash
   docker-compose logs -f [service-name]
   ```

## Service URLs

- **API Service**: http://localhost:8000
- **MinIO Console**: http://localhost:9001 (admin/admin123456)
- **MinIO API**: http://localhost:9000
- **Redis**: localhost:6379

## Common Commands

### Development Mode
```bash
# Rebuild and restart
docker-compose up --build -d

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

### Production Mode
```bash
# Scale workers
docker-compose up -d --scale celery-worker=3

# View resource usage
docker stats
```

### Database Management
```bash
# Backup MinIO data
docker run --rm -v tools-api_minio_data:/data -v $(pwd):/backup alpine tar czf /backup/minio-backup.tar.gz /data

# Restore MinIO data
docker run --rm -v tools-api_minio_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/minio-backup.tar.gz --strip 1"
```

## Health Checks

Each service has health checks configured:
- **API**: http://localhost:8000/health
- **Redis**: redis-cli ping
- **MinIO**: http://localhost:9000/minio/health/live

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yaml
2. **Permission issues**: Ensure Docker daemon has proper permissions
3. **Memory issues**: Adjust Docker resource limits

### Debug Mode
```bash
# Start with development configuration
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d
```

## Security Notes

- Change default credentials in production
- Use proper SSL certificates
- Configure firewall rules
- Regular security updates

## Performance Tuning

### Redis
- Adjust memory limits in docker-compose.yaml
- Configure persistence settings

### Celery
- Scale workers based on load
- Monitor task queue length
- Configure concurrency settings

### MinIO
- Use SSD storage for better performance
- Configure erasure coding for data protection