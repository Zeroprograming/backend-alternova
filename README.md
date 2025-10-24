# Backend Alternova - Django REST Framework API

API Backend desarrollada con Django REST Framework, PostgreSQL y **Arquitectura Modular**.

## 🚀 Características

- ✅ **Arquitectura Modular** con separación de responsabilidades
- ✅ Django 5.2.7 + Django REST Framework 3.16.1
- ✅ PostgreSQL con Docker
- ✅ Documentación Swagger/OpenAPI automática
- ✅ Variables de entorno con python-decouple
- ✅ Modelo de usuario personalizado
- ✅ Sistema de permisos granulares
- ✅ Middleware personalizado (logging, auditoría)
- ✅ Lógica de negocio en services (NO en views/serializers)
- ✅ Paginación y throttling configurados

## 📦 Aplicaciones Modulares

1. **common**: Utilidades compartidas, modelos base, permisos, decoradores
2. **users**: Gestión de usuarios y perfiles
3. **subjects**: Gestión de materias e inscripciones
4. **notifications**: Sistema de notificaciones
5. **reports**: Generación de reportes

## 📋 Requisitos

- Python 3.12+
- Docker y Docker Compose
- pip

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd backend-alternova
```

### 2. Crear entorno virtual y activarlo

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Django Settings
SECRET_KEY=django-insecure-tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5. Levantar PostgreSQL con Docker

```bash
docker-compose up -d
```

### 6. Aplicar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 8. Iniciar el servidor

```bash
python manage.py runserver
```

## 📚 Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a:

### Swagger UI (Recomendado)

```
http://localhost:8000/api/docs/
```

Interfaz interactiva donde puedes probar todos los endpoints.

### ReDoc

```
http://localhost:8000/api/redoc/
```

Documentación elegante y limpia.

### Schema OpenAPI

```
http://localhost:8000/api/schema/
```

Esquema raw en formato OpenAPI 3.0.

## 🎯 Endpoints Disponibles

### Autenticación (`/api/auth/`)

- `POST /api/auth/login/` - Login con JWT (registra auditoría)
- `POST /api/auth/refresh/` - Refrescar access token
- `POST /api/auth/verify/` - Verificar validez del token
- `POST /api/auth/logout/` - Logout (blacklist token + auditoría)
- `GET /api/auth/sessions/` - Ver sesiones activas del usuario
- `POST /api/auth/sessions/{id}/revoke/` - Revocar sesión específica

### Health Check

- `GET /` - Health check de la API (estado, versión, conexión DB)

### API de Ejemplo (Demo)

- `GET /api/examples/` - Lista de items de ejemplo
- `POST /api/examples/` - Crear un nuevo item
- `GET /api/examples/{id}/` - Obtener un item específico
- `GET /api/stats/` - Obtener estadísticas

### Admin

- `GET /admin/` - Panel de administración de Django

## 🧪 Probar la API

### Con Swagger UI:

1. Ve a http://localhost:8000/api/docs/
2. Haz clic en cualquier endpoint
3. Clic en "Try it out"
4. Completa los parámetros (si es necesario)
5. Clic en "Execute"
6. Ve la respuesta

### Con curl:

**Health Check:**

```bash
curl http://localhost:8000/
```

**Registrar usuario:**

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "estudiante1",
    "email": "estudiante@example.com",
    "password": "Password123!",
    "password_confirm": "Password123!",
    "first_name": "Juan",
    "last_name": "Pérez",
    "user_type": "student"
  }'
```

**Login (Obtener JWT):**

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "estudiante1",
    "password": "Password123!"
  }'
```

**Ver mi perfil (Con JWT):**

```bash
curl http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

**Listar materias (Con JWT):**

```bash
curl http://localhost:8000/api/subjects/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

**Logout:**

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "TU_REFRESH_TOKEN"
  }'
```

## 🗄️ Base de Datos

### Comandos útiles de Docker:

```bash
# Ver logs de PostgreSQL
docker-compose logs -f db

# Detener PostgreSQL
docker-compose down

# Detener y eliminar datos
docker-compose down -v

# Reiniciar PostgreSQL
docker-compose restart
```

### Conectarse a PostgreSQL:

```bash
docker exec -it alternova_postgres psql -U postgres -d postgres
```

## 📦 Estructura del Proyecto

```
backend-alternova/
├── config/                 # Configuración del proyecto
│   ├── settings.py        # Settings de Django
│   ├── urls.py           # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── example_api/           # App de ejemplo
│   ├── views.py          # Vistas de la API
│   ├── serializers.py    # Serializers
│   └── urls.py           # URLs de la app
├── venv/                  # Entorno virtual
├── .env                   # Variables de entorno (no subir a git)
├── .gitignore
├── docker-compose.yml     # Configuración de Docker
├── manage.py
├── requirements.txt       # Dependencias
├── README.md             # Este archivo
└── SWAGGER_GUIDE.md      # Guía detallada de Swagger
```

## 🔧 Desarrollo

### Crear una nueva app:

```bash
python manage.py startapp nombre_app
```

### Agregar la app a INSTALLED_APPS en `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'nombre_app',
]
```

### Crear migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 📝 Configuración de DRF

La configuración de Django REST Framework incluye:

- **Autenticación**: Session + Basic Auth
- **Permisos**: IsAuthenticatedOrReadOnly (lectura pública, escritura autenticada)
- **Paginación**: 10 items por página
- **Throttling**: 100/día anónimos, 1000/día autenticados
- **Renderizado**: JSON + Browsable API
- **Parsers**: JSON, Form, MultiPart

Ver `config/settings.py` para más detalles.

## 📖 Documentación Adicional

- [SWAGGER_GUIDE.md](SWAGGER_GUIDE.md) - Guía completa de uso de Swagger
- [Documentación de Django REST Framework](https://www.django-rest-framework.org/)
- [Documentación de drf-spectacular](https://drf-spectacular.readthedocs.io/)

## 🚀 Despliegue

Para producción, recuerda:

1. Cambiar `DEBUG=False` en `.env`
2. Configurar `ALLOWED_HOSTS` apropiadamente
3. Generar un `SECRET_KEY` seguro
4. Cambiar credenciales de PostgreSQL
5. Configurar servidor WSGI (Gunicorn, uWSGI)
6. Configurar servidor web (Nginx, Apache)
7. Recolectar archivos estáticos: `python manage.py collectstatic`

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Contacto

Alternova - [@alternova](https://github.com/alternova)

---

⭐️ Si te gusta este proyecto, dale una estrella en GitHub!
