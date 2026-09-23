# Informe de Auditoría: Top 10 Criterios de API REST

**Proyecto:** `fastapi-layered-api` (Users, Tasks & Categories API)  
**Estándares de Referencia:** Modelo de Madurez de Richardson (Nivel 2-3), RFCs de HTTP (RFC 7231, RFC 5789, RFC 9457, RFC 6749, RFC 7519) y OWASP API Security Top 10 (2023).  
**Fecha:** Septiembre 2026  
**Resultado Global:** **Excelente (96/100) — Cumplimiento Enterprise**

---

## Resumen Ejecutivo

| # | Criterio de Evaluación | Estado | Calificación | Evidencia en Código |
|---|------------------------|--------|:------------:|---------------------|
| 1 | **Modelado y Nomenclatura de URIs** | Cumple | 10/10 | `/api/v1/users`, `/api/v1/tasks`, `/api/v1/categories` |
| 2 | **Semántica Canónica de Verbos HTTP** | Cumple | 10/10 | `GET`, `POST`, `PATCH`, `DELETE` con semántica estricta |
| 3 | **Códigos de Estado HTTP Estándar** | Cumple | 10/10 | 200, 201, 204, 400, 401, 403, 404, 409, 422 |
| 4 | **Arquitectura Sin Estado (Statelessness)** | Cumple | 10/10 | Tokens Bearer JWT autocontenidos (RFC 7519) |
| 5 | **Separación de Contratos y Representaciones (DTOs)** | Cumple | 10/10 | Schemas Pydantic v2 vs Modelos ORM SQLAlchemy 2.0 |
| 6 | **Paginación y Control de Consumo de Recursos** | Cumple | 10/10 | Query params `page`, `page_size` con límites (`le=100`) |
| 7 | **Estandarización de Formato de Errores** | Parcial | 8/10 | Esquema `{"detail": "..."}` y exception handlers |
| 8 | **Seguridad y Control de Acceso (OWASP API Top 10)** | Cumple | 10/10 | Mitigación BOLA/IDOR, Argon2 + dummy hash |
| 9 | **Estrategia de Versionado de la API** | Cumple | 9/10 | Prefijo en URL `/api/v1` desacoplado por agregador |
| 10 | **Autodescripción y Documentación (OpenAPI)** | Cumple | 9/10 | Swagger UI (`/docs`), ReDoc (`/redoc`), OpenAPI 3.1 |

**Puntaje Total:** **96 / 100**

---

## Análisis Detallado por Criterio

### 1. Modelado y Nomenclatura de URIs
* **Principio:** Los recursos deben nombrarse mediante sustantivos en plural, evitando verbos o acciones en la ruta, estructurados en jerarquías lógicas y en minúsculas.
* **Evaluación del Proyecto:** **CUMPLE (10/10)**
* **Hallazgos:**
  - Rutas canónicas:
    - `/api/v1/users` (colección) y `/api/v1/users/{user_id}` (recurso individual).
    - `/api/v1/tasks` y `/api/v1/tasks/{task_id}`.
    - `/api/v1/categories` y `/api/v1/categories/{category_id}`.
  - No existen verbos en las rutas (ej. no se usa `/create-user` ni `/deleteTask`). Las acciones quedan delegadas exclusivamente a los métodos HTTP.
  - Nombres coherentes en minúsculas (`kebab-case` / sustantivos simples).

---

### 2. Semántica Canónica de Verbos HTTP
* **Principio:** Cada verbo HTTP debe emplearse de acuerdo a las especificaciones RFC 7231 y RFC 5789:
  - `GET`: Seguro e idempotente (solo lectura).
  - `POST`: No idempotente (creación o procesamiento).
  - `PUT`: Reemplazo completo e idempotente.
  - `PATCH`: Modificación parcial.
  - `DELETE`: Eliminación idempotente.
* **Evaluación del Proyecto:** **CUMPLE (10/10)**
* **Hallazgos:**
  - `GET /tasks`, `GET /categories` no provocan mutaciones en la base de datos.
  - `POST /tasks`, `POST /categories` crean nuevas entidades retornando su identificador.
  - `PATCH /tasks/{id}` y `PATCH /categories/{id}` reciben schemas donde todos los campos son opcionales (`TaskUpdate`, `CategoryUpdate`), cumpliendo a cabalidad con la semántica de modificación parcial.
  - `DELETE` elimina el recurso sin requerir cuerpo de petición.

---

