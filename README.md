
# Prospector Engine v1.0.0

Motor de extracción y enriquecimiento de prospectos originalmente desarrollado como parte de **Prospector CLI v0.7.0**.

Este repositorio contiene la versión reutilizable del motor de prospección que posteriormente será integrado como un **módulo interno de Prospector Service**, desarrollado con Python + FastAPI.

El objetivo de `Prospector Engine v1.0.0` es conservar y estabilizar la capacidad funcional de extracción existente, separándola de las responsabilidades propias de la CLI y preparando una interfaz interna reutilizable por otros componentes.

> **Estado:** Versión 1.0.0 — Alcance inicial estable del motor  
> **Origen:** Prospector CLI v0.7.0  
> **Propósito:** Extracción, enriquecimiento, normalización y deduplicación de prospectos  
> **Consumidor previsto:** Prospector Service  
> **Fuente soportada:** Google Maps  
> **Implementación:** Python + Playwright

---

# 1. Descripción

Prospector Engine es un motor especializado en la extracción de información de negocios a partir de consultas de búsqueda.

El motor realiza un pipeline compuesto por:

```text
SearchQuery
    ↓
Google Maps Navigation
    ↓
Result Loading / Scrolling
    ↓
Initial Business Extraction
    ↓
Detail Panel Enrichment
    ↓
Website Enrichment
    ↓
Normalization
    ↓
Deduplication
    ↓
Business[]
````

La responsabilidad principal del Engine es transformar una consulta de prospección en un conjunto estructurado de prospectos.

El Engine no administra usuarios, tenants, campañas ni reglas de negocio de la plataforma.

---

# 2. Objetivo de v1.0.0

La versión `1.0.0` busca proporcionar una base de extracción:

* funcional;
* reutilizable;
* independiente de la CLI;
* determinista en la medida permitida por las fuentes externas;
* con manejo básico de errores;
* con lifecycle controlado de recursos;
* con logging;
* con normalización;
* con deduplicación;
* y suficientemente estable para integrarse dentro de Prospector Service.

La prioridad de esta versión es:

```text
Funcionalidad
    >
Simplicidad
    >
Determinismo
    >
Mantenibilidad
    >
Abstracción
```

No se busca realizar una sobreingeniería del motor.

La implementación deberá privilegiar soluciones simples que resuelvan las necesidades reales del proyecto.

---

# 3. Relación con Prospector Service

Prospector Engine **no será un servicio independiente** dentro de la arquitectura final.

Su destino previsto es formar parte de:

```text
┌─────────────────────────────────────────┐
│           Prospector Service            │
│              Python + FastAPI           │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │       Prospector Engine         │   │
│   │                                 │   │
│   │ Google Maps Extraction           │   │
│   │ Detail Enrichment               │   │
│   │ Website Enrichment              │   │
│   │ Normalization                   │   │
│   │ Deduplication                   │   │
│   └─────────────────────────────────┘   │
│                                         │
│       API / Services / DTOs             │
└─────────────────────────────────────────┘
```

La arquitectura general prevista es:

```text
Flutter
   │
   ▼
SaaS Backend
   │
   │ HTTP
   ▼
Prospector Service
   │
   ├── API
   ├── DTOs
   ├── Validation
   ├── Service Layer
   └── Prospector Engine
          │
          ├── Google Maps
          └── Websites
```

La responsabilidad de cada componente se mantiene separada:

### Prospector Engine

Contiene la lógica técnica de:

* navegación;
* extracción;
* enriquecimiento;
* normalización;
* deduplicación.

### Prospector Service

Será responsable posteriormente de:

* exponer la API;
* definir DTOs;
* validar requests;
* orquestar ejecuciones;
* administrar errores de servicio;
* controlar la interacción con el Engine.

### SaaS Backend

Será responsable de:

* tenants;
* usuarios;
* autenticación;
* autorización;
* campañas;
* persistencia;
* reglas de negocio;
* administración de resultados.

### Flutter

Será cliente de la plataforma y no tendrá interacción directa con el Engine.

---

# 4. Frontera del Engine

La frontera conceptual del motor es:

```text
SearchQuery
      │
      ▼
Prospector Engine
      │
      ▼
SearchResult
      │
      ▼
Business[]
```

El punto de entrada heredado del CLI es:

```python
result = search_businesses(
    query=query,
    limit=limit
)
```

El conjunto de prospectos se encuentra en:

```python
result.businesses
```

La interfaz interna podrá evolucionar durante la integración con Prospector Service, pero la capacidad fundamental permanecerá:

```text
Input
   ↓
