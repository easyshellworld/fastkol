import requests
import os
import json

API_KEY = "sk_V2_hgu_kEcEgMV04dz_MGfUXmYrSbpqGGMxF86HD967VQV8f6Ci"
VIDEO_ID = "efa8285c63334ee78d925bb32cf485d3"

def check_status():
    url = f"https://api.heygen.com/v1/video_status.get?video_id={VIDEO_ID}"
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # print(json.dumps(data, indent=2))
        
        status = data.get("data", {}).get("status")
        video_url = data.get("data", {}).get("video_url")
        
        print(f"Status: {status}")
        if video_url:
            print(f"Video URL: {video_url}")
            with open("video_url.txt", "w") as f:
                f.write(video_url)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_status()
