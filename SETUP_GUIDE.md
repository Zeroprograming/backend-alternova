# Configuración de Ejemplo - Backend Alternova

## 📋 Archivo .env de Ejemplo

```env
# ===========================================
# CONFIGURACIÓN DJANGO
# ===========================================
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# ===========================================
# BASE DE DATOS POSTGRESQL
# ===========================================
DATABASE_URL=postgresql://alternova_user:alternova_password@localhost:5432/alternova_db
DB_ENGINE=django.db.backends.postgresql
DB_NAME=alternova_db
DB_USER=alternova_user
DB_PASSWORD=alternova_password
DB_HOST=localhost
DB_PORT=5432

# ===========================================
# REDIS CACHE
# ===========================================
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ===========================================
# CONFIGURACIÓN DE EMAIL (GMAIL)
# ===========================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=johanjimenez0210@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=johanjimenez0210@gmail.com
EMAIL_USE_SSL=False

# ===========================================
# CELERY CONFIGURACIÓN
# ===========================================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_ACCEPT_CONTENT=['json']
CELERY_TASK_SERIALIZER='json'
CELERY_RESULT_SERIALIZER='json'
CELERY_TIMEZONE='America/Bogota'
CELERY_ENABLE_UTC=True

# ===========================================
# CONFIGURACIÓN DE SEGURIDAD
# ===========================================
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=True
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080

# ===========================================
# MIDDLEWARE CONFIGURACIÓN
# ===========================================
ENABLE_IP_BLOCKING=False
ALLOWED_IPS=127.0.0.1,localhost,::1
BLOCKED_IPS=
ENABLE_REQUEST_LOGGING=True
ENABLE_PERFORMANCE_MONITORING=True

# ===========================================
# ARCHIVOS Y MEDIA
# ===========================================
MEDIA_URL=/media/
MEDIA_ROOT=media/
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# ===========================================
# CONFIGURACIÓN DE LOGGING
# ===========================================
LOG_LEVEL=INFO
LOG_FILE=logs/django.log
CELERY_LOG_FILE=logs/celery.log
ENABLE_FILE_LOGGING=True

# ===========================================
# CONFIGURACIÓN DE JWT
# ===========================================
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1440
JWT_ALGORITHM=HS256

# ===========================================
# CONFIGURACIÓN DE REPORTES
# ===========================================
REPORTS_DIRECTORY=reports/
MAX_REPORT_SIZE=10485760
REPORT_CLEANUP_DAYS=30

# ===========================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ===========================================
NOTIFICATION_CLEANUP_DAYS=90
EMAIL_RETRY_ATTEMPTS=3
EMAIL_RETRY_DELAY=60

# ===========================================
# CONFIGURACIÓN DE DESARROLLO
# ===========================================
ENABLE_DEBUG_TOOLBAR=True
ENABLE_SWAGGER_DOCS=True
ENABLE_API_DOCS=True
```

## 🐳 Docker Compose de Ejemplo

```yaml
# docker-compose.yml
version: "3.8"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: alternova_db
      POSTGRES_USER: alternova_user
      POSTGRES_PASSWORD: alternova_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://alternova_user:alternova_password@db:5432/alternova_db
      - REDIS_URL=redis://redis:6379/0

  celery:
    build: .
    command: celery -A config worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://alternova_user:alternova_password@db:5432/alternova_db
      - REDIS_URL=redis://redis:6379/0

  celery-beat:
    build: .
    command: celery -A config beat -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://alternova_user:alternova_password@db:5432/alternova_db
      - REDIS_URL=redis://redis:6379/0

volumes:
  postgres_data:
  redis_data:
```

## 🐳 Dockerfile de Ejemplo

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs media staticfiles reports

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📋 Scripts de Setup

### setup.sh (Linux/Mac)

```bash
#!/bin/bash

# Script de configuración automática para Linux/Mac

echo "🚀 Configurando Backend Alternova..."

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p logs media staticfiles reports

# Configurar base de datos
echo "🗄️ Configurando base de datos..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
echo "👤 Creando superusuario..."
python manage.py createsuperuser

# Recopilar archivos estáticos
echo "📄 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Configuración completada!"
echo "🚀 Para iniciar el servidor: python manage.py runserver"
```

### setup.bat (Windows)

```batch
@echo off

REM Script de configuración automática para Windows

echo 🚀 Configurando Backend Alternova...

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📥 Instalando dependencias...
pip install -r requirements.txt

REM Crear directorios necesarios
echo 📁 Creando directorios...
mkdir logs
mkdir media
mkdir staticfiles
mkdir reports

REM Configurar base de datos
echo 🗄️ Configurando base de datos...
python manage.py makemigrations
python manage.py migrate

REM Crear superusuario
echo 👤 Creando superusuario...
python manage.py createsuperuser

REM Recopilar archivos estáticos
echo 📄 Recopilando archivos estáticos...
python manage.py collectstatic --noinput

echo ✅ Configuración completada!
echo 🚀 Para iniciar el servidor: python manage.py runserver
pause
```

## 🔧 Comandos Útiles

### Desarrollo

```bash
# Activar entorno virtual
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar con Celery
celery -A config worker -l info
celery -A config beat -l info
```

### Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations

# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell
```

### Testing

#### **Sistema de Testing Completo**

- **Framework**: pytest + pytest-django
- **Total de Pruebas**: 108 pruebas implementadas
- **Cobertura**: 100% en todos los módulos
- **Apps Cubiertas**: common, users, notifications, subjects, reports

#### **Comandos de Testing**

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

#### **Testing Legacy (Django Test)**

```bash
# Ejecutar todas las pruebas Django
python manage.py test

# Pruebas con cobertura
coverage run --source='.' manage.py test
coverage report
coverage html
```

python manage.py test users.tests
python manage.py test subjects.tests

````

### Producción

```bash
# Verificar configuración
python manage.py check --deploy

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar con Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Ejecutar con Docker
docker-compose up -d
````

## 📊 Monitoreo y Logs

### Estructura de Logs

```
logs/
├── django.log              # Logs de Django
├── celery.log              # Logs de Celery
├── error.log               # Logs de errores
├── access.log              # Logs de acceso
└── audit.log               # Logs de auditoría
```

### Comandos de Monitoreo

```bash
# Ver logs en tiempo real
tail -f logs/django.log

# Ver logs de Celery
tail -f logs/celery.log

# Ver logs de errores
tail -f logs/error.log

# Verificar estado de servicios
ps aux | grep python
ps aux | grep celery
```

## 🚨 Troubleshooting

### Problemas Comunes

#### Error de Conexión a Base de Datos

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo systemctl start postgresql

# Verificar conexión
psql -h localhost -U alternova_user -d alternova_db
```

#### Error de Redis

```bash
# Verificar Redis
sudo systemctl status redis
sudo systemctl start redis

# Verificar conexión
redis-cli ping
```

#### Error de Permisos

```bash
# Cambiar permisos de directorios
chmod 755 logs/
chmod 755 media/
chmod 755 staticfiles/
chmod 755 reports/
```

#### Error de Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

_Estos archivos de configuración facilitan el setup y deployment del proyecto Backend Alternova._
