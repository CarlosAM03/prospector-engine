ARG PIP_VERSION=26.3

FROM python:3.11.14-slim-bookworm@sha256:65a93d69fa75478d554f4ad27c85c1e69fa184956261b4301ebaf6dbb0a3543d AS build
ARG PIP_VERSION
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /build
COPY requirements/constraints.txt requirements/constraints.txt
RUN python -m pip install --no-cache-dir --only-binary=:all: "pip==${PIP_VERSION}" \
    && python -m pip install --no-cache-dir -c requirements/constraints.txt build setuptools wheel
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m build --no-isolation --wheel

FROM python:3.11.14-slim-bookworm@sha256:65a93d69fa75478d554f4ad27c85c1e69fa184956261b4301ebaf6dbb0a3543d
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
COPY requirements/constraints.txt /opt/constraints.txt
RUN python -m pip install --no-cache-dir -c /opt/constraints.txt playwright beautifulsoup4 \
    && python -m playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/* /tmp/wheels \
    && useradd --create-home --uid 10001 engine \
    && chmod -R a+rX /opt/playwright
COPY --from=build /build/dist/*.whl /tmp/wheels/
ARG PIP_VERSION
RUN python -m pip install --no-cache-dir --only-binary=:all: "pip==${PIP_VERSION}" \
    && python -m pip install --no-cache-dir --no-deps /tmp/wheels/*.whl \
    && python -m pip uninstall --yes setuptools wheel \
    && python -m pip check \
    && rm -rf /tmp/wheels
USER 10001:10001
WORKDIR /home/engine
CMD ["python", "-m", "prospector_engine.diagnostics", "--browser"]
