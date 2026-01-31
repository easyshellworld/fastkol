import os
import asyncio
import json
from dotenv import load_dotenv
from heygen_mcp.api_client import HeyGenApiClient, VideoGenerateRequest, VideoInput, Character, Voice, Dimension

async def debug_payload():
    load_dotenv()
    api_key = os.getenv("HEYGEN_API_KEY")
    client = HeyGenApiClient(api_key)
    
    avatar_id = os.getenv("HEYGEN_AVATAR_ID")
    voice_id = os.getenv("HEYGEN_VOICE_ID")
    
    request = VideoGenerateRequest(
        title="test-debug",
        video_inputs=[
            VideoInput(
                character=Character(avatar_id=avatar_id),
                voice=Voice(input_text="Hello", voice_id=voice_id),
            )
        ],
        test=True,
        dimension=Dimension(width=1280, height=720),
    )
    
    # Dump the internal model
    payload = request.model_dump()
    print("Capturing HeyGen Payload Structure:")
    print(json.dumps(payload, indent=2))
    
    # Try actual call
    print("\nAttempting actual API call with this payload...")
    try:
        resp = await client.generate_avatar_video(request)
        print(f"API Response: {resp}")
    except Exception as e:
        print(f"API error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(debug_payload())
