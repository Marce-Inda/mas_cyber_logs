import sys
import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
from environment import CyberEnvironment
from agents import UserAgent, SysAdminAgent, AttackerAgent, CEOAgent

def main():
    print("Loading environment variables and Initializing Firebase Admin SDK...")
    load_dotenv()
    
    try:
        if os.getenv("FIREBASE_PROJECT_ID") and os.getenv("FIREBASE_PRIVATE_KEY") and os.getenv("FIREBASE_CLIENT_EMAIL"):
            # Ensure proper newline formatting in private key
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
            
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
                "private_key": private_key,
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL').replace('@', '%40')}") if os.getenv("FIREBASE_CLIENT_EMAIL") else ""
            })
            
            # Extract App Engine bucket format for Storage based on project ID
            bucket_name = f"{os.getenv('FIREBASE_PROJECT_ID')}.appspot.com"
            firebase_admin.initialize_app(cred, {
                'storageBucket': bucket_name
            })
            print("✅ Firebase Admin SDK initialized successfully via .env configuration.")
        else:
            print("Warning: Missing required Firebase environment variables in .env.")
    except Exception as e:
        print(f"Warning: Firebase Admin SDK initialization failed: {e}")

    print("Initializing Cyber Environment...")
    env = CyberEnvironment()
    
    print("Initializing MAS Agents...")
    agents = []
    # 8x UserAgent
    for i in range(1, 9):
        agents.append(UserAgent(name=f"User_0{i}"))
        
    # SysAdmin, Attacker, CEO
    agents.append(SysAdminAgent(name="SysAdmin_Alpha"))
    agents.append(AttackerAgent(name="APT_Threat_Actor"))
    agents.append(CEOAgent(name="CEO_Boss"))
    
    print(f"Total Agents: {len(agents)}")
    print("Starting Simulation (60 Ticks)...")
    
    # 60 Ticks Simulation
    for tick in range(1, 61):
        if tick % 10 == 0:
            print(f"  -> Processing Tick {tick}/60...")
        env.step(agents)
        
    print("\nSimulation Complete.")
    print(f"Final State: {env.state}")
    
    # Save output to logs.json
    env.save_logs("logs.json")
    print("Output available in logs.json")

if __name__ == "__main__":
    main()
