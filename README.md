# 🎓 Backend Alternova - Sistema de Gestión Académica

## 📋 Descripción del Proyecto

Backend Alternova es un sistema de gestión académica desarrollado con Django REST Framework siguiendo los principios de **Clean Architecture** y **SOLID**. El sistema permite la gestión completa de usuarios, materias, reportes y notificaciones en un entorno educativo.

## 🏗️ Arquitectura del Sistema

### Clean Architecture Implementation

El proyecto implementa **Clean Architecture** en todas sus aplicaciones, organizando el código en 5 capas principales:

```
📁 Estructura de Clean Architecture
├── 🎯 Domain Layer (Dominio)
│   ├── entities.py          # Entidades de negocio
│   └── value_objects.py     # Objetos de valor inmutables
├── 🔄 Application Layer (Aplicación)
│   ├── dto/                 # Data Transfer Objects
│   ├── services/            # Servicios de aplicación
│   └── use_cases/           # Casos de uso
├── 🔧 Infrastructure Layer (Infraestructura)
│   ├── models.py           # Modelos Django
│   ├── repositories/        # Implementaciones de repositorios
│   ├── external/           # Servicios externos
│   └── middleware/         # Middleware personalizado
├── 🎨 Presentation Layer (Presentación)
│   ├── views/              # Vistas API
│   ├── serializers/        # Serializadores DRF
│   ├── urls/               # Configuración de URLs
│   └── permissions/        # Permisos personalizados
└── 🧪 Tests Layer (Pruebas)
    ├── unit/               # Pruebas unitarias
    ├── integration/        # Pruebas de integración
    └── fixtures/           # Datos de prueba
```

### Principios SOLID Aplicados

- ✅ **Single Responsibility**: Cada clase tiene una responsabilidad única
- ✅ **Open/Closed**: Fácil extensión sin modificación
- ✅ **Liskov Substitution**: Interfaces intercambiables
- ✅ **Interface Segregation**: Interfaces específicas y pequeñas
- ✅ **Dependency Inversion**: Dependencias apuntan hacia abstracciones

## 🚀 Características Principales

### 👥 Gestión de Usuarios

- **Autenticación JWT**: Sistema seguro de autenticación
- **Roles y Permisos**: Estudiante, Profesor, Administrador
- **Perfiles de Usuario**: Información personal y académica
- **Auditoría de Sesiones**: Control de sesiones activas

### 📚 Gestión Académica

- **Materias**: CRUD completo de materias académicas
- **Inscripciones**: Sistema de inscripción de estudiantes
- **Calificaciones**: Gestión de notas y evaluaciones
- **Reportes Académicos**: Generación de reportes en CSV

### 🔔 Sistema de Notificaciones

- **Notificaciones Automáticas**: Al crear usuarios y calificar
- **Estado de Lectura**: Control de notificaciones leídas/no leídas
- **API de Consulta**: Endpoints para gestionar notificaciones

### 📊 Reportes y Analytics

- **Reportes CSV**: Exportación de datos académicos
- **Métricas de Rendimiento**: Análisis de consultas ORM
- **Auditoría Completa**: Registro de todas las operaciones

### 🔧 Funcionalidades Avanzadas

- **Middleware Personalizado**: Logging y bloqueo de IPs
- **Decoradores**: Funcionalidades transversales
- **Tareas Periódicas**: Celery + Beat para tareas programadas
- **Señales Django**: Automatización de procesos

## 🛠️ Tecnologías Utilizadas

### Backend

- **Django 5.2.7**: Framework web principal
- **Django REST Framework**: API REST
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y sesiones
- **Celery**: Tareas asíncronas
- **Celery Beat**: Tareas programadas

### Autenticación y Seguridad

- **JWT**: JSON Web Tokens
- **SimpleJWT**: Implementación JWT para Django
- **CORS**: Configuración de CORS
- **CSRF**: Protección CSRF

### Documentación y Testing

- **Swagger/OpenAPI**: Documentación automática de API
- **Django Debug Toolbar**: Herramientas de debug
- **Pytest**: Framework de testing

## 📦 Instalación y Configuración

### Prerrequisitos

- Python 3.12+
- PostgreSQL 13+
- Redis 6+
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/backend-alternova.git
cd backend-alternova
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de Datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/alternova_db

# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=johanjimenez0210@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Configuraciones Adicionales
ENABLE_IP_BLOCKING=False
ALLOWED_IPS=
BLOCKED_IPS=
```

### 5. Configurar Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 6. Ejecutar Servidor

```bash
# Servidor de desarrollo
python manage.py runserver

