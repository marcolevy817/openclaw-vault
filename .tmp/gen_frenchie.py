import warnings
warnings.filterwarnings("ignore")
from google import genai
from google.genai import types

API_KEY = "AIzaSyCGMrw7_ezmTTKHbz7CzFKzhZbZQhLF-Dw"
client = genai.Client(api_key=API_KEY)

prompt = (
    "A cute French Bulldog sitting and smiling with one single tooth sticking out from its lower jaw, "
    "giving it a goofy and adorable underbite expression. The dog has a bat-like ears, wrinkly face, "
    "short snout, and a brindle or fawn coat. Soft studio lighting, warm background, "
    "photorealistic, ultra detailed, high quality."
)

print("Generating French Bulldog image...")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"]
        )
    )
    saved = False
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data is not None:
            out_path = "/root/.openclaw/workspace/.tmp/frenchie.png"
            with open(out_path, "wb") as f:
                f.write(part.inline_data.data)
            print(f"✅ Saved {len(part.inline_data.data)//1024}KB → {out_path}")
            saved = True
            break
    if not saved:
        text = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                text = part.text[:300]
        print(f"❌ No image in response. Text: {text}")
except Exception as e:
    print(f"❌ {e}")
