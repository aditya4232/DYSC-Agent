import json
import os
import sys
import time
import uuid

from dysc_runtime.chat_store import ChatStore
from dysc_runtime.health import run_health_checks
from dysc_runtime.providers import (
    add_provider,
    list_providers,
    provider_key_status,
    set_primary_provider,
    set_provider_key_env,
)
from dysc_runtime.skills import disable_skill, enable_skill, install_local_skill, list_skills
from dysc_runtime.state import ensure_bootstrap
from dysc_runtime.workspace import ensure_workspace_default_to_cwd, set_workspace, show_workspace
from dysc_runtime.llm import chat_completion
from dysc_runtime.tools import get_available_tools, execute_tool
from dysc_runtime.security import run_security_review, suggest_human_fix
from dysc_runtime.context_runtime import get_runtime_context
from dysc_runtime.settings import list_settings, set_setting


DYSC_LOGO = [
    "          @@@          ",
    "      @@@@@@@@@@@      ",
    "    @@@@@@ @@@@@@      ",
    "   @@@@@   *   @@@@@   ",
    "    @@@@@@ @@@@@@      ",
    "      @@@@@@@@@@@      ",
    "          @@@          ",
    "       DYSC AGENT      ",
]


def render_logo():
    for line in DYSC_LOGO:
        print(line)


def animate_boot():
    if not sys.stdout.isatty():
        return

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    message = "Booting DYSC AGENT"
    try:
        for index in range(18):
            frame = frames[index % len(frames)]
            print(f"\r{frame} {message}", end="", flush=True)
            time.sleep(0.06)
        print("\r✅ DYSC AGENT online      ")
    except UnicodeEncodeError:
        fallback = ["-", "\\", "|", "/"]
        for index in range(12):
            frame = fallback[index % len(fallback)]
            print(f"\r{frame} {message}", end="", flush=True)
            time.sleep(0.06)
        print("\r[OK] DYSC AGENT online      ")


def emit(payload, exit_code=0):
    print(json.dumps(payload, indent=2))
    raise SystemExit(exit_code)


def handle_init(_):
    result = ensure_bootstrap()
    ensure_workspace_default_to_cwd(force=False)
    emit({"ok": True, "message": "DYSC initialized", "paths": result})


def handle_provider_list(_):
    ensure_bootstrap()
    emit({"ok": True, "providers": list_providers()})


def handle_provider_add(args):
    if len(args) < 5:
        emit({"ok": False, "error": "provider-add requires 5 arguments"}, 1)
    ensure_bootstrap()
    provider_id, provider_type, base_url, api_key_env, enabled_raw = args[:5]
    enabled = enabled_raw.lower() == "true"
    provider = add_provider(provider_id, provider_type, base_url, api_key_env, enabled)
    emit({"ok": True, "provider": provider})


def handle_provider_set_primary(args):
    if not args:
        emit({"ok": False, "error": "provider-set-primary requires provider id"}, 1)
    ensure_bootstrap()
    set_primary_provider(args[0])
    emit({"ok": True, "primary": args[0]})


def handle_provider_set_key_env(args):
    if len(args) < 2:
        emit({"ok": False, "error": "provider-set-key-env requires provider id and env var name"}, 1)
    ensure_bootstrap()
    provider = set_provider_key_env(args[0], args[1])
    emit(
        {
            "ok": True,
            "provider": provider["id"],
            "api_key_env": provider["api_key_env"],
            "note": "Store key securely in OS env var; DYSC never stores key plaintext.",
        }
    )


def handle_provider_key_status(args):
    if not args:
        emit({"ok": False, "error": "provider-key-status requires provider id"}, 1)
    ensure_bootstrap()
    emit({"ok": True, "status": provider_key_status(args[0])})


def handle_workspace_show(_):
    ensure_bootstrap()
    ensure_workspace_default_to_cwd(force=False)
    emit({"ok": True, "workspace": show_workspace()})


def handle_workspace_set(args):
    if not args:
        emit({"ok": False, "error": "workspace-set requires path"}, 1)
    ensure_bootstrap()
    selected = set_workspace(args[0])
    emit({"ok": True, "workspace": selected})


def handle_workspace_open(args):
    handle_workspace_set(args)


def handle_workspace_use_current(_):
    ensure_bootstrap()
    selected = ensure_workspace_default_to_cwd(force=True)
    emit({"ok": True, "workspace": selected})


def handle_skills_list(_):
    ensure_bootstrap()
    emit({"ok": True, "skills": list_skills()})