Extraction Pipeline
   ↓
Structured Result
```

---

# 5. Alcance funcional de v1.0.0

La versión 1.0.0 incluye las siguientes capacidades.

## 5.1 Búsqueda en Google Maps

El motor soporta inicialmente:

```text
Source.GOOGLE_MAPS
```

La búsqueda utiliza:

```text
keyword + location
```

Ejemplo conceptual:

```text
keyword  = "dentistas"
location = "Tijuana"
```

Consulta:

```text
dentistas Tijuana
```

El Engine navega a Google Maps y ejecuta la búsqueda.

---

# 6. Pipeline de extracción

## 6.1 Search Query

La entrada conceptual contiene:

```text
source
keyword
location
```

Modelo:

```python
SearchQuery(
    source=Source.GOOGLE_MAPS,
    keyword="...",
    location="..."
)
```

El límite de resultados puede proporcionarse como parámetro de ejecución.

---

## 6.2 Browser Initialization

El motor inicia Playwright y Chromium para ejecutar la navegación automatizada.

Flujo:

```text
Engine
   ↓
Playwright
   ↓
Chromium
   ↓
Maps Page
```

Cada ejecución deberá disponer de su propio estado de browser y páginas.

No se utilizará un browser global compartido como estado de aplicación.

---

## 6.3 Google Maps Navigation

La navegación realiza:

1. creación de la página;
2. navegación a Google Maps;
3. resolución del buscador;
4. escritura de la consulta;
5. ejecución de la búsqueda;
6. espera de la página de resultados;
7. espera del feed de resultados.

La navegación está encapsulada principalmente mediante:

```text
NavigationEngine
GoogleMapsNavigation
SelectorEngine
```

---

## 6.4 Result Loading

Google Maps utiliza un feed con carga progresiva.

El motor deberá:

* localizar el feed;
* observar el número de resultados;
* realizar scrolling;
* esperar la actualización del DOM;
* continuar mientras existan nuevos resultados;
* detenerse cuando se alcance el límite;
* detenerse cuando el feed se estabilice.

El comportamiento heredado utiliza:

```text
scroll vertical
+
conteo de resultados
+
ciclos de estabilidad
```

No se implementará paginación formal en v1.0.0.

---

# 7. Initial Business Extraction

Los resultados encontrados se transforman inicialmente en objetos `Business`.

La extracción inicial puede obtener:

```text
name
category
address
phone
```

Los resultados sin una identidad mínima válida, como nombre o href, podrán ser descartados.

El flujo es:

```text
Google Maps DOM
      ↓
Locator
      ↓
Text / Attributes
      ↓
Parser
      ↓
Business inicial
```

---

# 8. Detail Panel Enrichment

Después de la extracción inicial, el motor puede abrir el panel de detalle de cada negocio.

Flujo:

```text
Business inicial
      ↓
Business identity
      ↓
Google Maps Detail Panel
      ↓
Additional information
      ↓
Business enriquecido
```

La etapa puede obtener:

* dirección;
* teléfono;
* website.

La navegación utiliza información temporal del resultado para comprobar que el panel corresponde al negocio esperado.

Entre las verificaciones existentes se encuentran:

* `place_id`;
* URL;
* nombre del negocio;
* identidad temporal.

Si el enriquecimiento falla, el negocio puede conservarse como resultado parcial.

---

# 9. Website Enrichment

Cuando un negocio contiene un website, el motor puede realizar una segunda etapa de enriquecimiento.

Flujo:

```text
Business.website
       ↓
WebsiteCrawler
       ↓
WebsiteDocument
       ↓
WebsiteParser
       ↓
WebsiteExtractor
       ↓
WebsiteMetadata
       ↓
Business
```

La etapa es secundaria:

```text
Google Maps
     ↓
Business
     ↓
Website
     ↓
Additional information
```

Website enrichment no participa en la identificación inicial del negocio.

---

# 10. Información obtenida desde Websites

El Engine puede obtener:

```text
title
description
language
domain
final_url
status_code
emails
links
anchor texts
contact page information
about page information
```

La extracción utiliza principalmente:

```text
Playwright
BeautifulSoup
Regex
Python Standard Library
```

El HTML original no forma parte del resultado final del Engine.

---

# 11. Normalización

La versión 1.0.0 incorpora una etapa explícita de normalización.

Flujo:

```text
Extraction
    ↓
Enrichment
    ↓
