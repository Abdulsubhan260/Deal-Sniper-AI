import os
import base64
import asyncio
from dotenv import load_dotenv

from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import edge_tts

load_dotenv()

# 1. INITIALIZE CLIENTS
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Vision model for OCR & parsing
vision_llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.1,max_tokens=600)


def encode_image(image_path: str) -> str:
    """Reads local image in binary mode and returns Base64 UTF-8 string."""
    
    with open(image_path,'rb') as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

    


def extract_job_metadata(image_path: str) -> str:
    """Inspects job screenshot and extracts structured job & client metrics."""
    if not os.path.exists(image_path):
        return f" Error: Image '{image_path}' not found."

    print(f"\n--- 1. PARSING JOB SCREENSHOT: {image_path} ---")
    base64_img = encode_image(image_path)

    # Prompt forcing strict structured extraction
    prompt = """
    Analyze this freelance job posting screenshot carefully.
    Extract the following details in a clean, structured format:
    1. Job Title
    2. Client Country
    3. Payment Verified (Yes/No)
    4. Client Total Spend (e.g. $10k+, $50k+, or $0)
    5. Client Star Rating (e.g. 4.9 or None)
    6. Client Hire Rate (e.g. 70% or None)
    7. Primary Technical Skills Required (list them)
    8. Core Client Problem (1-2 sentence summary of what needs to be solved)

    Be concise and factual. If a metric is not visible, write 'Unknown'.
    """

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_img}"}
            }
        ]
    )

    
    response=vision_llm.invoke([message])
    return response.content
    


def parse_pitch_strategy(audio_path: str = None, typed_notes: str = "") -> str:
    """Combines spoken audio memo and typed user notes into a unified pitch strategy."""
    transcribed_voice = ""

    # Transcribe voice if audio file is provided and exists
    if audio_path and os.path.exists(audio_path):
        print(f"\n--- 2. TRANSCRIBING VOICE MEMO: {audio_path} ---")
        with open(audio_path, "rb") as f:
            transcription=groq_client.audio.transcriptions.create(
                file=(audio_path, f.read()),
                model="whisper-large-v3",
                response_format="text"
            )
            #
            transcribed_voice = None

    # Merge audio + typed notes (The Hybrid Pattern)
    strategy_parts = []
    if transcribed_voice:
        strategy_parts.append(f"Spoken Strategy: {transcribed_voice.strip()}")
    if typed_notes.strip():
        strategy_parts.append(f"Custom Freelancer Notes: {typed_notes.strip()}")

    if not strategy_parts:
        return "Default Strategy: Pitch standard enterprise best practices with competitive rates."

    return "\n".join(strategy_parts)


async def main():
    
    screenshot_file = "upwork_job.png"

    
    test_audio = "pitch_memo.mp3"
    comm = edge_tts.Communicate(
        "Make sure to emphasize our LangGraph multi-agent experience, offer a 2-week delivery timeline, and quote an hourly rate of seventy dollars.",
        "en-US-GuyNeural"
    )
    await comm.save(test_audio)

    # 3. Optional typed notes (testing dual input)
    my_typed_notes = "Include link to our deployed Hugging Face microservice demo."

    
    job_data = extract_job_metadata(screenshot_file)
    pitch_strategy = parse_pitch_strategy(audio_path=test_audio, typed_notes=my_typed_notes)

    print("\n==================================================")
    print("       SPRINT 2 INGESTION PACKET READY          ")
    print("==================================================")
    print(f"\n[EXTRACTED JOB DATA]:\n{job_data}")
    print(f"\n[UNIFIED PITCH STRATEGY]:\n{pitch_strategy}")

if __name__ == "__main__":
    asyncio.run(main())