### 3. Códigos de Estado HTTP Estándar
* **Principio:** La API debe comunicarse a través de los códigos de respuesta del estándar HTTP, sin encapsular errores en respuestas 200 con banderas JSON.
* **Evaluación del Proyecto:** **CUMPLE (10/10)**
* **Hallazgos:**
  - `200 OK`: Peticiones de lectura y actualización exitosas.
  - `201 Created`: Creación de usuarios, tareas y categorías.
  - `204 No Content`: Eliminación de recursos con cuerpo vacío.
  - `400 Bad Request`: Captura de `DomainError` en manejador global para prevenir errores internos.
  - `401 Unauthorized`: Ausencia o invalidez de token JWT, con cabecera reglamentaria `WWW-Authenticate: Bearer`.
  - `403 Forbidden`: Acceso a tareas ajenas (violación BOLA) o cuentas deshabilitadas.
  - `404 Not Found`: Solicitud de IDs inexistentes (`UserNotFoundError`, `TaskNotFoundError`, `CategoryNotFoundError`).
  - `409 Conflict`: Intentos de registrar emails duplicados o nombres de categorías ya existentes.
  - `422 Unprocessable Entity`: Errores de validación de formato/tipos gestionados por FastAPI y Pydantic.

---

### 4. Arquitectura Sin Estado (Statelessness)
* **Principio:** Roy Fielding establece que la sesión de cliente no debe residir en el servidor. Cada petición debe contener toda la información contextual para ser autorizada y procesada.
* **Evaluación del Proyecto:** **CUMPLE (10/10)**
* **Hallazgos:**
  - Se utiliza el estándar OAuth2 Bearer Token con JSON Web Tokens (**JWT**, RFC 7519).
  - El token es firmado criptográficamente con algoritmo `HS256` y clave secreta `SECRET_KEY`.
  - Contiene los *claims* estándar: `sub` (identificador del sujeto), `iat` (momento de emisión) y `exp` (tiempo de expiración).
  - El servidor no guarda sesiones en memoria, lo que permite escalabilidad horizontal inmediata detrás de un balanceador de carga.

---

