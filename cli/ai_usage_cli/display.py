# cli/ai_usage_cli/display.py

from core.ai_usage_widget.windows import get_reset_time_remaining


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
            percent = w.percent
            time_left = get_reset_time_remaining(w.reset_at)

            if isinstance(name, str):
                label = {
                    "5h": "5 horas",
                    "weekly": "Semanal",
                    "monthly": "Mensual",
                }.get(name, name)
            else:
                label = str(name)

            print(
                f"  {label:<10} ${used:<8.2f} / ${limit:<8.2f} "
                f"[{_bar(percent)}] {percent:5.1f}%  reset en {time_left}"
            )

        if source != "web":
            print()
            print(
                "  \033[90m(Ejecuta 'ai-usage setup' para sincronizar "
                "con la web)\033[0m"
            )

    print()
    _print_header("ChatGPT Plus")
    cg = data.get("chatgpt", {})
    if cg.get("error"):
        print(f"  \033[91m{cg['error']}\033[0m")
    else:
        plan_name = cg.get("plan_name", "")
        plan_cost = cg.get("plan_cost")
        cost_str = f"(${plan_cost}/mes)" if plan_cost is not None else "(costo N/A)"
        status_color = "\033[92m" if cg.get("allowed", True) else "\033[91m"
        status_text = "Activo" if cg.get("allowed", True) else "Limitado"
        print(f"  Plan: {plan_name} {cost_str}  {status_color}[{status_text}]\033[0m")
        for w in cg.get("windows", []):
            name = w["name"]
            percent = w["used_percent"]
            reset_after = w["reset_after_seconds"]
            label = {"5h": "5 horas", "weekly": "Semanal"}.get(name, name)
            time_left = _fmt_seconds(reset_after)
            print(
                f"  {label:<10} [{_bar(percent)}] {percent:5.1f}%  reset en {time_left}"
            )

        credits = cg.get("credits", {})
        if credits.get("has_credits"):
            approx_cloud = credits.get("approx_cloud")
            if approx_cloud and len(approx_cloud) == 2:
                print(f"  Mensajes cloud: {approx_cloud[0]} / {approx_cloud[1]}")
            if credits.get("balance") and credits["balance"] != "0":
                print(f"  Balance: ${credits['balance']}")

        if cg.get("limit_reached"):
            print("  \033[91mL\u00edmite alcanzado\033[0m")
    print()


def show_models(data: dict):
    _print_header("OpenCode Go - Modelos usados")
    oc = data.get("opencode_go", {})
    models = oc.get("models", {})
    if not models:
        print("  Sin datos")
        return

    print(
        f"  {'Modelo':<25} {'Sesiones':>8} {'In tokens':>12} "
        f"{'Out tokens':>12} {'Costo':>10}"
    )
    print(f"  {'-' * 25} {'-' * 8} {'-' * 12} {'-' * 12} {'-' * 10}")
    for model, stats in sorted(
        models.items(), key=lambda x: x[1]["cost"], reverse=True
    ):
        print(
            f"  {model:<25} {stats['sessions']:>8} "
            f"{stats['tokens_input']:>12,} {stats['tokens_output']:>12,} "
            f"${stats['cost']:>9.4f}"
        )
    print()


def _fmt_seconds(seconds: int) -> str:
    if seconds <= 0:
        return "ahora"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _print_header(title: str):
    print(f"\033[1;36m── {title} ──\033[0m")
