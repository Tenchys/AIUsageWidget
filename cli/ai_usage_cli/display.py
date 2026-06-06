# cli/ai_usage_cli/display.py

import sys
from core.ai_usage_widget.windows import WindowStatus, get_reset_time_remaining


def _bar(percent: float, width: int = 20) -> str:
    filled = int(percent / 100 * width)
    empty = width - filled
    blocks = "█" * filled + "░" * empty
    if percent >= 90:
        color = "\033[91m"
    elif percent >= 70:
        color = "\033[93m"
    else:
        color = "\033[92m"
    reset = "\033[0m"
    return f"{color}{blocks}{reset}"


def show_status(data: dict):
    _print_header("OpenCode Go")
    oc = data.get("opencode_go", {})
    if oc.get("error"):
        print(f"  \033[91m{oc['error']}\033[0m")
    else:
        source = oc.get("source", "local")
        tag = "\033[92m[web]\033[0m" if source == "web" else "\033[90m[local]\033[0m"
        print(f"  Fuente: {tag}")
        print(f"  Sesiones registradas: {oc.get('total_sessions', 0)}")
        print(f"  Costo total estimado: \033[93m${oc.get('total_cost', 0):,.4f}\033[0m")
        cookie_expiry = oc.get("cookie_expiry")
        if cookie_expiry:
            print(f"  Cookie expira: \033[90m{cookie_expiry}\033[0m")
        print()
        for w in oc.get("windows", []):
            name = w.name
            limit = w.limit
            used = w.used
            remaining = w.remaining
            percent = w.percent
            time_left = get_reset_time_remaining(w.reset_at)

            if isinstance(name, str):
                label = {"5h": "5 horas", "weekly": "Semanal", "monthly": "Mensual"}.get(name, name)
            else:
                label = str(name)

            print(f"  {label:<10} ${used:<8.2f} / ${limit:<8.2f} [{_bar(percent)}] {percent:5.1f}%  reset en {time_left}")

        if source != "web":
            print()
            print(f"  \033[90m(Ejecuta 'ai-usage setup' para sincronizar con la web)\033[0m")

    print()
    _print_header("OpenAI Codex")
    oa = data.get("openai", {})
    if oa.get("error"):
        print(f"  \033[91m{oa['error']}\033[0m")
    else:
        print(f"  Costo hoy:     ${oa.get('cost_today', 0):,.4f}")
        print(f"  Costo semana:  ${oa.get('cost_week', 0):,.4f}")
        print(f"  Costo mes:     ${oa.get('cost_month', 0):,.4f}")
    print()


def show_models(data: dict):
    _print_header("OpenCode Go - Modelos usados")
    oc = data.get("opencode_go", {})
    models = oc.get("models", {})
    if not models:
        print("  Sin datos")
        return

    print(f"  {'Modelo':<25} {'Sesiones':>8} {'In tokens':>12} {'Out tokens':>12} {'Costo':>10}")
    print(f"  {'-'*25} {'-'*8} {'-'*12} {'-'*12} {'-'*10}")
    for model, stats in sorted(models.items(), key=lambda x: x[1]["cost"], reverse=True):
        print(f"  {model:<25} {stats['sessions']:>8} {stats['tokens_input']:>12,} {stats['tokens_output']:>12,} ${stats['cost']:>9.4f}")
    print()


def _print_header(title: str):
    print(f"\033[1;36m── {title} ──\033[0m")
