# cli/ai_usage_cli/main.py

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.ai_usage_widget.providers import opencode, openai
from core.ai_usage_widget.config import get_openai_key, set_openai_key
from cli.ai_usage_cli.display import show_status, show_models


def cmd_status():
    data = {
        "opencode_go": opencode.get_usage(),
        "openai": openai.get_usage(get_openai_key()),
    }
    show_status(data)


def cmd_models():
    data = {
        "opencode_go": opencode.get_usage(),
        "openai": {},
    }
    show_models(data)


def cmd_setup():
    print("Configurando sincronizacion con OpenCode Go...")
    print()

    cookie_entries = _try_auto_cookies()
    if cookie_entries:
        print(f"  \033[92mCookies detectadas automaticamente ({len(cookie_entries)} cookies)\033[0m")
    else:
        print("  No se pudieron detectar cookies automaticamente.")
        print()
        print("  Para extraerlas manualmente:")
        print("    1. Abri https://opencode.ai/auth en tu navegador")
        print("    2. Asegurate de estar logueado")
        print("    3. Abri la consola (F12) y ejecuta: copy(document.cookie)")
        print("    4. Pega el resultado aqui:")
        print()
        raw = input("  > ").strip()
        if not raw:
            print("  \033[91mNo se ingresaron cookies. Cancelado.\033[0m")
            return
        cookies = {}
        for part in raw.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                cookies[k.strip()] = v.strip()

    from scraper.cookies import save_cookies, save_cookie_entries, cookies_to_header
    if cookie_entries:
        save_cookie_entries(cookie_entries)
        cookies = {item["name"]: str(item["value"]) for item in cookie_entries}
    else:
        save_cookies(cookies)

    print()
    print("  Verificando conexion con OpenCode Go...")

    from scraper.opencode_go import fetch_go_usage
    header = cookies_to_header(cookies)
    data = fetch_go_usage(header)

    if data:
        print(f"  \033[92mConexion exitosa!\033[0m")
        print(f"    5 horas:  {data.five_hour_pct}% (reset en {data.five_hour_reset_seconds}s)")
        print(f"    Semanal:  {data.weekly_pct}% (reset en {data.weekly_reset_seconds}s)")
        print(f"    Mensual:  {data.monthly_pct}% (reset en {data.monthly_reset_seconds}s)")
        import time
        from core.ai_usage_widget.config import set_subscription_start
        sub_start = time.time() + data.monthly_reset_seconds - 30 * 86400
        set_subscription_start(sub_start)
        print()
        print("  \033[92mListo! Ahora 'ai-usage' mostrara datos de la web.\033[0m")
    else:
        print("  \033[91mNo se pudo obtener datos de la web.\033[0m")
        print("  Verifica que las cookies sean validas y que estes logueado en opencode.ai")


def _try_auto_cookies() -> list[dict[str, str | int | None]] | None:
    try:
        from scraper.cookies import _load_from_browser
        return _load_from_browser()
    except Exception:
        return None


def cmd_reset():
    from scraper.cookies import clear_cookies
    from core.ai_usage_widget.config import set_subscription_start
    clear_cookies()
    set_subscription_start(0)
    print("Cookies y calibracion eliminadas. Volviendo a modo local.")


def cmd_config(args: list[str]):
    if not args:
        print("Uso: ai-usage config --openai-admin-key KEY")
        return
    if args[0] == "--openai-admin-key":
        if len(args) < 2:
            print("Debes proporcionar la key")
            return
        set_openai_key(args[1])
        print("OpenAI Admin Key guardada en ~/.config/ai-usage/config.json")
    else:
        print(f"Opcion desconocida: {args[0]}")


def main():
    args = sys.argv[1:]

    if not args:
        cmd_status()
    elif args[0] == "status":
        cmd_status()
    elif args[0] == "models":
        cmd_models()
    elif args[0] == "setup":
        cmd_setup()
    elif args[0] == "reset":
        cmd_reset()
    elif args[0] == "config":
        cmd_config(args[1:])
    elif args[0] in ("-h", "--help"):
        print("AI Usage Widget")
        print()
        print("  ai-usage               Muestra el estado de uso actual")
        print("  ai-usage status        Igual que sin argumentos")
        print("  ai-usage models        Desglose por modelo")
        print("  ai-usage setup         Sincronizar con la web de OpenCode Go")
        print("  ai-usage reset         Volver a modo local (sin web)")
        print("  ai-usage config --openai-admin-key KEY   Configurar key de OpenAI")
    else:
        print(f"Comando desconocido: {args[0]}")
        print("Usa ai-usage --help para ayuda")


if __name__ == "__main__":
    main()