Normalization
```

El objetivo es producir datos consistentes antes de la deduplicación y entrega del resultado.

La normalización podrá incluir:

* eliminación de espacios innecesarios;
* limpieza de strings;
* normalización de emails;
* normalización de URLs;
* normalización básica de teléfonos;
* normalización de valores vacíos;
* eliminación de inconsistencias triviales de formato.

La normalización no deberá introducir reglas de negocio del SaaS.

Por ejemplo, el Engine no determina:

```text
¿Este negocio es un prospecto válido?
```

Esa decisión corresponde a la plataforma.

---

# 12. Deduplicación

La versión 1.0.0 incorpora deduplicación básica de resultados.

Esta capacidad es necesaria porque una campaña puede ejecutar múltiples búsquedas cuyos resultados se superponen.

Ejemplo:

```text
Búsqueda 1
"dentistas Tijuana"

A
B
C
D

Búsqueda 2
"clínicas dentales Tijuana"

B
C
E
F
```

Resultado:

```text
A
B
C
D
E
F
```

La deduplicación se realizará después de la normalización:

```text
Extraction
    ↓
Enrichment
    ↓
Normalization
    ↓
Deduplication
    ↓
Business[]
```

## Principios

La deduplicación deberá ser:

* simple;
* determinista;
* reproducible;
* suficientemente efectiva para el alcance del proyecto.

No se contempla inicialmente:

* fuzzy matching avanzado;
* machine learning;
* matching semántico;
* sistemas complejos de scoring.

La estrategia de identidad podrá evolucionar posteriormente.

---

# 13. Modelo Business

El modelo principal del Engine es:

```text
Business
```

La representación inicial contempla:

```text
name
category
address
phone
website
email
language
website_title
website_description
has_contact_page
has_about_page
website_status
```

Durante el pipeline pueden existir otros datos de soporte:

```text
place_id
href
index
identity
```

La versión 1.0.0 podrá revisar la representación de identidad conforme se implemente la deduplicación.

No obstante, cualquier cambio deberá evaluarse contra la necesidad real del consumidor y evitar agregar campos innecesarios.

---

# 14. SearchResult

El resultado estructurado de una ejecución es:

```text
SearchResult
```

Conceptualmente:

```text
SearchResult
├── query
├── businesses
└── execution_time
```

Los prospectos están contenidos en:

```python
result.businesses
```

El total de resultados puede determinarse mediante:

```python
len(result.businesses)
```

---

# 15. Estado de un Business

Un negocio puede atravesar diferentes etapas:

```text
Sin Business
     ↓
Initial Extraction
     ↓
Business inicial
     ↓
Detail Enrichment
     ↓
Business enriquecido
     ↓
Website Enrichment
     ↓
Normalization
     ↓
Business final
```

Un `Business` puede permanecer parcial cuando una etapa secundaria falla.

Ejemplo:

```text
Google Maps
     ↓
Business
     ↓
Detail Panel FAIL
     ↓
Business parcial
```

o:

```text
Business.website
     ↓
Website Crawl FAIL
     ↓
Business parcialmente enriquecido
```

Los fallos de enriquecimiento no necesariamente invalidan el negocio completo.

---

# 16. Manejo de errores

La v1.0.0 establece una separación básica entre errores fatales y resultados parciales.

## Errores fatales

Pueden detener una ejecución:

* fallo al iniciar Playwright;
* fallo al iniciar Chromium;
* imposibilidad de navegar a Google Maps;
* fallo del feed principal;
* fallo de infraestructura necesario para ejecutar la búsqueda.

Conceptualmente:

```text
Fatal error
    ↓
Execution failed
```

---

## Errores recuperables

Pueden permitir continuar:

* fallo de detail panel;
* website inexistente;
* timeout de website;
* HTTP error del website;
* fallo de parsing web;
* información faltante.

Conceptualmente:

```text
Business
    ↓
Enrichment failure
    ↓
Business partial
    ↓
Continue
```

---

## Principio

El Engine debe intentar conservar información válida siempre que sea posible.

No se deberá descartar un negocio completo únicamente porque una etapa secundaria de enriquecimiento haya fallado.

---

# 17. Logging

La versión 1.0.0 elimina la dependencia funcional de `print()` como mecanismo principal de comunicación operacional.

El Engine utilizará logging para registrar eventos relevantes como:

```text
execution started
search started
results loaded
business extracted
detail enrichment failed
website crawl started
website crawl failed
normalization completed
deduplication completed
execution completed
```

El Engine no deberá asumir cómo serán mostrados o almacenados los logs.

El consumidor podrá configurar posteriormente su salida.

---

# 18. Resource Lifecycle

Los recursos principales de una ejecución son:

```text
Playwright
    ↓
