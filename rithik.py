import threading
import time
import sys
from rich.console import Console
from rich.prompt import Prompt

from config import Config
from bot_engine import InstaBot
from interface import Dashboard
import os

LICENSE_KEY = "rithikvinayakkl07db7456"
LICENSE_FILE = "license.key"

def check_license():
    console = Console()
    
    # Check if license exists locally
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            if f.read().strip() == LICENSE_KEY:
                return True
    
    # Prompt user
    console.print(Panel(
        "[bold yellow]For purchasing license key 🗝  contact developer via instagram : @rithikvinayak_[/bold yellow]\n[cyan]( ₹1500 for life time access )[/cyan]",
        title="[red]LICENSE REQUIRED[/red]",
        border_style="red"
    ))
    
    key = Prompt.ask("Enter License Key", password=True)
    
    if key.strip() == LICENSE_KEY:
        with open(LICENSE_FILE, "w") as f:
            f.write(key.strip())
        console.print("[green]License Verified! Welcome.[/green]")
        time.sleep(2)
        return True
    else:
        console.print("[bold red]Invalid License Key! Exiting...[/bold red]")
        time.sleep(2)
        return False

def main():
    if not check_license():
        sys.exit(1)

    console = Console()
    config = Config()
    
    # Initialize UI
    dashboard = Dashboard(config)
    
    # Initialize Bot
    # Pass dashboard.add_log as callback
    bot = InstaBot(config, log_callback=dashboard.add_log)
    
    bot_thread = None

    while True:
        try:
            dashboard.render_view()
            
            # Simple status of bot
            if bot_thread and bot_thread.is_alive():
                 console.print("\n[bold green]BOT IS RUNNING IN BACKGROUND[/bold green]")
            else:
                 console.print("\n[bold red]BOT IS STOPPED[/bold red]")

            choice = Prompt.ask("\nSelect Option", choices=["1", "2", "3", "4", "5", "6", "0"], default="5")
            
            if choice == "1":
                dashboard.configure_service("timeline_liker", "Bot Liker")
            
            elif choice == "2":
                dashboard.configure_service("timeline_commenter", "Bot Commenter")
                
            elif choice == "3":
                dashboard.configure_service("story_watcher", "Story Watcher")
                
            elif choice == "4":
                dashboard.configure_service("reels_booster", "Reels Booster")
                
            elif choice == "5":
                # Start/Monitor Bot
                if not config.get_credentials()[0]:
                    console.print("[red]Please set credentials first (Option 6)![/red]")
                    time.sleep(2)
                    continue

                if not (bot_thread and bot_thread.is_alive()):
                    # Login check
                    console.print("[yellow]Logging in...[/yellow]")
                    if bot.login():
                        bot_thread = threading.Thread(target=bot.run, daemon=True)
                        bot_thread.start()
                    else:
                        console.print("[red]Login Failed! Check credentials.[/red]")
                        time.sleep(2)
                        continue
                
                # Monitor Loop
                from rich.live import Live
                try:
                    console.print("[green]Bot Started![/green]")
                    time.sleep(1)
                    
                    # Use Live display to prevent blinking
                    # screen=True uses alternate screen buffer (clean exit)
                    with Live(dashboard.get_renderable(), refresh_per_second=4, screen=True) as live:
                        while True:
                            live.update(dashboard.get_renderable())
                            time.sleep(0.5)
                            
                except KeyboardInterrupt:
                    # Determine if we should stop bot or just menu
                    # Prompt requirement: "Press Ctrl+C to stop" implies stopping the bot/script?
                    # Or just stopping the monitoring view?
                    # Usually user wants to stop the bot.
                    bot.stop()
                    if bot_thread:
                        bot_thread.join(timeout=2)
                    console.clear() # Clear alternate screen artifact if needed
                    console.print("\n[yellow]Bot Stopped. Returning to menu...[/yellow]")
                    time.sleep(1)
            
            elif choice == "6":
                u = Prompt.ask("Enter Username")
                p = Prompt.ask("Enter Password", password=True)
                config.set_credentials(u, p)
                console.print("[green]Credentials Saved![/green]")
                time.sleep(1)
                
            elif choice == "0":
                if bot_thread and bot_thread.is_alive():
                    bot.stop()
                    bot_thread.join()
                console.print("Goodbye!")
                sys.exit(0)
                
        except KeyboardInterrupt:
            # Global exit
            if bot_thread and bot_thread.is_alive():
                bot.stop()
            sys.exit(0)

if __name__ == "__main__":
    main()
