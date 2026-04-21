import os
import json
import subprocess
import requests
import shutil
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from time import sleep

console = Console()

CONFIG_DIR = "config"
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
GLOBAL_SETTINGS_PATH = os.path.join(CONFIG_DIR, "global_settings.json")
TOKENS_PATH = "tokens.txt"
BACKUP_DIR = "backup_configs"

GITHUB_API_URL = "https://api.github.com/repos/kiy0w0/owomizu"
GITHUB_REPO_URL = "https://github.com/kiy0w0/owomizu.git"

MIZU_API_URL = "https://api.ive.my.id"

def print_mizu_header():

    header_text = Text()
    header_text.append("MIZU ", style="bold cyan")
    header_text.append("水", style="bold blue")
    header_text.append(" NETWORK UPDATER", style="bold cyan")

    panel = Panel(
        header_text,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def get_current_version():

    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()[:8]
    except subprocess.CalledProcessError:
        return "unknown"

def get_latest_version():

    try:
        response = requests.get(f"{GITHUB_API_URL}/commits/main", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['sha'][:8]
        else:
            console.print(f"[red]Failed to fetch version info: {response.status_code}[/red]")
            return None
    except requests.RequestException as e:
        console.print(f"[red]Error fetching version: {e}[/red]")
        return None

def check_for_updates():

    console.print("[cyan]🔍 Checking for updates...[/cyan]")

    current = get_current_version()
    latest = get_latest_version()

    if latest is None:
        return False, current, "unknown"

    if current != latest:
        console.print(f"[green]📦 Update available![/green]")
        console.print(f"[yellow]Current version: {current}[/yellow]")
        console.print(f"[green]Latest version: {latest}[/green]")
        return True, current, latest
    else:
        console.print(f"[green]✅ You're running the latest version ({current})[/green]")
        return False, current, latest

def create_backup():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")

    try:
        os.makedirs(backup_path, exist_ok=True)

        if os.path.exists(SETTINGS_PATH):
            shutil.copy2(SETTINGS_PATH, backup_path)
        if os.path.exists(GLOBAL_SETTINGS_PATH):
            shutil.copy2(GLOBAL_SETTINGS_PATH, backup_path)
        if os.path.exists(TOKENS_PATH):
            shutil.copy2(TOKENS_PATH, backup_path)

        console.print(f"[green]💾 Backup created: {backup_path}[/green]")
        return backup_path
    except Exception as e:
        console.print(f"[red]❌ Failed to create backup: {e}[/red]")
        return None

def read_tokens_file():

    try:
        with open(TOKENS_PATH, "r") as tokens_file:
            return tokens_file.read()
    except FileNotFoundError:
        return ""

def write_tokens_file(content):

    try:
        with open(TOKENS_PATH, "w") as tokens_file:
            tokens_file.write(content)
    except Exception as e:
        console.print(f"[red]❌ Failed to write tokens file: {e}[/red]")

def load_config_file(file_path):

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as config_file:
                return json.load(config_file)
        return {}
    except Exception as e:
        console.print(f"[red]❌ Failed to load {file_path}: {e}[/red]")
        return {}

def deep_merge_carry_over(base, new):

    result = {}

    for key, value in new.items():
        if key in base:
            if isinstance(value, dict) and isinstance(base[key], dict):
                result[key] = deep_merge_carry_over(base[key], value)
            else:
                result[key] = base[key]
        else:
            result[key] = value

    return result

def save_config_file(file_path, data):

    try:
        with open(file_path, 'w') as output_file:
            json.dump(data, output_file, indent=4)
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to save {file_path}: {e}[/red]")
        return False

def merge_configurations(backup_path):

    console.print("[cyan]🔧 Merging configurations...[/cyan]")

    backup_settings = load_config_file(os.path.join(backup_path, "settings.json"))
    backup_global = load_config_file(os.path.join(backup_path, "global_settings.json"))

    new_settings = load_config_file(SETTINGS_PATH)
    new_global = load_config_file(GLOBAL_SETTINGS_PATH)

    if backup_settings and new_settings:
        merged_settings = deep_merge_carry_over(backup_settings, new_settings)
        if save_config_file(SETTINGS_PATH, merged_settings):
            console.print("[green]✅ Settings configuration merged[/green]")

    if backup_global and new_global:
        merged_global = deep_merge_carry_over(backup_global, new_global)
        if save_config_file(GLOBAL_SETTINGS_PATH, merged_global):
            console.print("[green]✅ Global configuration merged[/green]")

    backup_tokens_path = os.path.join(backup_path, "tokens.txt")
    if os.path.exists(backup_tokens_path):
        try:
            with open(backup_tokens_path, "r") as backup_tokens:
                tokens_content = backup_tokens.read()
            write_tokens_file(tokens_content)
            console.print("[green]✅ Tokens restored[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to restore tokens: {e}[/red]")

def perform_git_update(backup_path):

    try:
        repo_dir = "."
        os.chdir(repo_dir)

        with console.status("[bold cyan]🔍 Checking for uncommitted changes..."):
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True, check=True)

        if status_result.stdout:
            console.print("[yellow]⚠️ Uncommitted changes detected. Stashing changes...[/yellow]")
            with console.status("[bold yellow]📦 Stashing changes..."):
                subprocess.run(['git', 'stash'], check=True)
            sleep(1)

        with console.status("[bold cyan]🔍 Checking for untracked files..."):
            untracked_files = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], 
                                           capture_output=True, text=True, check=True)

        if untracked_files.stdout:
            console.print("[yellow]⚠️ Untracked files detected. Cleaning up...[/yellow]")
            with console.status("[bold red]🧹 Cleaning untracked files..."):
                subprocess.run(['git', 'clean', '-f', '-d'], check=True)
                sleep(1)

        with console.status("[bold cyan]🔄 Switching to main branch..."):
            subprocess.run(['git', 'checkout', 'main'], check=True)

        with console.status("[bold green]⬇️ Pulling latest changes from GitHub..."):
            result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                  capture_output=True, text=True, check=True)
            sleep(1)

        if "Already up to date" in result.stdout:
            console.print("[green]✅ Repository was already up to date[/green]")
            return True
        else:
            console.print("[green]✅ Successfully pulled latest changes[/green]")
            return True

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Git operation failed: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Unexpected error during update: {e}[/red]")
        return False