Browser
    ↓
Maps Page
    ↓
Website Pages
```

El Engine deberá controlar su ciclo de vida.

Objetivo:

```text
Execution Start
      ↓
Create resources
      ↓
Use resources
      ↓
Cleanup
      ↓
Execution End
```

El cierre de recursos deberá ejecutarse también ante excepciones cuando técnicamente sea posible.

Particularmente:

* Browser;
* Maps Page;
* Website Pages.

La v1.0.0 busca eliminar el riesgo de dejar browsers o páginas abiertos después de una ejecución fallida.

---

# 19. Sincronización

Google Maps y los websites procesados son fuentes dinámicas.

El Engine utiliza principalmente sincronización basada en estado:

```text
wait_for()
wait_for_url()
wait_for_function()
wait_hidden()
wait_detached()
```

Las esperas basadas exclusivamente en tiempo deberán mantenerse al mínimo necesario.

El comportamiento heredado incluye una espera temporal durante el scrolling de Google Maps.

La v1.0.0 podrá mejorar esta sincronización sin cambiar innecesariamente el comportamiento funcional del extractor.

---

# 20. Determinismo

El Engine deberá evitar introducir comportamiento aleatorio o estado global innecesario.

Una misma entrada deberá producir resultados equivalentes siempre que las fuentes externas proporcionen información equivalente.

El comportamiento externo de:

* Google Maps;
* websites;
* red;
* DOM dinámico;

no puede garantizarse completamente.

Por lo tanto, el objetivo de determinismo aplica principalmente al procesamiento interno.

---

# 21. Concurrencia

La v1.0.0 no introduce concurrencia avanzada como requisito funcional.

Cada ejecución deberá mantener su propio estado:

```text
Browser
Page
SelectorEngine
Registry
Business[]
SearchResult
```

No se utilizarán objetos globales mutables para compartir el estado de diferentes ejecuciones.

La ejecución puede realizarse de forma secuencial.

La concurrencia podrá evaluarse posteriormente si los requerimientos de Prospector Service lo justifican.

---

# 22. Dependencias

Las principales dependencias son:

```text
Python
│
├── Playwright
│   └── Chromium
│
├── BeautifulSoup
│
└── Python Standard Library
```

Dependencias operacionales externas:

```text
Google Maps
Websites encontrados
Internet
```

El Engine no requiere:

```text
PostgreSQL
NestJS
Flutter
Redis
RabbitMQ
```

para ejecutar su pipeline principal.

---

# 23. Arquitectura interna

La estructura conceptual de v1.0.0 es:

```text
prospector-engine/

├── src/
│   │
│   ├── core/
│   │   ├── scraper/
│   │   ├── search/
│   │   ├── extraction/
│   │   └── enrichment/
│   │
│   ├── domain/
│   │   ├── business.py
│   │   ├── search_query.py
│   │   ├── search_result.py
│   │   ├── website_document.py
│   │   └── website_metadata.py
│   │
│   ├── navigation/
│   │   ├── navigation_engine.py
│   │   └── google_maps_navigation.py
│   │
│   ├── selectors/
│   │   ├── selector_engine.py
│   │   ├── elector_engine.py
│   │   ├── registry.py
│   │   ├── profiles.py
│   │   └── lazycharge.py
│   │
│   ├── website/
│   │   ├── website_engine.py
│   │   ├── crawler.py
│   │   ├── parser.py
│   │   ├── extractor.py
│   │   ├── metadata.py
│   │   ├── email.py
│   │   └── language.py
│   │
│   └── utils/
│       └── parser.py
│
├── tests/
│
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

Esta estructura representa una organización conceptual y podrá ajustarse durante la implementación.

No todos los componentes deben ser abstraídos desde el inicio.

---

# 24. Componentes principales

## Domain

```text
Business
SearchQuery
SearchResult
WebsiteDocument
WebsiteMetadata
```

Responsabilidad:

Representar la información utilizada por el Engine.

---

## Navigation

```text
NavigationEngine
GoogleMapsNavigation
```

Responsabilidad:

Controlar la navegación de fuentes mediante Playwright.

---

## Selectors

```text
SelectorEngine
ElectorEngine
SelectorRegistry
Profiles
LazyChargeEngine
```

Responsabilidad:

Resolver elementos dinámicos y sincronización específica de la interfaz.

---

## Extraction

```text
Result List
Business Parser
Detail Panel
```

Responsabilidad:

Obtener información de negocios desde Google Maps.

