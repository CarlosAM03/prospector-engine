# Hardening de dependencias del Engine

Revisión del 23 de noviembre de 2026. Los reportes automatizados del propietario
figuran como **NO_PROVIDED**. No se encontró `SECURITY_INPUT/` en el checkout.

## Inventario

| Alcance | Resolución del candidato |
|---|---|
| Runtime directo | Playwright 1.61.0, BeautifulSoup4 4.15.0 |
| Runtime transitivo | greenlet 3.5.6, pyee 13.0.1, Soup Sieve 3.0.3, typing-extensions 4.16.0 |
| Build | setuptools 84.2.1 y wheel 0.48.0 en `pyproject.toml` y `requirements/constraints.txt` |
| Dev y tooling | pytest 9.1.1, build 1.2.2.post1, Ruff 0.11.13, packaging 26.3, pyproject-hooks 1.3.3, colorama 0.4.6 (Windows), iniconfig 2.3.1, pluggy 1.7.0, Pygments 2.21.0 |
| Browser | Chromium administrado revisión 1228, versión 149.0.7827.55 según Playwright. Edge Stable es externo al wheel y al Dockerfile. |
| Contenedor | Python 3.11.18 en Debian slim-bookworm, digest `sha256:a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39`. Playwright instala los paquetes de SO requeridos por Chromium. La imagen fija pip 26.3 y retira setuptools y wheel en la etapa final después de instalar el paquete. |
| CI | Refs de major `actions/checkout@v4`, `actions/setup-python@v5` y `actions/upload-artifact@v4`. |

## Avisos verificados

