from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich.live import Live
from rich.prompt import Prompt, IntPrompt, Confirm
import os
import time

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    console.print(Panel(
        Align.center("[bold magenta]Developed With ❤️  By 📸 @rithikvinayak_[/bold magenta]"),
        border_style="bright_blue",
        title="[bold green]Termux Instagram Bot[/bold green]",
        subtitle="[italic cyan]Automation Dashboard[/italic cyan]"
    ))

def get_status_table(config):
    table = Table(title="Service Status", expand=True)
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Delay (s)", style="yellow")
    table.add_column("Settings", style="dim")

    services = config.settings.get("services", {})
    
    for name, cfg in services.items():
        enabled = cfg.get("enabled", False)
        status = "[green][ENABLED][/green]" if enabled else "[red][DISABLED][/red]"
        delay = f"{cfg.get('delay_min')}-{cfg.get('delay_max')}"
        
    # Display extra info
        extra = ""
        if name == "timeline_commenter":
            count = len(cfg.get("comments", []))
            extra = f"{count} comments"
        
        # Source Info
        if name != "story_watcher":
            sType = cfg.get("source_type", "hashtag")
            sVal = cfg.get("source_value", "none")
            extra += f" | {sType}: {sVal}"
        else:
            likes = "Yes" if cfg.get("like_stories", True) else "No"
            extra += f" | Like: {likes}"
            
        table.add_row(name.replace("_", " ").title(), status, delay, extra)
        
    return table

class Dashboard:
    def __init__(self, config):
        self.config = config
        self.logs = []
        self.max_logs = 10

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def get_renderable(self):
        # Returns a Group of renderables for Live display
        from rich.console import Group
        
        # Header
        header = Panel(
            Align.center("[bold magenta]Developed With ❤️  By 📸 @rithikvinayak_[/bold magenta]"),
            border_style="bright_blue",
            title="[bold green]Termux Instagram Bot[/bold green]",
            subtitle="[italic cyan]Automation Dashboard[/italic cyan]"
        )
        
        # Status
        status_table = get_status_table(self.config)
        
        # Logs
        log_text = "\n".join(self.logs) if self.logs else "[italic dim]No active logs...[/italic dim]"
        logs_panel = Panel(
            log_text,
            title="Bot Activity Logs",
            title_align="left",
            border_style="yellow",
            height=15
        )
        
        return Group(header, status_table, logs_panel)

    def render_view(self):
        clear_screen()
        console.print(self.get_renderable())
        
        console.print("\n[bold]Configuration Menu:[/bold]")
        console.print("1. [bold cyan]Bot Liker[/bold cyan] [Toggle/Set/Source]")
        console.print("2. [bold cyan]Bot Commenter[/bold cyan] [Toggle/Set/Source/Comments]")
        console.print("3. [bold cyan]Story Watcher[/bold cyan] [Toggle/Set/Like]")
        console.print("4. [bold red]Start/Stop Bot[/bold red] (Use Ctrl+C to Stop Monitoring)")
        console.print("5. [bold]Edit Credentials[/bold]")
        console.print("0. [bold]Exit[/bold]")

    def configure_service(self, service_key, pretty_name):
        cfg = self.config.get_service_config(service_key)
        console.print(f"\n[bold]Configuring {pretty_name}[/bold]")
        
        # Toggle
        current_status = cfg.get("enabled", False)
        if Confirm.ask(f"Enable {pretty_name}?", default=current_status):
            self.config.update_service_config(service_key, "enabled", True)
        else:
            self.config.update_service_config(service_key, "enabled", False)
            
        # Delay
        if service_key != "reels_booster":
             console.print("[italic]Safe Human-like Delay: 30-60 seconds[/italic]")
             min_d = IntPrompt.ask("Min Delay", default=cfg.get("delay_min", 30))
             max_d = IntPrompt.ask("Max Delay", default=cfg.get("delay_max", 60))
             self.config.update_service_config(service_key, "delay_min", min_d)
             self.config.update_service_config(service_key, "delay_max", max_d)
        

        # Target Source (Liker/Commenter/Story)
        if service_key in ["timeline_liker", "timeline_commenter", "story_watcher"]:
            console.print("\n[bold]Target Source:[/bold]")
            options = ["hashtag", "followers", "following", "location"]
            if service_key == "story_watcher":
                options.insert(0, "feed") # Default for stories
                
            s_type = Prompt.ask("Select Source", choices=options, default=cfg.get("source_type", "feed" if service_key == "story_watcher" else "hashtag"))
            
            if s_type == "feed":
                s_val = "none"
            else:
                prompt_text = "Enter Hashtag (without #)"
                if s_type == "followers": prompt_text = "Enter Username to scrape Followers from"
                if s_type == "following": prompt_text = "Enter Username to scrape Following from"
                if s_type == "location": prompt_text = "Enter Location ID"
                
                s_val = Prompt.ask(prompt_text, default=cfg.get("source_value", "instagram"))
            
            self.config.update_service_config(service_key, "source_type", s_type)
            self.config.update_service_config(service_key, "source_value", s_val)

        # Story Like Toggle
        if service_key == "story_watcher":
             do_like = Confirm.ask("Like Stories while watching?", default=cfg.get("like_stories", True))
             self.config.update_service_config(service_key, "like_stories", do_like)

        # Extra for Commenter
        if service_key == "timeline_commenter":
            console.print(f"\nCurrent Comments: {cfg.get('comments', [])}")
            if Confirm.ask("Edit Comments List?"):
                new_comments_str = Prompt.ask("Enter comments separated by comma")
                new_comments = [c.strip() for c in new_comments_str.split(",") if c.strip()]
                self.config.update_service_config(service_key, "comments", new_comments)
                
        console.print("[green]Settings Saved![/green]")
        time.sleep(1)