---

## Website

```text
WebsiteEngine
WebsiteCrawler
WebsiteParser
WebsiteExtractor
EmailExtractor
LanguageDetector
MetadataBuilder
```

Responsabilidad:

Obtener y transformar información de sitios web.

---

# 25. Google Maps como Source Adapter

Google Maps representa una fuente concreta y no debe confundirse con toda la lógica del Engine.

Componentes específicos:

```text
GoogleMapsNavigation
Google Maps selectors
Google Maps URL handling
place_id extraction
Maps DOM extraction
```

Dependencias específicas:

```text
a[href*='/maps/place/']
aria-label
div[role='feed']
div[role='main']
h1
div.W4Efsd
data-item-id='address'
```

Estas dependencias pueden cambiar si Google Maps modifica su DOM.

El Engine deberá mantener la lógica específica de Maps lo más localizada posible.

---

# 26. Website Engine como componente secundario

Website Engine constituye una capacidad de enriquecimiento secundaria.

No determina la existencia inicial del negocio.

Flujo:

```text
Google Maps
     ↓
Business
     ↓
Business.website
     ↓
Website Engine
     ↓
Additional metadata
```

Si no existe website:

```text
Business
     ↓
Skip Website Enrichment
```

Si el website falla:

```text
Business
     ↓
Website failure
     ↓
Business partial
```

---

# 27. Identidad y deduplicación

La auditoría original identificó que parte de la identidad del negocio era temporal.

Actualmente pueden utilizarse:

```text
href
place_id
index
name
```

La v1.0.0 incorpora deduplicación, por lo que la identidad del negocio deberá ser suficientemente estable para permitir comparar resultados.

La estrategia inicial deberá privilegiar identificadores fuertes cuando estén disponibles.

Como principio:

```text
Identidad fuerte
    >
Identidad derivada
    >
Comparación textual simple
```

La implementación no deberá convertirse en un sistema complejo de matching.

---

# 28. Data Transformation Map

El flujo completo de transformación es:

```text
SearchQuery
    ↓
Google Maps
    ↓
DOM
    ↓
Locators
    ↓
Raw extracted values
    ↓
Business inicial
    ↓
Detail Panel
    ↓
Business enriquecido
    ↓
WebsiteDocument
    ↓
WebsiteMetadata
    ↓
Business enriquecido
    ↓
Normalization
    ↓
Deduplication
    ↓
SearchResult
    ↓
Business[]
```

Transformaciones principales:

```text
Google Maps aria-label
        ↓
Business.name

Maps text blocks
        ↓
Business.category
Business.address
Business.phone

Maps href
        ↓
Business identity

Website href
        ↓
WebsiteCrawler

HTML
        ↓
WebsiteDocument

WebsiteDocument
        ↓
WebsiteMetadata

WebsiteMetadata
        ↓
Business.email
Business.language
Business.website_title
Business.website_description
Business.website_status
```

---

# 29. Datos que pueden perderse

El Engine busca conservar la información útil para el resultado, pero no necesariamente toda la información disponible en las fuentes.

Datos identificados históricamente como potencialmente descartados:

```text
index
emails adicionales
content_type
HTML original
DOM completo
metadata web no utilizada
```

La v1.0.0 deberá evitar pérdidas innecesarias cuando el dato sea necesario para:

* identificación;
* normalización;
* deduplicación;
* resultado final.

No se conservarán datos únicamente por conservarlos.

---

# 30. Persistencia

Prospector Engine no administra persistencia de plataforma.

No contiene:

```text
Database
ORM
Repositories
Tenant storage
Campaign storage
User storage
```

El Engine produce resultados estructurados:

```text
SearchResult
    ↓
Business[]
```

El consumidor decidirá posteriormente qué hacer con ellos.

---

# 31. Responsabilidades excluidas

## SaaS

El Engine no implementa:

* tenants;
* usuarios;
* roles;
* permisos;
* campañas;
* planes;
* cuotas;
* facturación;
* reglas de negocio.

---

## Seguridad de plataforma

El Engine no implementa:

* autenticación de usuarios;
* autorización;
* JWT;
* sesiones;
* permisos de plataforma.

---

## API

El Engine no implementa:

* FastAPI;
* endpoints HTTP;
* DTOs HTTP;
* contratos REST;
* autenticación HTTP;
* rate limiting de API.

Estas responsabilidades pertenecen a Prospector Service.

---

## CLI

El Engine no implementa:

* `input()`;
* menús;
* impresión interactiva;
* selección de formatos;
* exportación CSV;
* exportación Excel;
* file naming.

