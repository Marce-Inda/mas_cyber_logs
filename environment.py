import json
import time

class CyberEnvironment:
    """
    Simulation Environment for MAS Cyber Logs tracking system state 
    and maintaining logs over time.
    """
    def __init__(self):
        self.state = {
            "suspicious_events": 0,
            "compromised_hosts": 0
        }
        self.logs = []
        
    def step(self, agents):
        """Advances the simulation by one tick, allowing all agents to act."""
        for agent in agents:
            # Agent's act function must return a dictionary representing the log
            log = agent.act(self.state)
            
            if log:
                # Append standard metadata
                log['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S')
                self.logs.append(log)
                
                # Update environment state based on log action
                action = log.get("action", "").lower()
                event_type = log.get("event_type", "").lower()
                
                if "suspicious" in action or event_type == "suspicious":
                    self.state["suspicious_events"] += 1
                
                if "compromise" in action or event_type == "compromise":
                    self.state["compromised_hosts"] += 1

    def save_logs(self, filename="logs.json"):
        """Exports the generated logs to a JSON file and attempts to upload to Firebase."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=4)
        print(f"[Environment] Logs saved to {filename} ({len(self.logs)} events)")

        # Firebase integration: Upload via Admin SDK directly to Storage
        # Skipped locally because bucket requires Blaze plan
        """
        try:
            from firebase_admin import storage
            # This requires firebase_admin to be initialized in main.py
            bucket = storage.bucket()
            blob_name = f"mas-logs/{filename}"
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(filename, content_type='application/json')
            print(f"[Firebase] Successfully uploaded {filename} to Storage: {blob_name}")
        except ImportError:
            pass # firebase_admin not installed
        except ValueError:
            pass # firebase_admin not initialized
        except Exception as e:
            print(f"[Firebase] Warning: Could not upload directly to Storage: {e}")
        """
            
        # Optional: Send via HTTP Cloud Function (generateLogs) if deployed
        # Uncomment to use the Cloud Function route instead
        """
        import requests
        try:
            url = "https://us-central1-the-responder-36ce2.cloudfunctions.net/generateLogs"
            response = requests.post(url, json=self.logs)
            if response.status_code == 200:
                print(f"[Cloud Function] Logs processed successfully: {response.json()}")
            else:
                print(f"[Cloud Function] Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[Cloud Function] Error invoking function: {e}")
        """
