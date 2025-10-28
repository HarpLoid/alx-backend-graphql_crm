# CRM Celery Beat Weekly Report Setup

## Requirements

- Redis
- Celery
- Django Celery Beat

## Installation

```bash
    sudo apt install redis-server
    pip install -r requirements.txt
    python manage.py migrate
    celery -A crm worker -l info
    celery -A crm beat -l info
```

Verify logs using:

```bash
    cat /tmp/crm_report_log.txt
```
