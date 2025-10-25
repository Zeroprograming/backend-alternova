# 🔄 DIAGRAMA DE FLUJO DEL PROYECTO - Backend Alternova

## 🏗️ Arquitectura General del Sistema

```mermaid
graph TB
    %% Cliente
    Client[👤 Cliente Web/Móvil]

    %% Nginx
    Nginx[🌐 Nginx<br/>Reverse Proxy<br/>Rate Limiting<br/>Static Files]

    %% Django App
    Django[🐍 Django App<br/>Gunicorn<br/>Port 8000]

    %% Servicios de Backend
    Auth[🔐 Authentication<br/>JWT Tokens<br/>Session Management]
    Users[👥 User Management<br/>Students/Teachers/Admins]
    Subjects[📚 Subject Management<br/>Courses & Prerequisites]
    Reports[📊 Report Generation<br/>CSV Export<br/>Analytics]
    Notifications[🔔 Notification System<br/>Real-time Alerts]

    %% Base de Datos
    PostgreSQL[(🗄️ PostgreSQL<br/>Primary Database<br/>Port 5432)]

    %% Cache y Cola
    Redis[(⚡ Redis<br/>Cache & Message Broker<br/>Port 6379)]

    %% Celery Workers
    CeleryWorker[⚙️ Celery Worker<br/>Background Tasks<br/>Report Generation]
    CeleryBeat[⏰ Celery Beat<br/>Scheduled Tasks<br/>Cleanup Jobs]

    %% Conexiones
    Client --> Nginx
    Nginx --> Django
    Django --> Auth
    Django --> Users
    Django --> Subjects
    Django --> Reports
    Django --> Notifications

    Django --> PostgreSQL
    Django --> Redis

    CeleryWorker --> PostgreSQL
    CeleryWorker --> Redis
    CeleryBeat --> Redis

    %% Estilos
    classDef client fill:#e1f5fe
    classDef nginx fill:#fff3e0
    classDef django fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef database fill:#fce4ec
    classDef worker fill:#fff8e1

    class Client client
    class Nginx nginx
    class Django django
    class Auth,Users,Subjects,Reports,Notifications service
    class PostgreSQL,Redis database
    class CeleryWorker,CeleryBeat worker
```

## 🔄 Flujo de Datos Principal

```mermaid
sequenceDiagram
    participant C as Cliente
    participant N as Nginx
    participant D as Django App
    participant DB as PostgreSQL
    participant R as Redis
    participant CW as Celery Worker

    %% Autenticación
    C->>N: POST /api/auth/login/
    N->>D: Forward Request
    D->>DB: Validate User
    DB-->>D: User Data
    D->>R: Store Session
    D-->>N: JWT Token
    N-->>C: Authentication Response

    %% Operación CRUD
    C->>N: GET /api/subjects/
    N->>D: Forward Request
    D->>R: Check Cache
    alt Cache Hit
        R-->>D: Cached Data
    else Cache Miss
        D->>DB: Query Subjects
        DB-->>D: Subject Data
        D->>R: Store in Cache
    end
    D-->>N: JSON Response
    N-->>C: Subject List

    %% Generación de Reporte
    C->>N: POST /api/reports/
    N->>D: Forward Request
    D->>CW: Queue Report Task
    CW->>DB: Generate Report Data
    DB-->>CW: Report Data
    CW->>DB: Save Report File
    CW->>R: Update Task Status
    D-->>N: Task ID
    N-->>C: Report Started

    %% Notificación
    CW->>D: Report Complete
    D->>R: Send Notification
    D->>DB: Update Report Status
```

## 🏛️ Arquitectura Clean Architecture

```mermaid
graph TB
    %% Capas de Clean Architecture
    subgraph "🎯 Domain Layer"
        Entities[📦 Entities<br/>User, Subject, Enrollment<br/>Notification, Report]
        ValueObjects[💎 Value Objects<br/>Email, Phone, Grade<br/>NotificationType]
        Repositories[📋 Repository Interfaces<br/>IUserRepository<br/>ISubjectRepository]
        Services[⚙️ Domain Services<br/>UserDomainService<br/>AcademicDomainService]
    end

    subgraph "🔧 Application Layer"
        UseCases[🎯 Use Cases<br/>CreateUserUseCase<br/>EnrollStudentUseCase<br/>GenerateReportUseCase]
        DTOs[📄 DTOs<br/>UserDTO, SubjectDTO<br/>EnrollmentDTO, ReportDTO]
        AppServices[🛠️ Application Services<br/>UserApplicationService<br/>SubjectApplicationService]
    end

    subgraph "🏗️ Infrastructure Layer"
        DjangoModels[🗄️ Django Models<br/>User, Subject, Enrollment<br/>Notification, Report]
        RepoImpl[📚 Repository Implementations<br/>DjangoUserRepository<br/>DjangoSubjectRepository]
        ExternalServices[🌐 External Services<br/>EmailService, JWTService<br/>FileStorageService]
        Tasks[⚡ Celery Tasks<br/>SendEmailTask<br/>GenerateReportTask]
    end

    subgraph "🎨 Presentation Layer"
        Views[👁️ Views<br/>UserViewSet, SubjectViewSet<br/>ReportViewSet, NotificationViewSet]
        Serializers[🔄 Serializers<br/>UserSerializer, SubjectSerializer<br/>EnrollmentSerializer]
        URLs[🔗 URL Patterns<br/>API Endpoints<br/>Authentication Routes]
        Permissions[🔐 Permissions<br/>IsOwnerOrAdmin<br/>CanManageSubjects]
    end

    %% Flujo de dependencias
    Views --> UseCases
    Serializers --> DTOs
    URLs --> Views
    Permissions --> Views

    UseCases --> Entities
    UseCases --> Repositories
    DTOs --> Entities
    AppServices --> UseCases

    Repositories --> DjangoModels
    RepoImpl --> DjangoModels
    ExternalServices --> Tasks
    Tasks --> DjangoModels

    %% Estilos
    classDef domain fill:#e8f5e8
    classDef application fill:#e1f5fe
    classDef infrastructure fill:#fff3e0
    classDef presentation fill:#f3e5f5

    class Entities,ValueObjects,Repositories,Services domain
    class UseCases,DTOs,AppServices application
    class DjangoModels,RepoImpl,ExternalServices,Tasks infrastructure
    class Views,Serializers,URLs,Permissions presentation
```

