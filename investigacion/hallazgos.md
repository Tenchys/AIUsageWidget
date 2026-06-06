# Investigacion - AI Usage Widget

## 1. OpenCode Go

### Suscripcion y limites

| Concepto | Valor |
|----------|-------|
| Costo suscripcion | $5 primer mes, luego **$10/mes** |
| Limite 5 horas | **$12** de uso |
| Limite semanal | **$30** de uso |
| Limite mensual | **$60** de uso |
| Consola de uso | https://opencode.ai/auth |
| API publica de uso | **No existe** |

### Modelos y precios (por 1M tokens)

| Modelo | Input | Output | Cached Read | Cached Write |
|--------|-------|--------|-------------|--------------|
| GLM-5.1 | $1.40 | $4.40 | $0.26 | — |
| GLM-5 | $1.00 | $3.20 | $0.20 | — |
| Kimi K2.6 | $0.95 | $4.00 | $0.16 | — |
| Kimi K2.5 | $0.60 | $3.00 | $0.10 | — |
| MiMo V2.5 | $0.14 | $0.28 | $0.0028 | — |
| MiMo V2.5 Pro | $1.74 | $3.48 | $0.0145 | — |
| MiniMax M3 | $0.60 | $2.40 | $0.12 | $0.75 |
| MiniMax M2.7 | $0.30 | $1.20 | $0.06 | $0.375 |
| MiniMax M2.5 | $0.30 | $1.20 | $0.06 | $0.375 |
| Qwen3.7 Max | $2.50 | $7.50 | $0.50 | $3.125 |
| Qwen3.7 Plus | $0.40 | $1.60 | $0.04 | $0.50 |
| Qwen3.6 Plus | $0.50 | $3.00 | $0.05 | $0.625 |
| DeepSeek V4 Pro | $1.74 | $3.48 | $0.0145 | — |
| DeepSeek V4 Flash | $0.14 | $0.28 | $0.0028 | — |

### API Endpoints (para chat, no para uso)

- OpenAI-compatible: `POST https://opencode.ai/zen/go/v1/chat/completions`
- Anthropic-compatible: `POST https://opencode.ai/zen/go/v1/messages`
- List models: `GET https://opencode.ai/zen/go/v1/models`
- Auth header: `Authorization: Bearer <api-key>`

---

## 2. OpenAI / Codex

### Autenticacion

- **Admin API Key** requerida para endpoints de uso (NO la key normal)
- Se crea en: https://platform.openai.com/settings/organization/admin-keys
- Header: `Authorization: Bearer $OPENAI_ADMIN_KEY`

### Endpoints de uso (Admin API)

Base path: `https://api.openai.com/v1/organization/`

| Endpoint | Descripcion |
|----------|-------------|
| `/costs` | Costos por dia |
| `/usage/completions` | Uso de chat completions |
| `/usage/embeddings` | Uso de embeddings |
| `/usage/images` | Uso de imagenes |
| `/usage/audio_speeches` | Uso de audio (speech) |
| `/usage/audio_transcriptions` | Uso de audio (transcripcion) |

**Parametros:**
- `start_time`, `end_time` (unix seconds)
- `bucket_width`: `1m` (1 minuto), `1h` (1 hora), `1d` (1 dia)
- `group_by`: `project_id`, `user_id`, `api_key_id`, `model`
- Limites de buckets: 1m→max 1440, 1h→max 168, 1d→max 31

### Rate limit headers (en cada respuesta de API normal)

| Header | Ejemplo |
|--------|---------|
| `x-ratelimit-limit-requests` | 60 |
| `x-ratelimit-remaining-requests` | 59 |
| `x-ratelimit-reset-requests` | 1s |
| `x-ratelimit-limit-tokens` | 150000 |
| `x-ratelimit-remaining-tokens` | 149984 |
| `x-ratelimit-reset-tokens` | 6m0s |

### Modelos y precios (por 1M tokens)

**Modelos principales:**
| Modelo | Input | Cached Input | Output |
|--------|-------|-------------|--------|
| gpt-5.5 | $5.00 | $0.50 | $30.00 |
| gpt-5.5-pro | $30.00 | — | $180.00 |
| gpt-5.4 | $2.50 | $0.25 | $15.00 |
| gpt-5.4-mini | $0.75 | $0.075 | $4.50 |
| gpt-5.4-nano | $0.20 | $0.02 | $1.25 |

**Modelos legacy (aun disponibles):**
| Modelo | Input | Cached Input | Output |
|--------|-------|-------------|--------|
| gpt-4o | $2.50 | $1.25 | $10.00 |
| gpt-4o-mini | $0.15 | $0.075 | $0.60 |
| gpt-4.1 | $2.00 | $0.50 | $8.00 |
| gpt-4.1-mini | $0.40 | $0.10 | $1.60 |
| gpt-4.1-nano | $0.10 | $0.025 | $0.40 |
| o3 | $2.00 | $0.50 | $8.00 |
| o3-mini | $1.10 | $0.55 | $4.40 |
| o4-mini | $1.10 | $0.275 | $4.40 |
| o1 | $15.00 | $7.50 | $60.00 |