### 5. Separación de Contratos y Representaciones (DTOs vs ORM)
* **Principio:** La capa de persistencia (tablas/modelos de BD) debe estar completamente desacoplada de la capa de transporte público para evitar fugas de información (*Excessive Data Exposure* / *Mass Assignment*).
* **Evaluación del Proyecto:** **CUMPLE (10/10)**
* **Hallazgos:**
  - Los modelos ORM SQLAlchemy 2.0 ([User](file:///c:/Users/Thinkpad/Downloads/fastapi-layered-api/fastapi-layered-api/app/models/user.py), [Task](file:///c:/Users/Thinkpad/Downloads/fastapi-layered-api/fastapi-layered-api/app/models/task.py), [Category](file:///c:/Users/Thinkpad/Downloads/fastapi-layered-api/fastapi-layered-api/app/models/category.py)) **nunca** se retornan directamente al cliente.
  - Se definen esquemas Pydantic v2 diferenciados por propósito:
    - `Base`: Campos comunes.
    - `Create`: Campos requeridos al insertar.
    - `Update`: Campos opcionales para parches.
    - `Public`: Contrato de salida seguro mediante `model_config = ConfigDict(from_attributes=True)`.
  - Ejemplo crítico: El campo `hashed_password` existe en la tabla `users` pero está ausente en `UserPublic`, impidiendo fugas accidentales.

---

### 6. Paginación y Control de Consumo de Recursos
* **Principio:** Prevenir ataques de Denegación de Servicio (DoS por agotamiento de recursos — OWASP API4:2023) mediante paginación acotada en todas las colecciones.
* **Evaluación del Proyecto:** **CUMPLE (10/10)**
* **Hallazgos:**
  - Todos los endpoints de colección (`GET /users`, `GET /tasks`, `GET /categories`) implementan paginación:
    - `page: Query(ge=1, default=1)`
    - `page_size: Query(ge=1, le=100, default=20)`
  - La respuesta envuelve los elementos con metadatos estructurados (`items`, `total`, `page`, `page_size`).
  - Se impide que un cliente malicioso solicite `page_size=1000000`, evitando bloqueos en la base de datos o sobrecarga de memoria en el servidor.

---

### 7. Estandarización de Formato de Errores
* **Principio:** Los errores deben tener una estructura consistente y predecible a través de toda la API, idealmente alineada con especificaciones modernas como el RFC 9457 (*Problem Details for HTTP APIs*).
* **Evaluación del Proyecto:** **PARCIAL (8/10)**
* **Hallazgos:**
  - **Fortalezas:** Todas las respuestas de error siguen una estructura JSON uniforme `{"detail": "..."}` mediante el schema [`ErrorResponse`](file:///c:/Users/Thinkpad/Downloads/fastapi-layered-api/fastapi-layered-api/app/schemas/common.py). Se cuenta con un manejador global de excepciones `DomainError` en `main.py` que previene respuestas `500` con stack traces de Python.
  - **Oportunidad de Mejora:** Para alcanzar el nivel más avanzado de madurez REST, se recomienda adoptar el formato **RFC 9457** (`type`, `title`, `status`, `detail`, `instance`).

---

### 8. Seguridad y Control de Acceso (OWASP API Security Top 10)
* **Principio:** Una API REST debe implementar mecanismos robustos de autenticación, autorización a nivel de objeto y protección criptográfica.
* **Evaluación del Proyecto:** **CUMPLE (10/10)**
* **Hallazgos:**
  - **OWASP API1:2023 (BOLA / IDOR):** En `TaskService` y `UserService` se verifica explícitamente que `task.owner_id == current_user.id` o que el usuario sea superusuario, bloqueando accesos no autorizados con `403 Forbidden`.
  - **OWASP API2:2023 (Broken Authentication):**
    - Hashing de contraseñas con **Argon2** (`pwdlib`), resistente a GPU/ASIC.
    - Mitigación de ataques de temporización (*Timing Attacks*): Se calcula un *dummy hash* cuando un usuario no existe para que el tiempo de respuesta sea constante.
    - Expiración de tokens estricta (`ACCESS_TOKEN_EXPIRE_MINUTES`).
    - Verificación estricta de algoritmo (`algorithms=["HS256"]`) para prevenir ataques de *alg confusion*.
  - **Endpoints Públicos vs Protegidos:** La entidad `Category` expone lecturas públicas y protege mutaciones, demostrando un control de acceso granular y coherente.

---

### 9. Estrategia de Versionado de la API
* **Principio:** La API debe contemplar un esquema claro de evolución que permita introducir cambios de contrato sin romper integraciones activas.
* **Evaluación del Proyecto:** **CUMPLE (9/10)**
* **Hallazgos:**
  - Versionado explícito en la URI: `/api/v1/`.
  - Arquitectura modular: El archivo [app/api/v1/api.py](file:///c:/Users/Thinkpad/Downloads/fastapi-layered-api/fastapi-layered-api/app/api/v1/api.py) agrega los routers de la versión actual. Agregar una futura versión `v2` solo requiere crear `app/api/v2/api.py` sin alterar el código existente.
  - **Oportunidad de Mejora:** Si bien el versionado en la URL es el más extendido y práctico en la industria, no implementa versionado por cabeceras de contenido (`Accept: application/vnd.myapi.v1+json`). Sin embargo, el enfoque actual es completamente válido y recomendado por FastAPI.

---

### 10. Autodescripción y Documentación (OpenAPI / Discoverability)
* **Principio:** La API debe ser autodescriptiva, permitiendo a clientes humanos y máquinas entender contratos, formatos y opciones de autenticación sin recurrir a documentación externa desactualizada.
* **Evaluación del Proyecto:** **CUMPLE (9/10)**
* **Hallazgos:**
  - Generación automática de especificación **OpenAPI 3.1** en `/openapi.json`.
  - Documentación interactiva Swagger UI disponible en `/docs` con botón *Authorize* (OAuth2 Password Flow).
  - Documentación alternativa ReDoc disponible en `/redoc`.
  - Respuestas de error documentadas explícitamente en los decoradores (`responses={404: ..., 409: ...}`).
  - **Oportunidad de Mejora:** Para alcanzar el Nivel 3 del Modelo de Madurez de Richardson (*HATEOAS*), se podrían incluir hipervínculos (`_links`) en las respuestas para navegar a recursos relacionados.

---

## Conclusiones y Hoja de Ruta

La API implementa un diseño sumamente profesional y alineado con los estándares modernos de desarrollo de software empresarial:
1. **Arquitectura desacoplada**: Capas bien delimitadas con dependencias unidireccionales (**Routers $\rightarrow$ Services $\rightarrow$ Repositories $\rightarrow$ Models**).
2. **Seguridad rigurosa**: Protección activa contra BOLA y Broken Authentication.
3. **Flexibilidad de acceso**: Coexistencia de endpoints abiertos al público (`Category`) con endpoints estrictamente controlados (`User`, `Task`).

### Recomendaciones Futuras
1. Implementar *Rate Limiting* (ej. `slowapi` con Redis) en endpoints sensibles (`/auth/login`).
2. Migrar las respuestas de error al estándar RFC 9457 (*Problem Details*).
3. Implementar cabeceras de cacheo HTTP (`ETag`, `Cache-Control`) en endpoints públicos como `/categories`.
