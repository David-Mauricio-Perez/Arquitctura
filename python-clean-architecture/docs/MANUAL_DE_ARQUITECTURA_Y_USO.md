# 📘 Manual Integral del Proyecto — Python Clean Architecture & DDD

> **Objetivo de este documento:**  
> Servir como guía definitiva para que cualquier desarrollador, arquitecto o evaluador —incluso sin conocimiento previo del proyecto— comprenda **qué hace el sistema, cómo está estructurado, cómo fluyen los datos a través de sus capas, qué componentes intervienen y qué se necesita exactamente para compilarlo, configurarlo y ejecutarlo**.

---

## 📑 Tabla de Contenidos
1. [¿Qué es este proyecto? (Visión General)](#1-qué-es-este-proyecto-visión-general)
2. [Requisitos Previos y Entorno de Ejecución ("Qué necesita para compilar")](#2-requisitos-previos-y-entorno-de-ejecución-qué-necesita-para-compilar)
3. [Arquitectura del Sistema: Clean Architecture + DDD](#3-arquitectura-del-sistema-clean-architecture--ddd)
4. [Estructura del Código y Componentes Clave](#4-estructura-del-código-y-componentes-clave)
5. [Flujo Detallado de una Petición HTTP](#5-flujo-detallado-de-una-petición-http)
6. [La Relación 1:1 entre Usuario (User) y Rol (Rol)](#6-la-relación-11-entre-usuario-user-y-rol-rol)
7. [Paso a Paso: Cómo Compilar, Verificar y Ejecutar](#7-paso-a-paso-cómo-compilar-verificar-y-ejecutar)
8. [Pruebas Automatizadas y Aseguramiento de Calidad](#8-pruebas-automatizadas-y-aseguramiento-de-calidad)
9. [Resolución de Problemas Comunes (Troubleshooting)](#9-resolución-de-problemas-comunes-troubleshooting)

---

## 1. ¿Qué es este proyecto? (Visión General)

Este proyecto es una **API Web REST de grado productivo** construida con **Python 3.12+** y **FastAPI**. 

A diferencia de proyectos tradicionales donde las rutas, la lógica y las consultas a la base de datos se mezclan en los mismos archivos, este sistema implementa estrictamente **Clean Architecture (Arquitectura Limpia)** y principios de **DDD (Domain-Driven Design / Diseño Guiado por el Dominio)**.

### Módulos de Negocio Implementados
1. **Gestión de Usuarios (`User`)**: Registro, consulta, actualización y eliminación de usuarios con validaciones de negocio en objetos de valor (Email, Password, ID).
2. **Autenticación Segura (`Auth`)**: Generación y verificación de tokens **JWT** bajo el estándar **OAuth2** (flujo `password bearer`).
3. **Gestión de Roles (`Rol`)**: Creación y administración de roles del sistema, manteniendo una **relación estricta 1:1 (unívoca)** con la entidad `User`.

---

## 2. Requisitos Previos y Entorno de Ejecución ("Qué necesita para compilar")

Aunque Python es un lenguaje interpretado (no genera un binario ejecutable `.exe`), en desarrollo moderno el proceso de "compilación" equivale a:
1. La **instalación del árbol de dependencias** en un entorno virtual aislado.
2. La **comprobación estática de tipos (type-checking)** y análisis de sintaxis (linter).
3. La **inicialización de la base de datos relacional** y ejecución de migraciones.

### 2.1. Requisitos de Software
* **Python**: Versión `3.12` o superior (compatible y probado con Python `3.14`).
* **Gestor de Paquetes**: [Poetry](https://python-poetry.org/) o `pip` con `venv`.
* **Base de Datos**: [PostgreSQL](https://www.postgresql.org/) (versión 14 a 18).
* **Opcional (Muy recomendado)**: [Docker Desktop](https://www.docker.com/) con Docker Compose para levantar la base de datos sin instalación manual.

### 2.2. Variables de Entorno (`.env`)
El proyecto lee sus variables de configuración desde un archivo `.env` ubicado en la raíz del proyecto. Debe contener:

```ini
# Cadena de conexión asíncrona a PostgreSQL (driver asyncpg obligatorio)
DB_URL="postgresql+asyncpg://postgres:passwd@localhost:5432/app_dev"

# Clave criptográfica para firmar los tokens JWT
JWT_SECRET_KEY="development_secret_key_change_in_production"

# Algoritmo de firma y expiración
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración del servidor web
ENV="dev"
SERVER_HOST="0.0.0.0"
SERVER_PORT=8080
SERVER_RELOAD=true
LOG_LEVEL="INFO"
```

### 2.3. Extensiones recomendadas para el Editor (VSCode / PyCharm)
Para trabajar cómodamente en este proyecto se recomienda instalar:
* **Python & Pylance**: Autocompletado y análisis semántico.
* **Ruff**: Formateo instantáneo de código y corrección de advertencias.
* **Mypy Type Checker**: Detección de errores de tipos antes de ejecutar.
* **Draw.io Integration (Hediet)**: Para visualizar y editar interactivamente el archivo `Analisis_CleanArchitecture.drawio` incluido en el proyecto.

---

## 3. Arquitectura del Sistema: Clean Architecture + DDD

El pilar fundamental de la arquitectura es la **Regla de Dependencias (The Dependency Rule)**:
> *Las dependencias de código fuente solo pueden apuntar hacia adentro, en dirección a las políticas de mayor nivel (el Dominio).*

```
┌──────────────────────────────────────────────────────────────┐
│  CAPA 4: FRAMEWORKS Y DRIVERS (Externa)                      │
│  FastAPI · Uvicorn · PostgreSQL · SQLModel · Alembic · JWT   │
│                                                              │
│   ┌────────────────────────────────────────────────────────┐ │
│   │  CAPA 3: ADAPTADORES DE INTERFAZ (app/infra)           │ │
│   │  Routers API · Repositorios DB · Unit of Work Impl     │ │
│   │                                                        │ │
│   │   ┌──────────────────────────────────────────────────┐ │ │
│   │   │  CAPA 2: APLICACIÓN / CASOS DE USO (app/core)    │ │ │
│   │   │  CreateUser · CreateRol · DTOs · Puertos Protocol│ │ │
│   │   │                                                  │ │ │
│   │   │   ┌────────────────────────────────────────────┐ │ │ │
│   │   │   │  CAPA 1: DOMINIO (El Núcleo Puro)          │ │ │ │
│   │   │   │  Entidades (User, Rol)                     │ │ │ │
│   │   │   │  Objetos de Valor (Email, Password, ID)    │ │ │ │
│   │   │   │  Excepciones de Dominio (DomainException)  │ │ │ │
│   │   │   │  REGLA: 0 IMPORTS DE LIBRERÍAS EXTERNAS    │ │ │ │
│   │   │   └────────────────────────────────────────────┘ │ │ │
│   │   └──────────────────────────────────────────────────┘ │ │
│   └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Descripción de las 4 Capas

| Capa | Directorio | Responsabilidad | ¿Qué tiene prohibido? |
| :--- | :--- | :--- | :--- |
| **1. Dominio** | `app/core/entities/`<br>`app/core/value_objects/` | Reglas esenciales de negocio, invariantes y validación de tipos primitivos. | Prohibido importar FastAPI, SQLAlchemy, SQLModel o cualquier framework. |
| **2. Aplicación** | `app/core/usecases/`<br>`app/core/dtos/`<br>`app/core/ports/` | Orquestación de casos de uso específicos y definición de interfaces (Puertos / `Protocol`). | No conoce detalles de la base de datos ni de peticiones HTTP. |
| **3. Adaptadores** | `app/infra/api/routers/`<br>`app/infra/db/repositories/`<br>`app/infra/db/unit_of_work/` | Convierte datos del exterior (JSON HTTP, filas SQL) en objetos que el dominio y los casos de uso entienden. | No define reglas de negocio esenciales. |
| **4. Frameworks** | `app/infra/db/models/`<br>`app/infra/api/app.py`<br>`migrations/` | Herramientas y tecnologías (FastAPI, Uvicorn, PostgreSQL, Alembic). | Es la capa descartable; si cambias PostgreSQL por Mongo, el Dominio no se entera. |

---

## 4. Estructura del Código y Componentes Clave

```text
python-clean-architecture-master/
├── app/
│   ├── core/                           # ─── CAPA 1 & 2: EL NÚCLEO (DOMINIO Y APLICACIÓN)
│   │   ├── entities/                   # Entidades con identidad única y reglas
│   │   │   ├── user.py                 # Entidad User (contiene referencia opcional a Rol)
│   │   │   └── rol.py                  # Entidad Rol (contiene user_id obligatorio)
│   │   ├── value_objects/              # Objetos inmutables autovalidados
│   │   │   ├── email.py                # Email (valida formato con Regex)
│   │   │   ├── password.py             # Password (valida longitud mínima de 8 caracteres)
│   │   │   ├── id.py                   # ID (valida formato UUIDv4 canónico)
│   │   │   └── role_name.py            # RoleName (valida formato de rol)
│   │   ├── dtos/                       # Data Transfer Objects (Pydantic / Dataclasses)
│   │   │   ├── user.py                 # CreateUserRequest, UserResponse, etc.
│   │   │   └── rol.py                  # CreateRolRequest, RolResponse, etc.
│   │   ├── ports/                      # Contratos de interfaces (DIP) usando typing.Protocol
│   │   │   ├── repositories/           # UserRepo, RolRepo
│   │   │   ├── unit_of_work/           # UserUnitOfWork, RolUnitOfWork
│   │   │   └── security/               # Hasher, JWTProvider
│   │   ├── usecases/                   # Lógica de la aplicación
│   │   │   ├── user/                   # CreateUser, GetUser, UpdateUser, DeleteUser
│   │   │   ├── auth/                   # AuthenticateUser
│   │   │   └── rol/                    # CreateRol, GetRol, UpdateRol, DeleteRol
│   │   └── exceptions.py               # Excepciones semánticas del negocio
│   │
│   ├── infra/                          # ─── CAPA 3 & 4: ADAPTADORES E INFRAESTRUCTURA
│   │   ├── api/                        # Adaptadores de entrada Web (FastAPI)
│   │   │   ├── app.py                  # Fábrica create_app()
│   │   │   ├── lifespan.py             # Ciclo de vida del servidor (apertura/cierre recursos)
│   │   │   ├── routers/                # Endpoints HTTP (v1/user.py, v1/rol.py, v1/auth.py)
│   │   │   └── dependencies/           # Inyección de dependencias (DI Providers)
│   │   ├── db/                         # Adaptadores de persistencia
│   │   │   ├── models/                 # Modelos ORM relacionales (DBUser, DBRol)
│   │   │   ├── repositories/           # Implementaciones SQLModelUserRepo, SQLModelRolRepo
│   │   │   └── unit_of_work/           # Implementaciones con AsyncSession
│   │   └── security/                   # Implementación de Hasher (Passlib / Bcrypt)
│   ├── config.py                       # Configuración y lectura de .env (pydantic-settings)
│   ├── logger.py                       # Logging unificado de la aplicación
│   └── __main__.py                     # Punto de entrada de ejecución: start_server()
├── migrations/                         # Migraciones de esquema con Alembic
├── tests/                              # Suite de pruebas automatizadas
│   ├── unit/                           # Pruebas unitarias de Dominio y Casos de Uso (rápidas, con mocks)
│   └── integration/                    # Pruebas de integración con la API
├── pyproject.toml                      # Manifiesto de dependencias y scripts de arranque
└── README.md                           # Documentación rápida original
```

### Componentes Cruciales explicados:
1. **Value Objects (Objetos de Valor)**: Primitivas inmutables (`@dataclass(frozen=True)`). Hacen que sea **imposible** representar un estado inválido en la aplicación. Si un email no tiene `@` o un ID no es UUID, lanza un error inmediatamente al instanciarse.
2. **Puertos (`Protocol`)**: Clases abstractas de Python (`typing.Protocol`) que definen qué necesita el dominio del exterior sin saber quién se lo entregará.
3. **Unit of Work (`UoW`)**: Patrón que agrupa múltiples operaciones de repositorios dentro de una **única transacción atómica** de base de datos (`async with uow: ... await uow.commit()`). Si algo falla en el camino, se cancela todo automáticamente (*rollback*).

---

## 5. Flujo Detallado de una Petición HTTP

Para entender cómo interactúan los componentes, sigamos paso a paso qué ocurre cuando un cliente envía una petición para registrar un nuevo Rol:

```http
POST /api/v1/roles HTTP/1.1
Content-Type: application/json

{
  "name": "Administrador",
  "user_id": "8a32b6e1-95ec-4b8c-85fa-12003c270d1e"
}
```

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Cliente HTTP
    participant Router as RolRouter (FastAPI)
    participant DI as RolDIProvider
    participant UC as CreateRolUsecase
    participant UoW as SQLModelRolUoW
    participant Ent as Dominio (Rol & VOs)
    participant Repo as SQLModelRolRepo
    participant DB as PostgreSQL

    Cliente->>Router: POST /api/v1/roles (JSON Payload)
    Note over Router: Valida formato JSON con Pydantic DTO (CreateRolRequest)
    Router->>DI: Solicita dependencia (CreateRolUsecase)
    DI->>UoW: Instancia UoW con AsyncSession
    DI->>UC: Inyecta UoW en CreateRolUsecase
    Router->>UC: execute(request: CreateRolRequest)

    rect rgb(235, 245, 255)
        Note over UC,UoW: Reglas de Negocio en Aplicación
        UC->>UoW: async with uow:
        UC->>UoW: uow.user_repo.get_by_id(user_id)
        UoW->>DB: SELECT * FROM users WHERE id = :user_id
        DB-->>UoW: Retorna usuario (Existe)
        
        UC->>UoW: uow.rol_repo.get_by_user_id(user_id)
        UoW->>DB: SELECT * FROM roles WHERE user_id = :user_id
        DB-->>UoW: None (Usuario aún no tiene rol)

        UC->>Ent: Instancia Entidad Rol(id, name, user_id)
        Note over Ent: Auto-validación de invariantes en Value Objects
    end

    rect rgb(255, 240, 240)
        Note over UC,DB: Persistencia en Base de Datos
        UC->>UoW: uow.rol_repo.save(rol)
        UoW->>Repo: save(rol)
        Repo->>DB: INSERT INTO roles (id, name, user_id) VALUES (...)
        UC->>UoW: await uow.commit()
        UoW->>DB: COMMIT TRANSACTION
    end

    UC-->>Router: Retorna RolResponse (DTO)
    Router-->>Cliente: HTTP 201 Created (JSON RolResponse)
```

---

## 6. La Relación 1:1 entre Usuario (User) y Rol (Rol)

Uno de los requerimientos más estrictos del sistema es garantizar que **un usuario puede tener a lo sumo un rol, y un rol debe pertenecer exactamente a un usuario**.

Esta relación está blindada en **3 niveles de defensa**:

```
[1. DOMINIO]       User.rol.user_id == User.id  (Invariante de Entidad)
                         ↕
[2. APLICACIÓN]    CreateRolUsecase verifica:
                   - ¿Existe el usuario? (user_repo.get_by_id)
                   - ¿Tiene ya un rol? (rol_repo.get_by_user_id)
                         ↕
[3. BASE DE DATOS] UNIQUE (user_id) en tabla roles
                   FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

1. **Defensa en Capa de Dominio (`app/core/entities/user.py`)**:
   La entidad `User` tiene un método post-init que valida:
   ```python
   if self.rol is not None and self.rol.user_id != self.id:
       raise DomainException("El rol asignado no coincide con el ID del usuario")
   ```
2. **Defensa en Capa de Aplicación (`app/core/usecases/rol/create_rol.py`)**:
   Antes de permitir la creación, se valida que el usuario exista y que no posea rol asignado:
   ```python
   existing_rol = await self.uow.rol_repo.get_by_user_id(user_id)
   if existing_rol:
       raise UserAlreadyHasRolError(f"User {user_id.value} already has a rol")
   ```
3. **Defensa en Capa de Base de Datos (`app/infra/db/models/rol.py`)**:
   La columna `user_id` en la tabla `roles` posee un índice único relacional (`sa.UniqueConstraint("user_id")`), garantizando que incluso ante carreras concurrentes, la base de datos impedirá físicamente duplicados.

---

## 7. Paso a Paso: Cómo Compilar, Verificar y Ejecutar

Sigue estos pasos ordenados para poner en marcha el proyecto desde cero:

### Paso 1: Clonar y Ubicarse en el Proyecto
```powershell
cd c:\Users\Thinkpad\Downloads\Arquitectura\python-clean-architecture-master
```

### Paso 2: Crear / Activar el Entorno Virtual
Si ya existe la carpeta `.venv`:
```powershell
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```
Si vas a crearlo de cero:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### Paso 3: Configurar la Base de Datos
Tienes dos alternativas:

#### Alternativa A: Con Docker (La más sencilla)
Abre Docker Desktop y corre en la terminal:
```powershell
docker compose up pg-db -d
```
Esto creará un contenedor con PostgreSQL listo, accesible en `localhost:5432` con usuario `postgres` y clave `passwd`.

#### Alternativa B: Con tu PostgreSQL local de Windows
Abre tu archivo `.env` y coloca la contraseña real que creaste al instalar PostgreSQL:
```ini
DB_URL="postgresql+asyncpg://postgres:TU_CLAVE_AQUI@localhost:5432/app_dev"
```
Asegúrate de crear la base de datos `app_dev` mediante pgAdmin o psql:
```sql
CREATE DATABASE app_dev;
```

### Paso 4: Ejecutar las Migraciones de Base de Datos
Para crear las tablas `users` y `roles` con sus restricciones:
```powershell
alembic upgrade head
```

### Paso 5: Iniciar el Servidor Web
Ejecuta:
```powershell
.\.venv\Scripts\python -m app
```

Verás una salida como esta en tu consola:
```text
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
```

### Paso 6: Explorar y Probar la API
Abre tu navegador web e ingresa a:
* **Swagger UI (Documentación interactiva)**: [http://localhost:8080/docs](http://localhost:8080/docs)
* **ReDoc (Documentación alternativa)**: [http://localhost:8080/redoc](http://localhost:8080/redoc)
* **Health Check**: [http://localhost:8080/health-check](http://localhost:8080/health-check)

> 💡 **Nota importante**: Como es un servidor web en escucha activa, la terminal permanecerá abierta mostrando los registros de cada petición HTTP. Para apagar el servidor en cualquier momento, presiona **`Ctrl + C`**.

---

## 8. Pruebas Automatizadas y Aseguramiento de Calidad

El proyecto cuenta con un sistema de verificación estricto para garantizar que ningún cambio rompa la arquitectura.

### 1. Pruebas Unitarias (No requieren Base de Datos)
Comprueban toda la lógica del dominio, entidades, objetos de valor y casos de uso en memoria usando Mocks:
```powershell
.\.venv\Scripts\pytest tests/unit/
```
*(Resultado esperado: 75 pruebas pasadas al 100%).*

### 2. Análisis Estático de Tipos (Mypy)
Verifica que los contratos e interfaces (`Protocol`) se cumplan rigurosamente:
```powershell
.\.venv\Scripts\mypy app tests
```
*(Resultado esperado: Success: no issues found in 100 source files).*

### 3. Linter y Formato (Ruff)
Comprueba el estilo y detecta posibles errores de sintaxis:
```powershell
.\.venv\Scripts\ruff check .
```

---

## 9. Resolución de Problemas Comunes (Troubleshooting)

### Error 1: `la autentificación password falló para el usuario "postgres"`
* **Causa**: La contraseña configurada en `.env` (`passwd`) no coincide con la de tu instalación local de PostgreSQL.
* **Solución**: Corrige la contraseña en el archivo `.env` o utiliza Docker Compose (`docker compose up pg-db -d`).

### Error 2: `connection was closed in the middle of operation`
* **Causa**: El servicio PostgreSQL rechazó la conexión entrante antes del saludo inicial, comúnmente debido a rechazo de autenticación o falta de la base de datos destino (`app_dev`).
* **Solución**: Verifica que la base de datos `app_dev` exista y que el puerto `5432` no esté bloqueado por un firewall.

### Error 3: "La terminal se queda pegada al correr `python -m app`"
* **Explicación**: No está bloqueada ni pegada. Al ser un servidor web, Uvicorn entra en un bucle de eventos asíncrono a la espera de peticiones. Abre [http://localhost:8080/docs](http://localhost:8080/docs) en tu navegador para interactuar con él.

---

## 📌 Resumen de Comandos Frecuentes

| Tarea | Comando en PowerShell |
| :--- | :--- |
| **Iniciar la API** | `.\.venv\Scripts\python -m app` |
| **Ejecutar Pruebas Unitarias** | `.\.venv\Scripts\pytest tests/unit/` |
| **Ejecutar Pruebas de Integración** | `.\.venv\Scripts\pytest tests/integration/` |
| **Comprobar Tipos (Mypy)** | `.\.venv\Scripts\mypy app tests` |
| **Revisar Sintaxis (Ruff)** | `.\.venv\Scripts\ruff check .` |
| **Aplicar Migraciones** | `.\.venv\Scripts\alembic upgrade head` |
| **Prueba de Humo Rápida** | `Invoke-RestMethod http://localhost:8080/health-check` |
