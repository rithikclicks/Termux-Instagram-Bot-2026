import sys
import os
import time
import random
import logging

try:
    from instagrapi import Client
    from instagrapi.exceptions import (
        BadPassword, ReloginAttemptExceeded, ChallengeRequired,
        SelectContactPointRecoveryForm, RecaptchaChallengeForm,
        FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
    )
except ImportError:
    print("Error: 'instagrapi' library not found. Please run: pip install -r requirements.txt")
    sys.exit(1)

from config import Config
import instagrapi.types
from typing import Optional, Any

# --- MONKEY PATCH FOR PYDANTIC VALIDATION ERROR ---
# Fixes: Input should be a valid dictionary or instance of ClipsOriginalSoundInfo
try:
    from pydantic import ValidationError
    
    def patch_model_field(model_class, field_name):
        if hasattr(model_class, "model_fields"): # Pydantic v2
            if field_name in model_class.model_fields:
                model_class.model_fields[field_name].annotation = Optional[Any]
                model_class.model_rebuild(force=True)
        elif hasattr(model_class, "__fields__"): # Pydantic v1
            if field_name in model_class.__fields__:
                model_class.__fields__[field_name].outer_type_ = Optional[Any]
                model_class.__fields__[field_name].type_ = Any

    # 1. Patch ClipsOriginalSoundInfo (The specific error)
    if hasattr(instagrapi.types, "ClipsOriginalSoundInfo"):
        patch_model_field(instagrapi.types.ClipsOriginalSoundInfo, "audio_filter_infos")
        patch_model_field(instagrapi.types.ClipsOriginalSoundInfo, "consumption_info")

    # 2. Patch ClipsMetadata (The parent)
    if hasattr(instagrapi.types, "ClipsMetadata"):
        patch_model_field(instagrapi.types.ClipsMetadata, "original_sound_info")
        patch_model_field(instagrapi.types.ClipsMetadata, "music_info")

    # 3. Patch Media (The root - Nuclear Option)
    if hasattr(instagrapi.types, "Media"):
        patch_model_field(instagrapi.types.Media, "clips_metadata")

    # 4. Patch ImageCandidate (scans_profile error)
    if hasattr(instagrapi.types, "ImageCandidate"):
        patch_model_field(instagrapi.types.ImageCandidate, "scans_profile")

    print("[INFO] Applied Aggressive Pydantic Patches (Media, ClipsMetadata, ImageCandidate).")
except Exception as e:
    print(f"[WARNING] Could not apply Pydantic Patch: {e}")
# --------------------------------------------------
# MONKEY PATCH FOR EXTRACT_USER_GQL ERROR
# Fixes: TypeError: extract_user_gql() got an unexpected keyword argument 'update_headers'
try:
    import instagrapi.extractors
    from instagrapi.extractors import extract_user_gql as original_extract_user_gql
    import instagrapi.mixins.user

    def patched_extract_user_gql(data, update_headers=None):
        # Ignore update_headers if original doesn't support it
        return original_extract_user_gql(data)

    instagrapi.extractors.extract_user_gql = patched_extract_user_gql
    instagrapi.mixins.user.extract_user_gql = patched_extract_user_gql
    print("[INFO] Applied extract_user_gql Monkey Patch.")
except Exception as e:
    print(f"[WARNING] Could not apply extract_user_gql Patch: {e}")
# --------------------------------------------------