def rollback_update(backup_path):

    console.print("[yellow]🔄 Rolling back update...[/yellow]")
    try:
        if os.path.exists(backup_path):
            merge_configurations(backup_path)
            console.print("[green]✅ Rollback completed[/green]")
            return True
        else:
            console.print("[red]❌ Backup not found, cannot rollback[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Rollback failed: {e}[/red]")
        return False

def fetch_mizu_announcements():

    return []

def main():

    print_mizu_header()

    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]❌ Git is not installed or not available in PATH[/red]")
        console.print("[yellow]Please install Git and try again[/yellow]")
        return False

    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        console.print("[red]❌ This directory is not a git repository[/red]")
        console.print(f"[yellow]Please clone the repository first:[/yellow]")
        console.print(f"[cyan]git clone {GITHUB_REPO_URL}[/cyan]")
        return False

    has_updates, current_version, latest_version = check_for_updates()

    if not has_updates:
        announcements = fetch_mizu_announcements()
        if announcements:
            console.print("\n[bold cyan]📢 Announcements from Mizu Network:[/bold cyan]")
            for announcement in announcements:
                console.print(f"[yellow]• {announcement}[/yellow]")

        console.print("\n[green]🎉 You're all set! No updates needed.[/green]")
        return True

    console.print()
    if not Confirm.ask("[bold cyan]Would you like to update now?[/bold cyan]", default=True):
        console.print("[yellow]Update cancelled by user[/yellow]")
        return False

    console.print("\n[cyan]📦 Creating backup of your configurations...[/cyan]")
    backup_path = create_backup()
    if not backup_path:
        console.print("[red]❌ Failed to create backup. Update cancelled for safety.[/red]")
        return False

    console.print("\n[cyan]🚀 Starting update process...[/cyan]")
    update_success = perform_git_update(backup_path)

    if not update_success:
        console.print("\n[red]❌ Update failed. Rolling back...[/red]")
        rollback_update(backup_path)
        return False

    console.print("\n[cyan]🔧 Restoring your configurations...[/cyan]")
    merge_configurations(backup_path)

    console.print("\n[bold green]🎉 Update completed successfully![/bold green]")
    console.print(f"[green]✅ Updated from {current_version} to {latest_version}[/green]")

    announcements = fetch_mizu_announcements()
    if announcements:
        console.print("\n[bold cyan]📢 Latest announcements:[/bold cyan]")
        for announcement in announcements:
            console.print(f"[yellow]• {announcement}[/yellow]")

    console.print("\n[bold cyan]🚀 Next steps:[/bold cyan]")
    console.print("[cyan]• Run 'python mizu.py' to start the updated bot[/cyan]")
    console.print("[cyan]• Check your configurations in the config/ folder[/cyan]")
    console.print(f"[cyan]• Your backup is saved in: {backup_path}[/cyan]")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            console.print("\n[bold green]Thank you for using Mizu Network! 水[/bold green]")
        else:
            console.print("\n[bold red]Update process failed. Please check the errors above.[/bold red]")
            exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Update cancelled by user[/yellow]")
        exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        exit(1)