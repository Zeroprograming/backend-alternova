# 📊 ESQUEMA DE BASE DE DATOS (ERD) - Backend Alternova

## 🗄️ Diagrama de Entidad-Relación

```mermaid
erDiagram
    %% Usuarios
    User {
        int id PK
        string username UK
        string email UK
        string first_name
        string last_name
        string user_type "student/teacher/admin"
        string phone
        string avatar
        text bio
        date birth_date
        int max_credits_per_semester
        int current_semester_credits
        string academic_year
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    %% Materias
    Subject {
        int id PK
        string code UK
        string name
        text description
        int credits
        int teacher_id FK
        int semester
        boolean is_finished
        int max_students
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    %% Prerrequisitos
    Prerequisite {
        int id PK
        int subject_id FK
        int prerequisite_subject_id FK
        boolean is_mandatory
        datetime created_at
        datetime updated_at
    }

    %% Inscripciones
    Enrollment {
        int id PK
        int student_id FK
        int subject_id FK
        datetime enrolled_at
        decimal final_grade
        int semester
        string academic_year
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    %% Notificaciones
    Notification {
        int id PK
        int user_id FK
        string title
        text message
        string notification_type "info/warning/success/error"
        boolean is_read
        datetime read_at
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    %% Reportes
    Report {
        int id PK
        string title
        string report_type "grades/attendance/enrollments/users/custom"
        string status "pending/processing/completed/failed"
        json filters
        string file
        int generated_by_id FK
        datetime completed_at
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    %% Auditoría
    AuditLog {
        int id PK
        int user_id FK
        string action_type "login/logout/create/update/delete/grade_assigned/enrollment/etc"
        text description
        string ip_address
        text user_agent
        int content_type_id FK
        int object_id
        json extra_data
        datetime created_at
    }

    %% Sesiones de Usuario
    UserSession {
        int id PK
        int user_id FK
        string session_key UK
        string ip_address
        text user_agent
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    %% Relaciones
    User ||--o{ Subject : "teaches"
    User ||--o{ Enrollment : "enrolled_in"
    User ||--o{ Notification : "receives"
    User ||--o{ Report : "generates"
    User ||--o{ AuditLog : "performs"
    User ||--o{ UserSession : "has"

    Subject ||--o{ Enrollment : "has_students"
    Subject ||--o{ Prerequisite : "requires"
    Subject ||--o{ Prerequisite : "is_prerequisite_for"

    Enrollment }o--|| User : "student"
    Enrollment }o--|| Subject : "subject"

    Notification }o--|| User : "user"
    Report }o--|| User : "generated_by"
    AuditLog }o--|| User : "user"
    UserSession }o--|| User : "user"

    Prerequisite }o--|| Subject : "subject"
    Prerequisite }o--|| Subject : "prerequisite_subject"
```

## 📋 Descripción de Entidades

### 👤 **User (Usuario)**

- **Propósito**: Gestión de usuarios del sistema (estudiantes, profesores, administradores)
- **Campos Clave**: `user_type`, `academic_year`, `max_credits_per_semester`
- **Relaciones**: Central - conecta con todas las demás entidades

### 📚 **Subject (Materia)**

- **Propósito**: Gestión de materias/asignaturas académicas
- **Campos Clave**: `code` (único), `credits`, `teacher_id`, `max_students`
- **Relaciones**: Conecta con User (profesor), Enrollment (estudiantes), Prerequisite

### 🔗 **Prerequisite (Prerrequisito)**

- **Propósito**: Define prerrequisitos entre materias
- **Campos Clave**: `subject_id`, `prerequisite_subject_id`, `is_mandatory`
- **Relaciones**: Auto-referencial con Subject

### 📝 **Enrollment (Inscripción)**

- **Propósito**: Registra inscripciones de estudiantes en materias
- **Campos Clave**: `student_id`, `subject_id`, `final_grade`, `academic_year`
- **Restricciones**: Único por estudiante-materia-año académico

### 🔔 **Notification (Notificación)**

- **Propósito**: Sistema de notificaciones para usuarios
- **Campos Clave**: `user_id`, `notification_type`, `is_read`
- **Relaciones**: Conecta con User

### 📊 **Report (Reporte)**

- **Propósito**: Generación de reportes del sistema
- **Campos Clave**: `report_type`, `status`, `filters`, `generated_by_id`
- **Relaciones**: Conecta con User (generador)

### 🔍 **AuditLog (Log de Auditoría)**

- **Propósito**: Registro de todas las acciones importantes del sistema
- **Campos Clave**: `action_type`, `ip_address`, `user_agent`, `extra_data`
- **Relaciones**: Conecta con User, ContentType (genérico)

### 🔐 **UserSession (Sesión de Usuario)**

- **Propósito**: Gestión de sesiones activas de usuarios
- **Campos Clave**: `user_id`, `session_key`, `is_active`
- **Relaciones**: Conecta con User

## 🎯 Características del Diseño

### ✅ **Ventajas del Diseño**

1. **Normalización**: Evita redundancia de datos
2. **Integridad**: Claves foráneas garantizan consistencia
3. **Auditoría**: Registro completo de acciones
4. **Flexibilidad**: Campos JSON para datos dinámicos
5. **Escalabilidad**: Índices optimizados para consultas

### 🔧 **Patrones Implementados**

1. **Soft Delete**: Eliminación lógica con `is_active` y `deleted_at`
2. **Auditoría**: Registro de creación/modificación con `created_by`/`updated_by`
3. **Timestamps**: `created_at` y `updated_at` automáticos
4. **Generic Foreign Keys**: Para auditoría de cualquier modelo
5. **Unique Constraints**: Para evitar duplicados críticos

### 📈 **Optimizaciones**

1. **Índices**: En campos de consulta frecuente
2. **Campos Calculados**: Propiedades para lógica de negocio
3. **Validaciones**: A nivel de modelo y base de datos
4. **Managers Personalizados**: Para consultas optimizadas