## 🔄 Flujo de Procesamiento de Tareas

```mermaid
graph LR
    %% Inicio
    Start([🚀 Inicio])

    %% Proceso Principal
    Request[📥 Request HTTP]
    Auth[🔐 Authentication]
    Validation[✅ Validation]
    BusinessLogic[🧠 Business Logic]
    Database[🗄️ Database Operation]
    Response[📤 HTTP Response]

    %% Tareas Asíncronas
    TaskQueue[⚡ Task Queue]
    BackgroundTask[🔄 Background Task]
    Notification[🔔 Send Notification]

    %% Flujo Principal
    Start --> Request
    Request --> Auth
    Auth --> Validation
    Validation --> BusinessLogic
    BusinessLogic --> Database
    Database --> Response

    %% Flujo Asíncrono
    BusinessLogic --> TaskQueue
    TaskQueue --> BackgroundTask
    BackgroundTask --> Notification

    %% Decisiones
    Auth -->|Valid| Validation
    Auth -->|Invalid| Response
    Validation -->|Valid| BusinessLogic
    Validation -->|Invalid| Response

    %% Estilos
    classDef start fill:#4caf50
    classDef process fill:#2196f3
    classDef decision fill:#ff9800
    classDef async fill:#9c27b0

    class Start start
    class Request,Auth,Validation,BusinessLogic,Database,Response process
    class TaskQueue,BackgroundTask,Notification async
```

## 📊 Flujo de Datos por Módulo

### 👥 **Módulo de Usuarios**

```mermaid
graph LR
    UserRequest[👤 User Request] --> AuthCheck[🔐 Auth Check]
    AuthCheck -->|Valid| UserService[👥 User Service]
    AuthCheck -->|Invalid| ErrorResponse[❌ Error Response]

    UserService --> UserRepo[🗄️ User Repository]
    UserRepo --> UserModel[📦 User Model]
    UserModel --> AuditLog[📝 Audit Log]

    UserService --> UserResponse[✅ User Response]
```

### 📚 **Módulo de Materias**

```mermaid
graph LR
    SubjectRequest[📚 Subject Request] --> PermissionCheck[🔐 Permission Check]
    PermissionCheck -->|Allowed| SubjectService[📚 Subject Service]
    PermissionCheck -->|Denied| ErrorResponse[❌ Error Response]

    SubjectService --> SubjectRepo[🗄️ Subject Repository]
    SubjectRepo --> SubjectModel[📦 Subject Model]
    SubjectModel --> PrerequisiteCheck[🔗 Prerequisite Check]

    SubjectService --> SubjectResponse[✅ Subject Response]
```

### 📊 **Módulo de Reportes**

```mermaid
graph LR
    ReportRequest[📊 Report Request] --> ReportService[📊 Report Service]
    ReportService --> TaskQueue[⚡ Task Queue]
    TaskQueue --> CeleryWorker[⚙️ Celery Worker]

    CeleryWorker --> DataQuery[🔍 Data Query]
    DataQuery --> ReportGeneration[📄 Report Generation]
    ReportGeneration --> FileStorage[💾 File Storage]
    FileStorage --> Notification[🔔 Notification]

    ReportService --> TaskID[🆔 Task ID Response]
```

## 🎯 Características del Flujo

### ✅ **Ventajas del Diseño**

1. **Separación de Responsabilidades**: Cada capa tiene un propósito específico
2. **Escalabilidad**: Celery permite procesamiento asíncrono
3. **Caching**: Redis mejora el rendimiento
4. **Auditoría**: Registro completo de todas las operaciones
5. **Seguridad**: Autenticación JWT y permisos granulares

### 🔧 **Patrones Implementados**

1. **Clean Architecture**: Separación clara de capas
2. **Repository Pattern**: Abstracción del acceso a datos
3. **CQRS**: Separación de comandos y consultas
4. **Event Sourcing**: Auditoría de cambios
5. **Microservices**: Servicios independientes

### 📈 **Optimizaciones**

1. **Connection Pooling**: Reutilización de conexiones DB
2. **Query Optimization**: Consultas eficientes
3. **Background Processing**: Tareas pesadas en segundo plano
4. **Caching Strategy**: Cache inteligente con Redis
5. **Rate Limiting**: Protección contra abuso