# Servidor con Celery (en terminales separadas)
celery -A config worker -l info
celery -A config beat -l info
```

## 📚 Documentación de la API

### Acceso a la Documentación

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **Schema**: http://127.0.0.1:8000/api/schema/

### Endpoints Principales

#### 🔐 Autenticación

```
POST /api/auth/login/          # Iniciar sesión
POST /api/auth/logout/         # Cerrar sesión
POST /api/auth/refresh/        # Renovar token
POST /api/auth/verify/         # Verificar token
```

#### 👥 Usuarios

```
GET    /api/users/             # Listar usuarios
POST   /api/users/             # Crear usuario
GET    /api/users/{id}/        # Obtener usuario
PUT    /api/users/{id}/        # Actualizar usuario
DELETE /api/users/{id}/        # Eliminar usuario
```

#### 📚 Materias

```
GET    /api/subjects/          # Listar materias
POST   /api/subjects/          # Crear materia
GET    /api/subjects/{id}/     # Obtener materia
PUT    /api/subjects/{id}/     # Actualizar materia
DELETE /api/subjects/{id}/     # Eliminar materia
```

#### 📊 Reportes

```
GET    /api/reports/           # Listar reportes
POST   /api/reports/generate/  # Generar reporte
GET    /api/reports/{id}/download/ # Descargar reporte
```

#### 🔔 Notificaciones

```
GET    /api/notifications/     # Listar notificaciones
PUT    /api/notifications/{id}/mark-read/ # Marcar como leída
```

## 🧪 Testing

### Sistema de Testing Completo

- **Framework**: pytest + pytest-django
- **Cobertura**: Mínimo 70% (objetivo alcanzado)
- **Total de Pruebas**: 108 pruebas implementadas
- **Apps Cubiertas**: common, users, notifications, subjects, reports

### Pruebas por Módulo

- ✅ **Common**: 11 pruebas (auditoría, middleware, utilidades)
- ✅ **Users**: 20 pruebas (autenticación, gestión de usuarios)
- ✅ **Notifications**: 20 pruebas (sistema de notificaciones)
- ✅ **Subjects**: 32 pruebas (materias, inscripciones, calificaciones)
- ✅ **Reports**: 25 pruebas (reportes, exportación CSV)

### Comandos de Testing

```bash
# Ejecutar todas las pruebas (108 pruebas)
pytest -v --ds=config.test_settings

# Con cobertura completa
pytest -v --cov=common --cov=users --cov=notifications --cov=subjects --cov=reports --cov-report=html --cov-report=term-missing --cov-fail-under=70 --ds=config.test_settings

# Por módulo específico
pytest common/tests/unit/test_basic.py -v --ds=config.test_settings
pytest users/tests/unit/test_basic.py -v --ds=config.test_settings
pytest notifications/tests/unit/test_basic.py -v --ds=config.test_settings
pytest subjects/tests/unit/test_basic.py -v --ds=config.test_settings
pytest reports/tests/unit/test_basic.py -v --ds=config.test_settings
```

### Estructura de Testing

```
📁 Estructura de Testing por App
├── tests/
│   ├── unit/              # Pruebas unitarias
│   ├── integration/       # Pruebas de integración
│   ├── fixtures/          # Datos de prueba
│   └── conftest.py        # Configuración pytest
├── pytest.ini            # Configuración pytest
├── config/test_settings.py # Configuración Django para testing
└── requirements-testing.txt # Dependencias de testing
```

### Testing Legacy (Django Test)

```bash
# Todas las pruebas Django
python manage.py test

# Pruebas específicas
python manage.py test users.tests
python manage.py test subjects.tests
python manage.py test reports.tests
python manage.py test notifications.tests
python manage.py test common.tests
```

## 🚀 Despliegue en Producción

### Configuración para Producción

1. **Configurar Variables de Entorno**:

```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
SECRET_KEY=tu-secret-key-super-seguro
```

2. **Configurar Servidor Web**:

```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar con Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

3. **Configurar Nginx** (opcional):

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker (Opcional)

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📈 Monitoreo y Logs

### Logs del Sistema

- **Django Logs**: `logs/django.log`
- **Celery Logs**: `logs/celery.log`
- **Middleware Logs**: Registro automático de requests
- **Audit Logs**: Registro de operaciones críticas

### Métricas Disponibles

- **Performance**: Tiempo de respuesta de APIs
- **Database**: Número de consultas por request
- **Users**: Sesiones activas y actividad
- **Errors**: Errores y excepciones

## 🔧 Mantenimiento

### Comandos Útiles

```bash
# Verificar configuración
python manage.py check

# Recopilar archivos estáticos
python manage.py collectstatic

# Limpiar sesiones expiradas
python manage.py clearsessions

# Backup de base de datos
python manage.py dumpdata > backup.json

# Restaurar backup
python manage.py loaddata backup.json
```

### Tareas Periódicas

- **Limpieza de notificaciones**: Cada 7 días
- **Resumen académico**: Envío semanal a profesores
- **Backup automático**: Diario
- **Limpieza de logs**: Semanal

## 🤝 Contribución

### Flujo de Trabajo

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código

- **PEP 8**: Estilo de código Python
- **Clean Architecture**: Mantener separación de capas
- **SOLID Principles**: Aplicar principios de diseño
- **Documentación**: Documentar funciones y clases importantes

## 📞 Soporte y Contacto

### Desarrollador Principal

- **Nombre**: Johan Jiménez
- **Email**: johanjimenez0210@gmail.com
- **GitHub**: [@tu-usuario](https://github.com/tu-usuario)

### Reportar Issues

Para reportar bugs o solicitar nuevas funcionalidades, crear un issue en GitHub con:

- Descripción detallada del problema
- Pasos para reproducir
- Información del entorno
- Logs relevantes

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🎉 Agradecimientos

- **Django Community**: Por el excelente framework
- **Clean Architecture**: Por los principios de diseño
- **SOLID Principles**: Por las mejores prácticas de desarrollo
- **Open Source**: Por todas las librerías utilizadas

---

## 📊 Estadísticas del Proyecto

- **✅ 5 Aplicaciones**: Todas con Clean Architecture
- **✅ 61 Archivos**: Organizados profesionalmente
- **✅ 5 Capas**: Domain, Application, Infrastructure, Presentation, Tests
- **✅ 100% SOLID**: Principios aplicados consistentemente
- **✅ Documentación**: API completamente documentada
- **✅ Testing**: Suite de pruebas completa
- **✅ Producción**: Listo para despliegue

**¡El proyecto está completo y listo para producción!** 🚀

---

_Última actualización: Octubre 2025_
