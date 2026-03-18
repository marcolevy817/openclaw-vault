import warnings
warnings.filterwarnings("ignore")
from google import genai
from google.genai import types

API_KEY = "AIzaSyCGMrw7_ezmTTKHbz7CzFKzhZbZQhLF-Dw"
client = genai.Client(api_key=API_KEY)

jobs = [
    {
        "file": "skill-infographic-gemini.png",
        "prompt": (
            "Create an image: A sleek modern tech infographic on a dark navy background. Title: 'What is an OpenClaw Skill?' "
            "in bold purple-to-blue gradient text. "
            "Center: a glowing folder icon labeled 'my-skill/' containing a bright document labeled 'SKILL.md'. "
            "Four cards around it: brain 'AI reads SKILL.md', plug 'Pluggable & shareable', "
            "target 'Triggered by context', package 'Self-contained module'. "
            "Bottom flow: You ask → Agent matches → Reads SKILL.md → Done. "
            "Purple and blue color scheme, clean professional developer aesthetic."
        )
    },
    {
        "file": "cat-climbing-tree.png",
        "prompt": (
            "Create an image: A cute orange tabby cat with white paws climbing up a tall oak tree "
            "in warm golden afternoon sunlight. The cat is halfway up the trunk, claws gripping bark, "
            "tail curled, looking up adventurously. Lush green leaves above, soft bokeh background. "
            "Photorealistic, warm golden hour lighting."
        )
    }
]

for job in jobs:
    print(f"Generating: {job['file']} ...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=job["prompt"],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )
        saved = False
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                out_path = f"/Users/xcm-mac/.openclaw/workspace/.tmp/{job['file']}"
                with open(out_path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"  ✅ Saved {len(part.inline_data.data)//1024}KB → {out_path}")
                saved = True
                break
        if not saved:
            text = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    text = part.text[:200]
            print(f"  ❌ No image in response. Text: {text}")
    except Exception as e:
        print(f"  ❌ {e}")

print("All done.")
