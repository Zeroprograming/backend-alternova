# 📋 Guía Técnica - Backend Alternova

## 🏗️ Arquitectura Detallada

### Estructura de Directorios por Aplicación

#### 👥 Users App

```
users/
├── domain/
│   ├── entities.py              # User, UserProfile entities
│   └── value_objects.py         # UserType, UserStatus, etc.
├── application/
│   ├── dto/                     # UserDTO, ProfileDTO
│   ├── services/
│   │   ├── legacy_auth_services.py
│   │   └── legacy_role_services.py
│   └── use_cases/               # CreateUser, UpdateProfile, etc.
├── infrastructure/
│   ├── models.py               # Django models
│   ├── repositories/
│   │   ├── managers.py
│   │   └── querysets.py
│   └── middleware/
│       └── legacy_middleware.py
├── presentation/
│   ├── views/
│   │   ├── legacy_auth_views.py
│   │   ├── legacy_role_views.py
│   │   └── legacy_views.py
│   ├── serializers/
│   │   └── legacy_serializers.py
│   ├── urls/
│   │   ├── legacy_urls.py
│   │   └── legacy_role_urls.py
│   └── permissions/
│       └── permissions.py
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

#### 📚 Subjects App

```
subjects/
├── domain/
│   ├── entities.py              # Subject, Enrollment entities
│   └── value_objects.py         # SubjectCode, Grade, etc.
├── application/
│   ├── dto/                     # SubjectDTO, EnrollmentDTO
│   ├── services/
│   │   ├── legacy_enrollment_services.py
│   │   └── legacy_academic_services.py
│   └── use_cases/               # EnrollStudent, GradeStudent, etc.
├── infrastructure/
│   ├── models.py               # Django models
│   ├── repositories/
│   │   ├── managers.py
│   │   └── querysets.py
│   └── external/
│       └── decorators.py
├── presentation/
│   ├── views/
│   │   ├── legacy_academic_views.py
│   │   └── legacy_views.py
│   ├── serializers/
│   │   └── legacy_serializers.py
│   ├── urls/
│   │   ├── legacy_urls.py
│   │   └── legacy_academic_urls.py
│   └── permissions/
│       └── permissions.py
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

#### 📊 Reports App

```
reports/
├── domain/
│   ├── entities.py              # Report, ReportTemplate entities
│   └── value_objects.py         # ReportName, FilePath, etc.
├── application/
│   ├── dto/                     # ReportDTO, ReportRequestDTO
│   ├── services/
│   │   ├── legacy_csv_services.py
│   │   ├── advanced_report_services.py
│   │   └── optimized_query_services.py
│   └── use_cases/               # GenerateReport, ExportData, etc.
├── infrastructure/
│   ├── models.py               # Django models
│   ├── repositories/
│   │   ├── managers.py
│   │   └── querysets.py
│   └── external/
│       └── utils.py
├── presentation/
│   ├── views/
│   │   ├── legacy_csv_views.py
│   │   ├── advanced_report_views.py
│   │   └── legacy_views.py
│   ├── serializers/
│   │   └── legacy_serializers.py
│   ├── urls/
│   │   ├── legacy_urls.py
│   │   └── advanced_report_urls.py
│   └── permissions/
│       └── permissions.py
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

#### 🔔 Notifications App

```
notifications/
├── domain/
│   ├── entities.py              # Notification, NotificationTemplate entities
│   └── value_objects.py         # NotificationTitle, EmailAddress, etc.
├── application/
│   ├── dto/                     # NotificationDTO, EmailDTO
│   ├── services/
│   │   ├── legacy_notification_services.py
│   │   ├── advanced_email_services.py
│   │   └── optimized_notification_services.py
│   └── use_cases/               # SendNotification, MarkAsRead, etc.
├── infrastructure/
│   ├── models.py               # Django models
│   ├── repositories/
│   │   ├── managers.py
│   │   └── querysets.py
│   └── external/
│       └── email_utils.py
├── presentation/
│   ├── views/
│   │   ├── legacy_views.py
│   │   └── advanced_notification_views.py
│   ├── serializers/
│   │   └── legacy_serializers.py
│   ├── urls/
│   │   ├── legacy_urls.py
│   │   └── advanced_notification_urls.py
│   └── permissions/
│       └── permissions.py
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

