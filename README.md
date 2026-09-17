# Repositorio de Arquitecturas de Software

Bienvenido al repositorio de arquitecturas de software. Este repositorio contiene implementaciones de referencia de diferentes patrones arquitectónicos para APIs backend desarrolladas en Python con FastAPI.

Los proyectos se encuentran completamente separados e independientes en la rama **David_Perez**.

---

## 📁 Proyectos Disponibles

### 1. [Python Clean Architecture](./python-clean-architecture)
Implementación siguiendo los principios de **Clean Architecture (Arquitectura Limpia)** y **Hexagonal Architecture (Puertos y Adaptadores)**.
* **Propósito**: Máximo desacoplamiento del framework, base de datos y librerías externas respecto a las reglas de negocio y entidades de dominio.
* **Estructura clave**:
  * core/: Entidades de dominio, casos de uso, interfaces/puertos y excepciones de negocio.
  * infra/: Implementaciones de puertos, adaptadores de base de datos (SQLModel/PostgreSQL), repositorios, API web (FastAPI routers) y seguridad.
  * docs/: Documentación detallada, manuales de uso y diagramas de arquitectura ([Analisis_CleanArchitecture.drawio](./python-clean-architecture/docs/Analisis_CleanArchitecture.drawio)).
* **Gestor de dependencias**: Poetry (pyproject.toml, poetry.lock).

### 2. [FastAPI Layered API](./fastapi-layered-api)
Implementación siguiendo el patrón clásico de **Arquitectura por Capas (Layered / N-Tier Architecture)**.
* **Propósito**: Separación clara de responsabilidades en capas lógicas estándar para desarrollo ágil y estructurado.
* **Estructura clave**:
  * pi/: Capa de presentación (endpoints, routers, dependencias de FastAPI).
  * services/: Capa de servicios (lógica de negocio y orquestación).
  * epositories/: Capa de acceso a datos (interacción con la base de datos).
  * models/: Modelos de base de datos (SQLAlchemy ORM).
  * schemas/: Esquemas de validación y transferencia de datos (Pydantic DTOs).
  * core/: Configuraciones generales y utilidades de seguridad (JWT, hash de passwords).
  * db/: Conexión y sesión de base de datos.
* **Gestor de dependencias**: equirements.txt.

---

## 📊 Comparativa de Arquitecturas

| Criterio | Clean Architecture (python-clean-architecture) | Layered Architecture (astapi-layered-api) |
| :--- | :--- | :--- |
| **Enfoque Principal** | Reglas de negocio en el centro (Domain-Centric) | Flujo de datos lineal de arriba hacia abajo |
| **Inversión de Dependencias** | Sí (Puertos/Interfaces en core, implementados en infra) | Opcional / directa (Servicios llaman a Repositorios) |
| **Independencia de Framework** | Alta (el núcleo de dominio no conoce FastAPI) | Media (orientado al framework y bibliotecas) |
| **Complejidad Inicial** | Mayor curva de aprendizaje | Muy intuitiva y rápida de poner en marcha |
| **Idoneidad** | Sistemas empresariales medianos a grandes, alta volatilidad técnica | Proyectos ágiles, microservicios estándar y APIs CRUD |

---

## 🚀 Cómo Ejecutar Cada Proyecto

### Opción A: Clean Architecture
``bash
cd python-clean-architecture
cp .env.example .env
# Con Docker:
docker compose up --build
# O localmente con Poetry:
poetry install
poetry run uvicorn app:app --reload
``

### Opción B: Layered API
``bash
cd fastapi-layered-api
cp .env.example .env
# Localmente con virtualenv:
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
``

---

## 🌿 Estructura de Ramas en el Repositorio

* **David_Perez**: Rama principal de desarrollo donde conviven ambos proyectos organizados y documentados.
* **main / dev**: Ramas base limpias destinadas a versiones de entrega o releases.