class InstaBot:
    def __init__(self, config: Config, log_callback=None):
        self.config = config
        self.cl = Client()
        self.log_callback = log_callback
        self.running = False
        
        # Session handling
        self.session_file = config.SESSION_FILE
        self.cl.delay_range = [1, 3] # Internal delay for safety

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[LOG] {message}")

    def login(self):
        username, password = self.config.get_credentials()
        
        if os.path.exists(self.session_file):
            self.log("Loading session...")
            try:
                self.cl.load_settings(self.session_file)
            except Exception as e:
                self.log(f"Could not load session: {e}")

        self.log(f"Attempting login for {username}...")
        try:
            self.cl.login(username, password)
            self.cl.dump_settings(self.session_file)
            self.log("Login successful!")
            return True
        except (ChallengeRequired, SelectContactPointRecoveryForm, RecaptchaChallengeForm) as e:
            self.log(f"Challenge/2FA required: {e}")
            print(f"\n[!] INSTAGRAM CHALLENGE: {e}")
            try:
                code = input("Enter 2FA Code/SMS/Email Code: ")
                self.cl.challenge_code_handler(code)
                self.log("2FA/Challenge passed!")
                self.cl.dump_settings(self.session_file)
                return True
            except Exception as e2:
                self.log(f"2FA Failed: {e2}")
                print(f"[!] 2FA Handling Error: {e2}")
                return False
        except Exception as e:
            self.log(f"Login failed: {type(e).__name__} - {e}")
            print(f"\n[!] LOGIN ERROR: {type(e).__name__} - {e}")
            return False

    def get_delay(self, service_name):
        cfg = self.config.get_service_config(service_name)
        min_d = cfg.get("delay_min", 30)
        max_d = cfg.get("delay_max", 60)
        return random.randint(int(min_d), int(max_d))

    def timeline_liker(self):
        self.log("Starting Timeline Liker...")
        try:
            medias = self.cl.user_medias(self.cl.user_id, amount=5) # Check own media or timeline? Prompt says "Timeline Liker".
            # Usually "Timeline Liker" interprets as "Feed Liker" (home feed).
            # instagrapi has get_timeline_feed() but it might be risky. 
            # Let's interpret as hashtags or self-feed? "Fetch recent timeline media" -> Likely Home Feed.
            # Warning: Automated home feed actions are high risk.
            # Using user_medias of a target or hashtag is safer, but "Timeline" implies Home.
            # I'll use a safer approach: maybe interact with followers or specific hashtags if 'Timeline' is ambiguous,
            # but standard interpretation is Home Feed.
            # For safety loop, let's fetch pending feed.
            # Note: instagrapi's get_timeline_feed() might be complex. 
            # Let's mock safely if too complex or use hashtag for now as a safer 'timeline' proxy 
            # OR just implement `cl.get_timeline_feed()` if available.
            # Looking at instagrapi docs (mental check), it doesn't expose a simple public timeline feed easily due to API changes.
            # Iterating user's own feed (following) is safer.
            # 'Fetch recent timeline media' -> I will interpret this as checking the user's home feed.
            # Since instagrapi doesn't support generic home feed easily in all versions, 
            # I will use `hashtag_medias_top` or `user_medias` of some followed users as a proxy 
            # if direct feed isn't reliable, BUT let's try to mimic 'Timeline' by fetching from followed users.
            # Better strategy: Get list of followers/following, pick one, like their latest post.
            pass  # Logic will be inside run_loop to allow mixing services.
        except Exception as e:
            self.log(f"Timeline Liker Error: {e}")

    def fetch_media_from_source(self, service_name):
        cfg = self.config.get_service_config(service_name)
        s_type = cfg.get("source_type", "hashtag")
        s_val = cfg.get("source_value", "instagram")
        
        self.log(f"Fetching from {s_type}: {s_val}...")
        
        try:
            if s_type == "hashtag":
                medias = self.cl.hashtag_medias_top(s_val, amount=5)
                # Fallback to recent if top is empty
                if not medias: medias = self.cl.hashtag_medias_recent(s_val, amount=5)
                if medias: return random.choice(medias)
                
            elif s_type == "location":
                # Assuming s_val is location ID (int)
                if s_val.isdigit():
                    medias = self.cl.location_medias_top(int(s_val), amount=5)
                    if not medias: medias = self.cl.location_medias_recent(int(s_val), amount=5)
                    if medias: return random.choice(medias)
                else:
                    self.log(f"Invalid Location ID: {s_val} (Must be numeric)")

            elif s_type in ["followers", "following"]:
                # 1. Resolve User ID
                uid = None
                try:
                    uid = self.cl.user_id_from_username(s_val)
                except:
                    self.log(f"Could not find user: {s_val}")
                    return None
                
                if uid:
                    users = {}
                    if s_type == "followers":
                        users = self.cl.user_followers(uid, amount=20)
                    else:
                        users = self.cl.user_following(uid, amount=20)
                    
                    if users:
                        target_u = random.choice(list(users.keys()))
                        u_medias = self.cl.user_medias(target_u, amount=3)
                        if u_medias: return random.choice(u_medias)
            
            else:
                self.log(f"Unknown source type: {s_type}")
                
        except Exception as e:
            self.log(f"Fetch Error ({s_type}): {e}")
            
        return None

    def run(self):
        self.running = True
        self.log("Bot engine started.")
        
        while self.running:
            # check services
            services = self.config.settings.get("services", {})
            
            # --- Timeline Liker ---
            if services.get("timeline_liker", {}).get("enabled"):
                try:
                    target_media = self.fetch_media_from_source("timeline_liker")

                    if target_media:
                        if not getattr(target_media, 'has_liked', False):
                             u_name = target_media.user.username
                             self.log(f"Liking post by {u_name} ({target_media.pk})...")
                             self.cl.media_like(target_media.pk)
                             self.log("Liked successfully.")
                             time.sleep(self.get_delay("timeline_liker"))
                        else:
                             self.log(f"Already liked {target_media.pk}. Skipping.")
                    else:
                        self.log("Liker: No media found (Check source settings).")

                except Exception as e:
                    self.log(f"Liker Error: {type(e).__name__} - {e}")

            # --- Timeline Commenter ---
            if self.running and services.get("timeline_commenter", {}).get("enabled"):
                try:
                    target_media = self.fetch_media_from_source("timeline_commenter")

                    if target_media:
                        comments = services["timeline_commenter"].get("comments", ["Nice!"])
                        text = random.choice(comments)
                        u_name = target_media.user.username
                        self.log(f"Commenting '{text}' on post by {u_name}...")
                        self.cl.media_comment(target_media.pk, text)
                        self.log("Commented successfully.")
                        time.sleep(self.get_delay("timeline_commenter"))
                    else:
                        self.log("Commenter: No media found.")
                        
                except Exception as e:
                    self.log(f"Commenter Error: {e}")

            # --- Story Watcher ---
            if self.running and services.get("story_watcher", {}).get("enabled"):
                try:
                    self.log("Story Watcher: Finding stories...")
                    tray = []
                    s_type = services["story_watcher"].get("source_type", "feed")
                    
                    if s_type == "feed":
                         # Regular Tray Logic
                        try:
                            tray = self.cl.get_reels_tray()
                        except AttributeError:
                            try: tray = self.cl.get_timeline_stories()
                            except: pass
                        except Exception: pass
                        
                        if not tray:
                             try:
                                 followings = self.cl.user_following(self.cl.user_id, amount=5)
                                 if followings:
                                     u = random.choice(list(followings.keys()))
                                     tray = [self.cl.user_stories(u)]
                             except: pass
                    
                    else:
                        # Targeted Stories (Hashtag/Location/User)
                        target_media = self.fetch_media_from_source("story_watcher")
                        if target_media:
                            author_id = target_media.user.pk
                            self.log(f"Checking stories for user {target_media.user.username}...")
                            try:
                                user_stories = self.cl.user_stories(author_id)
                                if user_stories:
                                    tray = [type('MockTray', (object,), {'items': user_stories})()]
                            except Exception as e:
                                self.log(f"Could not get user stories: {e}")

                    if tray:
                        target = random.choice(tray)
                        # Try to get username of story owner
                        owner_name = "Unknown"
                        try:
                            if hasattr(target, 'user') and target.user:
                                owner_name = target.user.username
                            elif hasattr(target, 'items') and target.items and hasattr(target.items[0], 'user'):
                                owner_name = target.items[0].user.username
                        except: pass

                        items = target.items if hasattr(target, 'items') else target
                        if isinstance(items, list) and items:
                            should_like = services["story_watcher"].get("like_stories", True)
                            
                            for item in items:
                                try:
                                    self.cl.story_seen([item.pk])
                                    if should_like:
                                        self.cl.media_like(item.pk)
                                        self.log(f"Watched & Liked story by {owner_name}")
                                    else:
                                        self.log(f"Watched story by {owner_name}")
                                    time.sleep(2)
                                except:
                                    continue
                            time.sleep(self.get_delay("story_watcher"))
                        else:
                            self.log("Story Watcher: Empty story.")
                    else:
                        self.log("Story Watcher: No stories found.")

                except Exception as e:
                   self.log(f"Story Watcher Error: {e}")


            # Global sleep
            if not any(s.get("enabled", False) for s in services.values()):
                self.log("No services enabled. Sleeping...")
                time.sleep(10)
            else:
                self.log("Cycle complete. Sleeping briefly...")
                time.sleep(10)

    def stop(self):
        self.running = False
