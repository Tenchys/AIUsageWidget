# AI Usage Widget

Monitorea el uso de créditos de **OpenCode Go** y **ChatGPT Plus** directamente desde la terminal.

Obtiene datos de la base de datos local de OpenCode y sincroniza con la web de opencode.ai para mostrar ventanas de uso (5 horas, semanal, mensual) y costos estimados por modelo.

---

## Requisitos

- **Python** >= 3.10
- **(Opcional)** Navegador compatible con `browser-cookie3` (Chrome, Firefox, Brave, Edge, Chromium, Safari) para detección automática de cookies de opencode.ai
- **(Opcional)** Sesión iniciada en [Codex](https://codex.so) para obtener datos de ChatGPT Plus (`~/.codex/auth.json`)

---

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Tenchys/AIUsageWidget.git
cd AIUsageWidget

# Instalación básica
pip install .

# Con soporte de scraping de cookies
pip install ".[scraper]"

# Con herramientas de desarrollo y testing
pip install ".[test]"
```

---

## Uso

```
ai-usage            Ver el estado de uso de OpenCode Go y ChatGPT Plus
ai-usage status     Igual que sin argumentos
ai-usage models     Ver desglose por modelo de OpenCode Go
ai-usage setup      Sincronizar cookies con la web de opencode.ai
ai-usage reset      Volver a modo local (sin sincronización web)
```

### Sincronización web

```bash
ai-usage setup
```

Esto intentará detectar cookies automáticamente desde tu navegador. Si no lo logra, te pedirá que las pegues manualmente desde la consola de desarrollador de opencode.ai.

### Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `XDG_CONFIG_HOME` | Directorio de configuración (default: `~/.config`) |
| `XDG_DATA_HOME` | Directorio de datos (default: `~/.local/share`) |
| `OPENCODE_DB` | Ruta a la base de datos SQLite de OpenCode |

---

## Desarrollo

```bash
pip install ".[test]"
ruff check .
ruff format .
pytest --cov
```

---

## Cambios Futuros

### Interfaz TUI

### Soporte para más providers

### Dashboard web

---

*Parte de [Tenchys/AIUsageWidget](https://github.com/Tenchys/AIUsageWidget)*