def handle_skills_enable(args):
    if not args:
        emit({"ok": False, "error": "skills-enable requires skill id"}, 1)
    ensure_bootstrap()
    emit({"ok": True, "enabled": enable_skill(args[0])})


def handle_skills_disable(args):
    if not args:
        emit({"ok": False, "error": "skills-disable requires skill id"}, 1)
    ensure_bootstrap()
    emit({"ok": True, "enabled": disable_skill(args[0])})


def handle_skills_install_local(args):
    if len(args) < 2:
        emit({"ok": False, "error": "skills-install-local requires skill id and json path"}, 1)
    ensure_bootstrap()
    skill = install_local_skill(args[0], args[1])
    emit({"ok": True, "installed": skill})


def handle_health(_):
    ensure_bootstrap()
    health = run_health_checks()
    exit_code = 0 if health["status"] == "green" else 1
    emit({"ok": health["status"] == "green", "health": health}, exit_code)


def handle_start(args):
    ensure_bootstrap()
    health = run_health_checks()
    if health["status"] != "green":
        emit({"ok": False, "message": "DYSC failed readiness", "health": health}, 1)

    render_logo()
    animate_boot()
    try:
        print("🟢 DYSC READY")
    except UnicodeEncodeError:
        print("[GREEN] DYSC READY")

    if "--once" in args:
        emit(
            {
                "ok": True,
                "message": "DYSC runtime ready (once mode)",
                "provider": health["active_provider"],
                "workspace": health["workspace"],
                "skills": health["enabled_skills"],
            }
        )

    session_id = str(uuid.uuid4())
    store = ChatStore()

    print(f"Session ID: {session_id}")
    print("Type 'exit' or 'quit' to stop.")
    print("Slash commands: /help /health /review [limit] /context /settings /providers /workspace /skills /exit")
    print("-" * 40)

    try:
        while True:
            try:
                user_input = input("\n> ")
            except EOFError:
                break
                
            if not user_input.strip():
                continue
                
            if user_input.strip().lower() in {"exit", "quit"}:
                break

            if user_input.strip().startswith("/"):
                slash = user_input.strip().split()
                command = slash[0].lower()

                if command == "/help":
                    print("Available: /help /health /review [limit] /context /settings /providers /workspace /skills /exit")
                    continue
                if command == "/exit":
                    break
                if command == "/health":
                    print(json.dumps(run_health_checks(), indent=2))
                    continue
                if command == "/context":
                    print(json.dumps(get_runtime_context(), indent=2))
                    continue
                if command == "/settings":
                    print(json.dumps(list_settings(), indent=2))
                    continue
                if command == "/providers":
                    print(json.dumps(list_providers(), indent=2))
                    continue
                if command == "/workspace":
                    print(json.dumps(show_workspace(), indent=2))
                    continue
                if command == "/skills":
                    print(json.dumps(list_skills(), indent=2))
                    continue
                if command == "/review":
                    limit = 150
                    if len(slash) > 1:
                        try:
                            limit = max(1, min(int(slash[1]), 1000))
                        except ValueError:
                            print("Invalid /review limit; using default 150")
                    print(json.dumps(run_security_review(limit=limit), indent=2))
                    continue

                print(f"Unknown slash command: {command}. Try /help")
                continue

            store.save_message(session_id, "user", user_input)

            history = store.list_session(session_id)
            messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

            system_prompt = {
                "role": "system",
                "content": "You are DYSC, a Claude-Code-style coding agent focused on security reviews, robust AI fix plans, and tool-grounded responses. Use tools when needed, keep changes safe and production-grade.",
            }
            messages.insert(0, system_prompt)

            try:
                max_rounds = 4
                rounds = 0
                final_content = None

                while rounds < max_rounds:
                    rounds += 1
                    print("Thinking...")
                    response = chat_completion(messages, tools=get_available_tools())

                    if "choices" not in response or not response["choices"]:
                        raise RuntimeError(f"Unexpected response format: {response}")

                    message = response["choices"][0].get("message", {})
                    tool_calls = message.get("tool_calls") or []
                    content = message.get("content")

                    if content:
                        final_content = content

                    if not tool_calls:
                        break

                    messages.append(message)
                    for tool_call in tool_calls:
                        function_name = tool_call["function"]["name"]
                        arguments = json.loads(tool_call["function"].get("arguments", "{}"))
                        print(f"\n[Tool Call] {function_name}({arguments})")
                        result = execute_tool(function_name, arguments)
                        print(f"[Tool Result] {result}")
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": function_name,
                                "content": str(result),
                            }
                        )

                if final_content:
                    print(f"\nDYSC: {final_content}")
                    store.save_message(session_id, "assistant", final_content)
                else:
                    print("\nDYSC: No assistant text response generated.")
            except Exception as e:
                print(f"\nDYSC Error: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        store.close()
        emit({"ok": True, "message": "DYSC stopped"})


def handle_context_packages(_):
    ensure_bootstrap()
    emit(get_runtime_context())


def handle_review_security(args):
    ensure_bootstrap()
    limit = 150
    if args:
        try:
            limit = max(1, min(int(args[0]), 1000))
        except ValueError:
            emit({"ok": False, "error": "review-security limit must be an integer"}, 1)

    report = run_security_review(limit=limit)
    emit(report)


def handle_fix_suggest(args):
    if len(args) < 4:
        emit({"ok": False, "error": "fix-suggest requires file, line, rule, snippet"}, 1)
    ensure_bootstrap()

    file_path = args[0]
    try:
        line = int(args[1])
    except ValueError:
        emit({"ok": False, "error": "line must be integer"}, 1)
    rule = args[2]
    snippet = args[3]

    emit(suggest_human_fix(file_path, line, rule, snippet))


def handle_settings_show(_):
    ensure_bootstrap()
    emit({"ok": True, "settings": list_settings()})


def handle_settings_set(args):
    if len(args) < 2:
        emit({"ok": False, "error": "settings-set requires key and value"}, 1)
    ensure_bootstrap()
    settings = set_setting(args[0], args[1])
    emit({"ok": True, "settings": settings})


def handle_onboard(args):
    result = ensure_bootstrap()
    ensure_workspace_default_to_cwd(force=False)
    workspace = os.getcwd()
    if args:
        selected = set_workspace(args[0])
        workspace = selected.get("primary", workspace)

    health = run_health_checks()
    providers = list_providers()
    primary_provider = providers.get("primary")
    key_status = provider_key_status(primary_provider) if primary_provider else None

    emit(
        {
            "ok": True,
            "message": "DYSC onboarding ready",
            "paths": result,
            "workspace": workspace,
            "primary_provider": primary_provider,
            "api_key": key_status,
            "health": health,
            "next_steps": [
                "Set provider key env name: dysc provider set-key-env <providerId> <ENV_VAR>",
                "Set environment variable in your shell/OS (never commit keys)",
                "Validate key presence: dysc provider key-status <providerId>",
                "Start agent: dysc start",
            ],
        }
    )


def handle_chat_save(args):
    if len(args) < 3:
        emit({"ok": False, "error": "chat-save requires session, role, content"}, 1)
    ensure_bootstrap()
    session_id, role, content = args[0], args[1], args[2]
    store = ChatStore()
    row_id = store.save_message(session_id=session_id, role=role, content=content)
    emit({"ok": True, "saved": {"id": row_id, "session": session_id}})


def handle_chat_list(args):
    if not args:
        emit({"ok": False, "error": "chat-list requires session id"}, 1)
    ensure_bootstrap()
    store = ChatStore()
    messages = store.list_session(args[0])
    emit({"ok": True, "session": args[0], "messages": messages})


def main():
    args = sys.argv[1:]
    if not args:
        emit({"ok": False, "error": "No command provided"}, 1)

    command = args[0]
    command_args = args[1:]
    handlers = {
        "init": handle_init,
        "provider-list": handle_provider_list,
        "provider-add": handle_provider_add,
        "provider-set-primary": handle_provider_set_primary,
        "provider-set-key-env": handle_provider_set_key_env,
        "provider-key-status": handle_provider_key_status,
        "workspace-show": handle_workspace_show,
        "workspace-set": handle_workspace_set,
        "workspace-open": handle_workspace_open,
        "workspace-use-current": handle_workspace_use_current,
        "skills-list": handle_skills_list,
        "skills-enable": handle_skills_enable,
        "skills-disable": handle_skills_disable,
        "skills-install-local": handle_skills_install_local,
        "health": handle_health,
        "doctor": handle_health,
        "start": handle_start,
        "chat-save": handle_chat_save,
        "chat-list": handle_chat_list,
        "context-packages": handle_context_packages,
        "review-security": handle_review_security,
        "fix-suggest": handle_fix_suggest,
        "settings-show": handle_settings_show,
        "settings-set": handle_settings_set,
        "onboard": handle_onboard,
    }

    handler = handlers.get(command)
    if handler is None:
        emit({"ok": False, "error": f"Unknown command: {command}"}, 1)
    handler(command_args)


if __name__ == "__main__":
    main()