#### 🔧 Common App

```
common/
├── domain/
│   ├── entities.py              # AuditLog, QueryMetrics, CacheEntry
│   └── value_objects.py         # RequestId, ModelName, IPAddress, etc.
├── application/
│   ├── dto/                     # AuditDTO, MetricsDTO
│   ├── services/
│   │   ├── legacy_services.py
│   │   ├── advanced_orm_services.py
│   │   ├── audit_services.py
│   │   └── optimized_query_services.py
│   └── use_cases/               # AuditAction, OptimizeQuery, etc.
├── infrastructure/
│   ├── models.py               # BaseModel, TimeStampedModel
│   ├── audit_models.py         # AuditLog, UserSession
│   ├── repositories/
│   │   ├── managers.py
│   │   └── querysets.py
│   ├── external/
│   │   ├── utils.py
│   │   └── decorators.py
│   ├── middleware/
│   │   ├── advanced_middleware.py
│   │   └── legacy_middleware.py
│   ├── validators.py           # Validadores personalizados
│   ├── admin.py                # Configuración admin
│   ├── signals.py              # Señales Django
│   └── tasks.py                # Tareas Celery
├── presentation/
│   ├── views/
│   │   ├── legacy_views.py
│   │   └── advanced_orm_views.py
│   ├── serializers/             # Serializadores comunes
│   ├── urls/
│   │   └── advanced_orm_urls.py
│   └── permissions/
│       └── permissions.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── models.py                   # Proxy para compatibilidad Django
├── validators.py               # Proxy para compatibilidad
├── audit_services.py           # Proxy para compatibilidad
├── utils.py                    # Proxy para compatibilidad
├── middleware.py               # Proxy para compatibilidad
├── advanced_middleware.py      # Proxy para compatibilidad
└── apps.py                     # Configuración Django
```

## 🔄 Flujo de Datos

### 1. Request Flow

```
Client Request → Middleware → URL Router → View → Serializer → Service → Repository → Database
```

### 2. Response Flow

```
Database → Repository → Service → Serializer → View → Middleware → Client Response
```

### 3. Clean Architecture Flow

```
Presentation Layer → Application Layer → Domain Layer → Infrastructure Layer
```

## 🛡️ Seguridad Implementada

### Autenticación JWT

- **Access Tokens**: Válidos por 5 minutos
- **Refresh Tokens**: Válidos por 1 día
- **Token Verification**: Endpoint para verificar tokens
- **Session Management**: Control de sesiones activas

### Middleware de Seguridad

- **IP Blocking**: Bloqueo de IPs maliciosas
- **Request Logging**: Registro de todas las requests
- **Rate Limiting**: Limitación de requests por usuario
- **CSRF Protection**: Protección CSRF habilitada

### Auditoría

- **Audit Logs**: Registro de todas las operaciones críticas
- **User Sessions**: Control de sesiones de usuario
- **Request Tracking**: Seguimiento de requests y respuestas
- **Error Logging**: Registro de errores y excepciones

## 📊 Performance y Optimización

### ORM Optimizations

- **Select Related**: Optimización de consultas relacionadas
- **Prefetch Related**: Carga anticipada de relaciones
- **Query Optimization**: Análisis y optimización de consultas
- **Database Indexing**: Índices optimizados para consultas frecuentes

### Caching Strategy

- **Redis Cache**: Cache de sesiones y datos frecuentes
- **Query Cache**: Cache de consultas complejas
- **Template Cache**: Cache de templates Django
- **Static Files**: Cache de archivos estáticos

### Monitoring

- **Query Metrics**: Métricas de consultas de base de datos
- **Response Times**: Tiempos de respuesta de APIs
- **Error Rates**: Tasas de error por endpoint
- **User Activity**: Actividad de usuarios en tiempo real

## 🔧 Configuración Avanzada

### Variables de Entorno Detalladas