**Codex y especializados:**
| Modelo | Input | Cached Input | Output |
|--------|-------|-------------|--------|
| **gpt-5.3-codex** | $1.75 | $0.175 | $14.00 |
| chat-latest | $5.00 | $0.50 | $30.00 |
| computer-use-preview | $1.50 | — | $6.00 |

### Tiers de uso (limites de gasto mensual)

| Tier | Requisito | Limite mensual |
|------|-----------|---------------|
| Free | Geografia permitida | $100 |
| Tier 1 | $5 pagado | $100 |
| Tier 2 | $50 pagado | $500 |
| Tier 3 | $100 pagado | $1,000 |
| Tier 4 | $250 pagado | $5,000 |
| Tier 5 | $1,000 pagado | $200,000 |

---

## 3. Captura de datos - Opencode CLI

### Base de datos local

- **Ubicacion**: `~/.local/share/opencode/opencode.db` (SQLite)
- **Tabla `session`** con columnas relevantes:
  - `tokens_input` INTEGER
  - `tokens_output` INTEGER
  - `tokens_reasoning` INTEGER
  - `tokens_cache_read` INTEGER
  - `tokens_cache_write` INTEGER
  - `cost` REAL
  - `updated_at` TEXT
  - `model` TEXT

### Comandos nativos utiles

| Comando | Funcion |
|---------|---------|
| `opencode stats` | Dashboard de uso (sesiones, tokens, costo) |
| `opencode export <id>` | Exporta sesion como JSON con tokens por mensaje |
| `opencode db "SELECT ..."` | Consultas SQL directas a la DB |
| `opencode db path` | Devuelve ruta de la DB |
| `opencode --print-logs` | Imprime logs con info de tokens a stderr |

### Formato de export JSON

```json
{
  "cost": 0.049216944,
  "tokens": {
    "input": 17628,
    "output": 2479,
    "reasoning": 2429,
    "cache": { "read": 100992, "write": 0 }
  },
  "messages": [
    {
      "cost": 0.0143463,
      "tokens": {
        "total": 8122,
        "input": 7999,
        "output": 69,
        "reasoning": 54,
        "cache": { "write": 0, "read": 0 }
      }
    }
  ]
}
```

### Estrategia de captura

**OpenCode Go**: Lectura directa del SQLite local (`opencode.db`). Se consultan sesiones dentro de cada ventana de tiempo (5h, 7d, 30d) y se suma el costo/tokens. No se necesita wrapper ni proxy.

**OpenAI Codex**: Uso de la Admin API (`/v1/organization/usage/*`) para obtener datos reales de uso con bucket_width `1h` o `1d` segun la ventana.

---

## 4. Arquitectura propuesta

```
ai-usage-widget/
├── pyproject.toml
├── ai_usage_widget/
│   ├── __init__.py
│   ├── main.py              # CLI (click/typer) - comandos status, config, etc.
│   ├── config.py            # API keys, configuracion
│   ├── storage.py           # Lectura de opencode.db + almacenamiento propio
│   ├── calculator.py        # Calculo de costos por token segun pricing
│   ├── windows.py           # Logica de ventanas de tiempo (5h/sem/mes)
│   ├── display.py           # Formateo de tablas y barras de progreso
│   ├── pricing/
│   │   ├── opencode_go.py   # Precios de los 14 modelos Go
│   │   └── openai.py        # Precios de modelos OpenAI/Codex
│   └── providers/
│       ├── __init__.py
│       ├── opencode.py      # Lee opencode.db y calcula uso Go
│       └── openai.py        # Consulta Admin API de OpenAI
```

### Comandos CLI

```
ai-usage status              # Uso actual en las 3 ventanas, $ restantes, reset
ai-usage config              # Configurar API keys y preferencias
ai-usage history             # Historial de sesiones con costo estimado
```

---

## 5. Discrepancias con la web

### Diferencias detectadas

La web de OpenCode muestra porcentajes diferentes al CLI local:

| Ventana | Web | CLI (Go-only, rolling) |
|---------|-----|----------------------|
| 5h | 16% | ~36-45% |
| Semanal | 26% | ~42% |
| Mensual | 83% | ~59% |

### Causas identificadas

1. **Sesiones con provider null (547 sesiones)**: Son sesiones antiguas sin metadata de provider. La web posiblemente las cuenta en la ventana mensual ($24.07 en 30d) pero NO en 5h/semanal (0 sesiones null en esas ventanas).

2. **Ventanas de tiempo diferentes**:
   - **CLI**: Ventanas moviles (rolling) de exactamente 5h/7d/30d
   - **Web**: Posiblemente bloques fijos anclados a la fecha de suscripcion. Los tiempos de reset de la web (5h: 2h43m, sem: 2d20h, mens: 3d19h) sugieren bloques fijos

3. **Timestamp source**: El campo `time_created` vs `time_updated` tiene diferencias minimas (<1h), insuficiente para explicar la discrepancia.

4. **Servidor vs Local**: La web usa datos del servidor (que pueden incluir ajustes post-procesamiento o sesiones de otras maquinas), mientras que el CLI lee la DB local.

### Conclusion

El CLI da una estimacion razonable pero NO puede igualar exactamente los numeros de la web sin acceso a la API del servidor. Las ventanas moviles del CLI tienden a sobreestimar el uso en ventanas cortas (5h/sem) y subestimarlo en la mensual, debido a que las sesiones null no se incluyen como Go.