---

# 32. CLI como consumidor

La CLI puede utilizar el Engine como consumidor.

Conceptualmente:

```text
Prospector CLI
      │
      ▼
Prospector Engine
      │
      ▼
SearchResult
      │
      ▼
CLI Output / Export
```

La CLI deja de ser parte del motor.

Esto permite que el mismo Engine sea utilizado posteriormente por Prospector Service.

---

# 33. Relación con el futuro Prospector Service

La integración prevista es:

```text
Prospector Service
        │
        ▼
Service Layer
        │
        ▼
Prospector Engine
        │
        ├── Google Maps
        └── Website
```

El Service será responsable de orquestar el Engine.

Conceptualmente:

```text
HTTP Request
     ↓
DTO
     ↓
Validation
     ↓
Prospector Service
     ↓
Prospector Engine
     ↓
SearchResult
     ↓
Service Response
```

El Engine no conocerá la estructura HTTP.

---

# 34. Reutilización desde Prospector Service

El objetivo es que el Service pueda reutilizar directamente el Engine:

```text
Prospector Service
│
└── Prospector Engine
      │
      ├── Extraction
      ├── Enrichment
      ├── Normalization
      └── Deduplication
```

No existe una comunicación:

```text
Service
   │
   │ HTTP
   ▼
Engine
```

dentro de la arquitectura final.

El Engine será un módulo integrado.

---

# 35. Principios de diseño

La versión 1.0.0 seguirá los siguientes principios.

## 1. Reutilizar antes que reescribir

La lógica funcional existente de Prospector CLI será reutilizada siempre que sea viable.

---

## 2. Separar responsabilidades

La lógica del motor no deberá depender de:

* CLI;
* plataforma;
* API;
* persistencia.

---

## 3. Simpleza sobre glamour

No se introducirán abstracciones únicamente por hacer la arquitectura más sofisticada.

---

## 4. Funcionalidad antes que complejidad

Una solución sencilla y funcional tendrá prioridad sobre una solución más compleja que no aporte valor real.

---

## 5. Determinismo

El procesamiento interno deberá evitar comportamientos impredecibles.

---

## 6. Fuente aislada

La lógica específica de Google Maps deberá permanecer localizada como Source Adapter.

---

## 7. Enrichment secundario

Website Enrichment continuará siendo una etapa posterior a la extracción inicial.

---

## 8. Sin reglas de negocio SaaS

El Engine no deberá determinar reglas como:

```text
¿El prospecto es válido?
¿A qué tenant pertenece?
¿A qué campaña pertenece?
¿Debe guardarse?
```

---

## 9. Evitar sobreingeniería

La arquitectura deberá evolucionar conforme aparezcan necesidades reales.

---

# 36. Concurrencia y aislamiento

Cada ejecución debe mantener sus recursos aislados:

```text
Execution A
├── Browser A
├── Page A
├── Businesses A
└── Result A

Execution B
├── Browser B
├── Page B
├── Businesses B
└── Result B
```

No deberán compartirse objetos mutables entre ejecuciones.

Los recursos externos sí pueden ser compartidos indirectamente:

```text
Internet
Google Maps
Websites
CPU
RAM
Chromium resources
```

La concurrencia avanzada queda fuera del alcance inicial.

---

# 37. Reliability

Los principales riesgos conocidos son:

### Google Maps

* cambios de DOM;
* cambios de selectores;
* comportamiento dinámico;
* scrolling;
* ausencia de paginación;
* resultados duplicados.

### Websites

* websites inaccesibles;
* timeouts;
* HTTP errors;
* contenido dinámico;
* HTML incompleto.

### Browser

* consumo elevado de recursos;
* fallos de Chromium;
* páginas abiertas accidentalmente.

### Red

* latencia;
* pérdida de conexión;
* comportamiento variable de servicios externos.

La v1.0.0 busca mitigar los riesgos internos sin intentar controlar completamente el comportamiento de servicios externos.

---

# 38. Pruebas

La versión 1.0.0 deberá contar con pruebas suficientes para validar las partes deterministas del Engine.

Prioridad:

```text
Domain
    ↓
Pure extraction
    ↓
Normalization
    ↓
Deduplication
    ↓
Website parsing
    ↓
Integration pipeline
```

Se deberán priorizar pruebas de:

* `Business`;
* `SearchQuery`;
* `SearchResult`;
* parsers;
* normalización;
* deduplicación;
* extracción de emails;
* detección de idioma;
* transformación de metadata;
* comportamiento ante datos faltantes.