```env
# Django Core
SECRET_KEY=tu-secret-key-super-seguro
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# Database
DATABASE_URL=postgresql://usuario:password@localhost:5432/alternova_db
DB_ENGINE=django.db.backends.postgresql
DB_NAME=alternova_db
DB_USER=usuario
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=johanjimenez0210@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=johanjimenez0210@gmail.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_ACCEPT_CONTENT=['json']
CELERY_TASK_SERIALIZER='json'
CELERY_RESULT_SERIALIZER='json'
CELERY_TIMEZONE='America/Bogota'

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=True
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Middleware Configuration
ENABLE_IP_BLOCKING=False
ALLOWED_IPS=127.0.0.1,localhost
BLOCKED_IPS=
ENABLE_REQUEST_LOGGING=True
ENABLE_PERFORMANCE_MONITORING=True

# File Storage
MEDIA_URL=/media/
MEDIA_ROOT=media/
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/django.log
CELERY_LOG_FILE=logs/celery.log
```

### Configuración de Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'common': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 🧪 Testing Strategy

### Tipos de Pruebas

1. **Unit Tests**: Pruebas de funciones y métodos individuales
2. **Integration Tests**: Pruebas de integración entre componentes
3. **API Tests**: Pruebas de endpoints de la API
4. **Performance Tests**: Pruebas de rendimiento y carga

### Cobertura de Pruebas

- **Domain Layer**: 100% cobertura
- **Application Layer**: 95% cobertura
- **Infrastructure Layer**: 90% cobertura
- **Presentation Layer**: 85% cobertura

### Ejecutar Pruebas

```bash
# Pruebas unitarias
python manage.py test users.tests.unit
python manage.py test subjects.tests.unit
python manage.py test reports.tests.unit
python manage.py test notifications.tests.unit
python manage.py test common.tests.unit

# Pruebas de integración
python manage.py test users.tests.integration
python manage.py test subjects.tests.integration
python manage.py test reports.tests.integration
python manage.py test notifications.tests.integration
python manage.py test common.tests.integration

# Todas las pruebas
python manage.py test
```

## 🚀 Deployment Checklist

### Pre-deployment

- [ ] Variables de entorno configuradas
- [ ] Base de datos migrada
- [ ] Archivos estáticos recopilados
- [ ] Pruebas ejecutadas y pasadas
- [ ] Logs configurados
- [ ] Backup de datos realizado

### Production Setup

- [ ] Servidor web configurado (Nginx/Apache)
- [ ] WSGI server configurado (Gunicorn/uWSGI)
- [ ] SSL/TLS certificados instalados
- [ ] Firewall configurado
- [ ] Monitoring configurado
- [ ] Backup automático configurado

### Post-deployment

- [ ] Health checks funcionando
- [ ] Logs monitoreados
- [ ] Performance monitoreado
- [ ] Error tracking configurado
- [ ] Alertas configuradas

## 📈 Métricas y KPIs

### Performance Metrics

- **Response Time**: < 200ms promedio
- **Throughput**: > 1000 requests/minuto
- **Error Rate**: < 1%
- **Uptime**: > 99.9%

### Business Metrics

- **User Registration**: Nuevos usuarios por día
- **Active Users**: Usuarios activos por mes
- **API Usage**: Endpoints más utilizados
- **Report Generation**: Reportes generados por día

## 🔍 Troubleshooting

### Problemas Comunes

#### Error de Conexión a Base de Datos

```bash
# Verificar conexión
python manage.py dbshell

# Verificar migraciones
python manage.py showmigrations

# Aplicar migraciones pendientes
python manage.py migrate
```

#### Error de Redis

```bash
# Verificar Redis
redis-cli ping

# Verificar configuración
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

#### Error de Celery

```bash
# Verificar worker
celery -A config worker -l info

# Verificar beat
celery -A config beat -l info

# Verificar tasks
python manage.py shell
>>> from common.infrastructure.tasks import test_task
>>> test_task.delay()
```

### Logs Importantes

- **Django Logs**: `logs/django.log`
- **Celery Logs**: `logs/celery.log`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `/var/log/syslog`

---

_Esta guía técnica complementa el README principal y proporciona información detallada para desarrolladores y administradores del sistema._
