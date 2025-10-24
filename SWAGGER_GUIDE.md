# 📚 Guía de Swagger - Documentación de API

## ✅ Swagger Instalado y Configurado

### 🎯 URLs de Documentación Disponibles:

1. **Swagger UI** (Interfaz interactiva recomendada)

   ```
   http://localhost:8000/api/docs/
   ```

   - Interfaz visual moderna
   - Prueba endpoints directamente desde el navegador
   - Documenta automáticamente todos tus endpoints

2. **ReDoc** (Documentación limpia y elegante)

   ```
   http://localhost:8000/api/redoc/
   ```

   - Presentación más limpia
   - Ideal para compartir con clientes
   - Solo lectura (no permite probar endpoints)

3. **Schema OpenAPI** (JSON/YAML)
   ```
   http://localhost:8000/api/schema/
   ```
   - Esquema raw en formato OpenAPI 3.0
   - Útil para generación de código
   - Importable a otras herramientas

---

## 🚀 Cómo Usar Swagger

### 1. **Inicia tu servidor**

```bash
python manage.py runserver
```

### 2. **Abre Swagger UI**

Ve a: http://localhost:8000/api/docs/

### 3. **Interfaz de Swagger UI**

Verás:

- **Lista de endpoints**: Todos tus endpoints organizados por tags
- **Métodos HTTP**: GET, POST, PUT, PATCH, DELETE
- **Parámetros**: Query params, path params, body
- **Respuestas**: Códigos de estado y ejemplos
- **Modelos**: Schemas de tus serializers

### 4. **Probar un Endpoint**

1. Click en el endpoint que quieres probar
2. Click en "Try it out"
3. Completa los parámetros necesarios
4. Click en "Execute"
5. Ve la respuesta con el código de estado

---

## 🎨 Configuración Actual

### En `settings.py`:

```python
SPECTACULAR_SETTINGS = {
    "TITLE": "Alternova API",
    "DESCRIPTION": "API Documentation for Alternova Backend",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api",
}
```

### URLs configuradas:

```python
urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

---

## 📝 Documentar tus Endpoints

### Ejemplo 1: ViewSet Básico

```python
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos.

    Este endpoint permite crear, leer, actualizar y eliminar productos.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @extend_schema(
        summary="Listar todos los productos",
        description="Retorna una lista paginada de todos los productos disponibles",
        tags=["Productos"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Crear un nuevo producto",
        description="Crea un nuevo producto en el sistema",
        tags=["Productos"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
```

### Ejemplo 2: APIView con Decorador

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

class StatsView(APIView):
    @extend_schema(
        summary="Obtener estadísticas",
        description="Retorna estadísticas generales del sistema",
        tags=["Estadísticas"],
        responses={200: {
            "type": "object",
            "properties": {
                "total_products": {"type": "integer"},
                "total_users": {"type": "integer"},
                "total_sales": {"type": "number"}
            }
        }}
    )
    def get(self, request):
        return Response({
            "total_products": 100,
            "total_users": 50,
            "total_sales": 15000.50
        })
```

### Ejemplo 3: Con Parámetros Personalizados

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class ProductViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="Buscar productos",
        description="Busca productos por nombre o categoría",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Término de búsqueda',
                required=False
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='ID de la categoría',
                required=False
            ),
        ],
        tags=["Productos"],
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        # Tu lógica aquí
        pass
```

---

## 🔒 Documentar Autenticación

### Si usas autenticación por Token:

```python
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="Endpoint protegido",
    description="Requiere autenticación",
    tags=["Seguridad"],
    auth=['tokenAuth'],  # Indica que requiere token
)
@api_view(['GET'])
def protected_view(request):
    return Response({"message": "Autenticado!"})
```

---

## 🎯 Tags y Organización

Organiza tus endpoints con tags:

```python
@extend_schema(tags=["Usuarios"])
class UserViewSet(viewsets.ModelViewSet):
    pass

@extend_schema(tags=["Productos", "Inventario"])
class ProductViewSet(viewsets.ModelViewSet):
    pass
```

Esto agrupa los endpoints en Swagger UI.

---

## 🔧 Personalización Avanzada

### Cambiar Título y Descripción:

En `settings.py`:

```python
SPECTACULAR_SETTINGS = {
    "TITLE": "Mi Super API",
    "DESCRIPTION": "La mejor API del mundo",
    "VERSION": "2.0.0",
    "CONTACT": {
        "name": "Soporte Técnico",
        "email": "soporte@alternova.com",
    },
    "LICENSE": {
        "name": "MIT",
    },
}
```

### Agregar Servidores:

```python
SPECTACULAR_SETTINGS = {
    # ... otras configuraciones
    "SERVERS": [
        {"url": "http://localhost:8000", "description": "Desarrollo"},
        {"url": "https://api.alternova.com", "description": "Producción"},
    ],
}
```

---

## 📱 Exportar Documentación

### Generar archivo de schema:

```bash
python manage.py spectacular --file schema.yml
```

Esto genera un archivo `schema.yml` que puedes:

- Importar en Postman
- Usar con herramientas de generación de código
- Compartir con tu equipo frontend

---

## 🐛 Solución de Problemas

### Swagger no muestra mis endpoints:

1. Verifica que tus views usen ViewSets o APIViews de DRF
2. Asegúrate de incluir las URLs en `urlpatterns`
3. Reinicia el servidor

### Error "No schema available":

1. Verifica que `DEFAULT_SCHEMA_CLASS` esté configurado:
   ```python
   REST_FRAMEWORK = {
       "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
   }
   ```

### Endpoints no documentados correctamente:

Usa el decorador `@extend_schema`:

```python
from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="Mi endpoint",
    description="Descripción detallada",
)
def my_view(request):
    pass
```

---

## 🎉 ¡Tu Swagger está listo!

Visita: **http://localhost:8000/api/docs/**

Cuando crees tus primeras APIs, aparecerán automáticamente en la documentación. 🚀

---

## 📚 Recursos Adicionales

- [Documentación oficial de drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Django REST Framework](https://www.django-rest-framework.org/)