Las pruebas de Google Maps y Playwright podrán requerir integración con servicios externos.

---

# 39. Versionado

La evolución inicial prevista es:

```text
Prospector CLI v0.7.0
        ↓
Engine v0.7.1
        ↓
Engine v0.8.0
        ↓
Engine v0.9.0
        ↓
Engine v1.0.0
```

## v0.7.0

Estado original auditado.

Incluye:

* extracción Maps;
* detail enrichment;
* website enrichment;
* modelos;
* selectores;
* crawling.

---

## v0.7.1

Estabilización del comportamiento existente.

Objetivos:

* separar CLI;
* mejorar lifecycle;
* logging;
* errores;
* cleanup;
* pruebas;
* mantener funcionalidad existente.

---

## v0.8.0

Normalización.

Objetivo:

```text
Extraction
    ↓
Enrichment
    ↓
Normalization
```

---

## v0.9.0

Deduplicación.

Objetivo:

```text
Normalization
    ↓
Deduplication
    ↓
Business[]
```

---

## v1.0.0

Versión estable del Engine.

Incluye:

```text
Extraction
Detail Enrichment
Website Enrichment
Normalization
Deduplication
Error Handling
Logging
Resource Lifecycle
Deterministic Processing
CLI Independence
```

La versión 1.0.0 no representa una arquitectura definitiva.

Representa una versión suficientemente estable para ser integrada dentro de Prospector Service.

---

# 40. Criterio de cierre de v1.0.0

Prospector Engine v1.0.0 se considera funcionalmente completo cuando:

* puede ejecutarse sin `main.py`;
* puede recibir una consulta estructurada;
* puede ejecutar la búsqueda en Google Maps;
* puede cargar resultados;
* puede extraer negocios;
* puede enriquecer detalles;
* puede enriquecer websites;
* puede normalizar resultados;
* puede deduplicar resultados;
* puede devolver un resultado estructurado;
* puede manejar resultados parciales;
* utiliza logging;
* controla el lifecycle de Playwright;
* no depende de la plataforma SaaS;
* no depende de FastAPI;
* no depende de NestJS;
* no depende de Flutter;
* no requiere persistencia;
* mantiene una implementación simple.

---

# 41. Criterio para evitar sobreingeniería

Antes de agregar una nueva capacidad al Engine deberá evaluarse:

```text
¿Es necesaria para extraer, enriquecer,
normalizar o deduplicar prospectos?
          │
      ┌───┴───┐
     Sí       No
      │        │
      ▼        ▼
 Evaluar     Fuera de
 implementación alcance
```

No se incorporarán prematuramente:

* microservicios;
* colas;
* sistemas distribuidos;
* cache distribuida;
* machine learning;
* fuzzy matching complejo;
* múltiples fuentes;
* plugins;
* persistencia;
* métricas avanzadas;
* sistemas de configuración complejos.

Estas capacidades podrán evaluarse posteriormente si aparecen requerimientos reales.

---

# 42. Roadmap posterior

Después de `v1.0.0`, el desarrollo podrá evolucionar según las necesidades de Prospector Service.

Posibles líneas futuras:

```text
v1.x
│
├── Mejoras de extracción
├── Nuevas reglas de normalización
├── Mejor deduplicación
├── Mejor manejo de errores
└── Mejoras de observabilidad
```

Posteriormente podrían evaluarse:

```text
Nuevas fuentes
Mayor concurrencia
Retries
Configuración avanzada
Mejor identidad de negocios
Mayor cobertura de websites
```

Estas capacidades no forman parte del alcance inicial.

---

# 43. Arquitectura objetivo

La arquitectura conceptual completa queda:

```text
┌─────────────────────────────────────────────┐
│                  Flutter                    │
│              Client Application             │
└──────────────────────┬──────────────────────┘
                       │
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────┐
│               SaaS Backend                  │
│             Node.js + NestJS                │
│                                             │
│  ┌────────────┐ ┌────────────┐             │
│  │   Auth     │ │  Tenants   │             │
│  └────────────┘ └────────────┘             │
│                                             │
│  ┌────────────┐ ┌────────────┐             │
│  │ Campaigns  │ │  Business  │             │
│  └────────────┘ └────────────┘             │
└──────────────────────┬──────────────────────┘
                       │
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────┐
│             Prospector Service              │
│                Python + FastAPI             │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │ API / DTOs / Validation / Services   │  │
│  └──────────────────────┬────────────────┘  │
│                         │                   │
│                         ▼                   │
│  ┌───────────────────────────────────────┐  │
│  │         Prospector Engine             │  │
│  │                                       │  │
│  │  Google Maps Extraction               │  │
│  │          ↓                            │  │
│  │  Detail Enrichment                    │  │
│  │          ↓                            │  │
│  │  Website Enrichment                   │  │
│  │          ↓                            │  │
│  │  Normalization                        │  │
│  │          ↓                            │  │
│  │  Deduplication                        │  │
│  │          ↓                            │  │
│  │  Business[]                           │  │
│  └───────────────────────────────────────┘  │
└──────────────────────┬──────────────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Google Maps           Websites
```