| Aviso | Rango y alcance | Tratamiento |
|---|---|---|
| [CVE-2026-24049, GHSA-8rrh-rw8j-w5fx](https://github.com/pypa/wheel/security/advisories/GHSA-8rrh-rw8j-w5fx), alto | wheel hasta 0.46.1, corregido en 0.46.2. La ruta afectada es `wheel unpack` con un wheel no confiable. El flujo del Engine construye con `build` e instala con `pip`. | El pin 0.45.1 estaba dentro del rango. Se seleccionó 0.48.0, versión corregida disponible para validación. |
| [CVE-2026-59890, GHSA-h35f-9h28-mq5c](https://github.com/pypa/setuptools/security/advisories/GHSA-h35f-9h28-mq5c), moderado | setuptools anterior a 83.0.0. Afecta exclusiones de `MANIFEST.in` al empaquetar en sistemas macOS con las condiciones descritas por PyPA. | Se actualizó de 80.9.0 a 84.2.1. Los gates del candidato cubren Windows y Linux. |
| [GHSA-xmj3-9gf7-h52w](https://github.com/pypa/setuptools/security/advisories/GHSA-xmj3-9gf7-h52w), bajo | setuptools desde 38.2.2 hasta antes de 84.1.0. Requiere instalación legacy de un wheel en Windows. No se identificó uso de esa ruta en el Engine. | Se seleccionó 84.2.1, que cubre ambos avisos y declara Python ≥3.10. |
| [CVE-2025-47273, GHSA-5rjg-fvgr-3xxf](https://github.com/pypa/setuptools/security/advisories/GHSA-5rjg-fvgr-3xxf), moderado | setuptools anterior a 78.1.1. | El pin 80.9.0 ya incluía la corrección. |
| [Avisos de pip en PyPI](https://pypi.org/pypi/pip/25.1.1/json), entre ellos [CVE-2026-13346](https://github.com/pypa/pip/security/advisories/GHSA-qwm4-qh6w-59xr) | La primera imagen incluyó pip 24.0, setuptools 79.0.1 y wheel 0.45.1 heredados de la base. El entorno de pruebas Windows se creó con pip 25.1.1 de `ensurepip`. Los avisos de pip incluyen vulnerabilidades de instalación o manejo de archivos fuera del código del Engine. | Docker fija [pip 26.3](https://pypi.org/project/pip/26.3/) en ambas etapas y elimina setuptools/wheel de la imagen final. El bootstrap de los entornos de desarrollo sigue dependiendo de las herramientas del host. |
| [CVE-2026-126190, GHSA-mmhr-3c5m-f64f](https://github.com/advisories/GHSA-mmhr-3c5m-f64f), alto | Soup Sieve anterior a 4.0.0, instalado indirectamente por BeautifulSoup4. El aviso afecta la evaluación de selectores CSS descendientes. El parser del Engine sólo llama a `find()` / `find_all()` y los selectores de browser se evalúan en Playwright. | La versión coincide con el rango. No se encontró una ruta de ejecución del selector afectado. Se conserva el pin y se registra la evaluación de aplicabilidad, sin excluir el aviso del escaneo. |
| [Chromium en Playwright 1.61.0](https://github.com/microsoft/playwright/releases/tag/v1.61.0) y [actualización de seguridad Chrome 149](https://chromereleases.googleblog.com/2026/06/stable-channel-update-for-desktop_0153744567.html) | El Chromium empaquetado es anterior a la actualización de 149.0.7827.102/.103 que Google publicó con correcciones. La versión de Chrome desktop por sí sola no acredita aplicabilidad individual al binario headless de Playwright. El Engine navega HTML de terceros. | Gate abierto. Evaluar un browser con parches posteriores y volver a probar navegación, selectores, lifecycle y cancelación con el perfil de despliegue que apruebe el propietario. |
| [Actualización de seguridad Node.js 24.22.3](https://nodejs.org/en/blog/release/v24.22.3) | Docker Scout detectó Node.js 24.17.0 bajo el driver de Playwright. El proveedor confirma correcciones posteriores de TLS, HTTP y HTTP/2. El Engine ejecuta el driver local y no inicia servicios Node.js públicos. | Evaluar alcance por aviso y una versión de Playwright cuyo driver incluya los parches junto con la revisión de Chromium. |
| [Correcciones de CPython 3.11.15](https://www.python.org/downloads/release/python-31115/) y [versión 3.11.18](https://www.python.org/downloads/release/python-31118/) | La base anterior 3.11.14 precede correcciones del parser HTML de la biblioteca estándar. El enriquecimiento usa el parser `html.parser` de BeautifulSoup sobre contenido externo. | Base oficial 3.11.18 fijada por digest para build y runtime. |

## Evidencia Python

`pip check` respaldó la resolución del entorno Windows. `pip-audit 2.10.0` se
ejecutó en su propia venv contra los 17 pins de constraints con
`-r requirements/constraints.txt --no-deps --disable-pip`. El primer intento
contra el baseline sufrió un cierre de conexión. La repetición enumeró cinco
entradas en tres paquetes, incluida una duplicación por alias. El candidato
reportó sólo CVE-2026-126190 en Soup Sieve. Los reportes JSON, la consulta
complementaria de PyPI y el SBOM CycloneDX están en
`artifacts/engine-v1-candidate/`. El escaneo de constraints excluye el pip
inyectado por `ensurepip` en Windows, evaluado mediante la consulta PyPI.

Docker Scout también atribuyó avisos de setuptools 70.3.0 al SBOM de pip 26.3.
La inspección de esa instalación encontró `pkg_resources` vendorizado y ninguna
distribución independiente de setuptools en la imagen. Los avisos listados se
refieren a rutas de `PackageIndex`, a `sdist` o a instalación legacy de setuptools.
El registro del scanner se conserva con esa distinción. [Política de dependencias vendorizadas de pip](https://github.com/pypa/pip/security).

El inventario de la imagen final registró pip 26.3 y packaging 26.3 como
herramientas de base, además de las dependencias de runtime. `pip check` pasó
después de retirar setuptools y wheel como distribuciones independientes.
El listado `dpkg-query -W` contiene 209 paquetes. Está disponible junto al
inventario Python en `artifacts/v1-docker/`. Para OpenSSL, `libssl3` y `openssl`
pasaron de 3.0.18-1~deb12u2 a 3.0.22-1~deb12u2, que Debian registra como
corregida para CVE-2026-34182. [Debian Security Tracker](https://security-tracker.debian.org/tracker/CVE-2026-34182).

## Escaneo de imagen

Docker Scout 1.27.0 completó `docker scout cves --format sarif` para tres
imágenes locales. La tabla cuenta asociaciones reportadas por scanner.

| Imagen | Debian | Driver Node.js | PyPI | Total | Críticas | Altas |
|---|---:|---:|---:|---:|---:|---:|
| `f7ccdc0` con herramientas heredadas | 275 | 36 | 11 | 322 | 8 | 77 |
| `1dde01b` con herramientas corregidas | 275 | 36 | 4 | 315 | 8 | 76 |
| `307df17` con base Python 3.11.18 | 197 | 36 | 4 | 237 | 0 | 38 |

El SARIF y el resumen `scout-summary.json` están en `artifacts/v1-docker/`.
Las cuatro entradas PyPI de la imagen final corresponden a Soup Sieve y al
SBOM vendorizado de pip, descritos arriba. Los resultados de Debian y Node.js
restantes son señales del scanner pendientes de evaluación por componente,
versión y ruta de ejecución. La cobertura de Scout no sustituye la revisión
del Chromium descargado por Playwright. El gate de seguridad para promover
una release continúa abierto.

## Revisión de aplicabilidad del 24 de noviembre de 2026

| Componente en la imagen analizada | Evidencia y alcance | Mitigación y decisión pendiente |
|---|---|---|
| Chromium 149.0.7827.55 | Navega contenido de terceros y antecede a correcciones de Chrome 149. La equivalencia aviso por aviso con Headless Shell requiere revisar la revisión de Chromium. | UID 10001, `cap-drop=ALL` y `no-new-privileges` se probaron en Docker. El Engine no habilita explícitamente el sandbox de Chromium. Aprobar un perfil de navegador con parches y validar su aislamiento antes de producción. |
| Node.js 24.17.0 en el driver | El proveedor confirma que la línea 24.x está afectada por [CVE-2026-123863](https://nodejs.org/en/blog/vulnerability/november-2026-security-releases/), ligado a servidores HTTP/2. El Engine usa el driver local de Playwright y no abre un servidor Node HTTP/2 por contrato. La revisión de otras rutas del driver sigue abierta. | Revisar cliente TLS, proxies y la versión de Node incluida en la actualización de Playwright. |
| Kerberos `1.20.1-2+deb12u5` | Debian confirma avisos abiertos en Bookworm, entre ellos [CVE-2026-119079](https://security-tracker.debian.org/tracker/CVE-2026-119079). La imagen analizada instala bibliotecas cliente y el diagnóstico no configura un KDC ni un servidor de administración. | Mantener el aviso abierto y verificar rutas cliente que puedan invocarse con el perfil productivo. |
| Xorg/Xvfb `2:21.1.7-3+deb12u13` | [Debian registra CVE-2026-109904 y CVE-2026-109903 como abiertos](https://security-tracker.debian.org/tracker/source-package/xorg-server) en Bookworm. La prueba controlada usa Chromium headless y no arranca Xvfb. | Verificar si el despliegue necesita Xvfb. Separar esa evaluación de la validación headless. |
| glibc `2.36-9+deb12u14` y otros paquetes Debian | [Debian registra avisos abiertos para glibc en Bookworm](https://security-tracker.debian.org/tracker/source-package/glibc). Requieren correlación con las funciones habilitadas por el runtime. | Conservar los hallazgos del scanner y revisar disponibilidad de parches y alcance por componente. |

El análisis del riesgo residual sigue abierto. No se concedieron excepciones
ni se configuró una lista de avisos ignorados. La evidencia automatizada del
propietario continúa NO_PROVIDED.