---

# 44. Estado del proyecto

`Prospector Engine v1.0.0` representa la primera versión estable del motor de prospección reutilizable.

Su origen es:

```text
Prospector CLI v0.7.0
```

La evolución conceptual es:

```text
CLI
 │
 │ Auditoría
 ▼
Extraction Engine
 │
 │ Separación
 ▼
Prospector Engine
 │
 │ Integración
 ▼
Prospector Service
 │
 │ HTTP
 ▼
SaaS Backend
```

El Engine constituye una capacidad especializada de extracción.

No constituye:

```text
una API pública
un microservicio
una plataforma SaaS
un módulo de autenticación
un sistema de persistencia
```

Su responsabilidad termina en producir información estructurada de prospectos.

---

# 45. Resumen de responsabilidades

| Componente             | Responsabilidad                                               |
| ---------------------- | ------------------------------------------------------------- |
| **Prospector Engine**  | Extracción, enriquecimiento, normalización y deduplicación    |
| **Prospector Service** | API, DTOs, validación y orquestación del Engine               |
| **SaaS Backend**       | Lógica de negocio, tenants, usuarios, campañas y persistencia |
| **Flutter**            | Interfaz de usuario                                           |
| **Google Maps**        | Fuente primaria de prospectos                                 |
| **Websites**           | Fuente secundaria de enriquecimiento                          |

---

# 46. Resumen del alcance v1.0.0

```text
┌─────────────────────────────────────────┐
│        PROSPECTOR ENGINE v1.0.0         │
├─────────────────────────────────────────┤
│                                         │
│ Google Maps Extraction          ✓       │
│ Result Loading / Scrolling      ✓       │
│ Business Extraction             ✓       │
│ Detail Enrichment               ✓       │
│ Website Enrichment              ✓       │
│ Normalization                   ✓       │
│ Deduplication                   ✓       │
│ Error Handling                  ✓       │
│ Logging                         ✓       │
│ Resource Lifecycle              ✓       │
│ CLI Independence                ✓       │
│ Deterministic Processing        ✓       │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│ FastAPI                         ✗       │
│ HTTP API                        ✗       │
│ Tenants                         ✗       │
│ Users                           ✗       │
│ Campaigns                       ✗       │
│ Authentication                  ✗       │
│ Authorization                   ✗       │
│ Persistence                     ✗       │
│ Flutter Integration             ✗       │
│ NestJS Integration              ✗       │
│ Distributed Engine              ✗       │
│ Multiple Sources                ✗       │
│ Advanced Fuzzy Matching         ✗       │
│                                         │
└─────────────────────────────────────────┘
```

---

# 47. Conclusión

Prospector Engine v1.0.0 representa la evolución del motor de extracción originalmente desarrollado dentro de Prospector CLI.

La versión conserva el pipeline funcional existente:

```text
Search
  ↓
Google Maps
  ↓
Business Extraction
  ↓
Detail Enrichment
  ↓
Website Enrichment
  ↓
Normalization
  ↓
Deduplication
  ↓
Business[]
```

La principal finalidad de esta versión es **estabilizar y reutilizar la capacidad de prospección sin introducir responsabilidades pertenecientes a la plataforma**.

La arquitectura resultante establece una separación clara:

```text
SaaS Backend
     │
     │ HTTP
     ▼
Prospector Service
     │
     │ internal module
     ▼
Prospector Engine
     │
     ├── Google Maps
     └── Websites
```

El Engine se mantiene como una capacidad técnica especializada.

Prospector Service será posteriormente la frontera de comunicación con la plataforma, mientras que el SaaS Backend conservará las reglas de negocio, administración de tenants, campañas, usuarios y persistencia.

La prioridad de `v1.0.0` es entregar un motor:

```text
Simple
   +
Funcional
   +
Determinista
   +
Reutilizable
   +
Mantenible
```

sin convertirlo prematuramente en una solución sobrearquitecturada.
