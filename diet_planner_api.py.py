from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, validator
import google.generativeai as genai
import uvicorn
import os
import nest_asyncio
import asyncio
import re

# Apply nest_asyncio to fix the event loop issue in notebooks
nest_asyncio.apply()

app = FastAPI()

# Configure Gemini API - Use a direct API key for simplicity in this example
GENAI_API_KEY = "AIzaSyApoBMdGlXi-XJTfOBPyq3cU4dPvMLOge4"  # Replace with your API key in production
genai.configure(api_key=GENAI_API_KEY)

class DietPlanRequest(BaseModel):
    name: str
    gender: str
    age: int
    height: float
    weight: float
    activity_level: str
    goal: str
    diet_pref: str
    allergies: str
    medical_conditions: str
    meal_pref: str
    budget_level: str
    days: int = 7  # Default to 7 days

    @validator("days")
    def check_days(cls, value):
        if value > 14:
            raise ValueError("The number of days cannot exceed 14.")
        if value < 1:
            raise ValueError("The number of days must be at least 1.")
        return value

async def stream_diet_plan(data: DietPlanRequest):
    prompt = f"""Create a personalized diet plan for a client based on the following details:
    
Age: {data.age}
Gender: {data.gender}
Height: {data.height} cm
Weight: {data.weight} kg
Activity Level: {data.activity_level}
Goal: {data.goal}
Dietary Preferences: {data.diet_pref}
Allergies or Restrictions: {data.allergies}
Medical Conditions: {data.medical_conditions}
Meal Preferences: {data.meal_pref}
Budget Range: {data.budget_level}
Number of Days: {data.days}

Generate a {data.days}-day meal plan with breakfast, lunch, snacks, and dinner for each day. Include calorie estimates, macronutrient breakdowns (carbs, proteins, fats), and portion sizes. Ensure the meals align with the client's preferences.
Do not include client details in the response. Just provide the structured meal plan."""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt, stream=True)
    
    buffer = ""
    
    for chunk in response:
        if chunk.text:
            # Add text to buffer
            buffer += chunk.text
            
            # Process buffer to create natural breaks
            while len(buffer) > 0:
                # Find natural breakpoints like sentence endings, list items, etc.
                match = re.search(r'([.!?]\s+|\n|:\s*|\d+\.\s+)', buffer)
                
                if match and match.start() > 0:
                    # Send text up to the natural break
                    segment = buffer[:match.end()]
                    
                    # Break segment into smaller chunks (words or short phrases)
                    words = re.findall(r'\S+\s*', segment)
                    current_chunk = ""
                    
                    for word in words:
                        current_chunk += word
                        # Send smaller chunks (2-4 words at a time)
                        if len(current_chunk.split()) >= 3 or len(current_chunk) > 20:
                            yield current_chunk
                            await asyncio.sleep(0.05)  # Shorter delay between small chunks
                            current_chunk = ""
                    
                    # Send any remaining text in the current chunk
                    if current_chunk:
                        yield current_chunk
                    
                    buffer = buffer[match.end():]
                    
                    # Add slightly longer pause at natural breaks
                    if ":" in segment:  # Headers get longer pauses
                        await asyncio.sleep(0.3)
                    elif "." in segment:  # End of sentences
                        await asyncio.sleep(0.15)
                    elif "\n" in segment:  # Line breaks
                        await asyncio.sleep(0.1)
                else:
                    # If no natural break is found and buffer is getting large, send a chunk
                    if len(buffer) > 20:
                        segment = buffer[:20]
                        buffer = buffer[20:]
                        yield segment
                        await asyncio.sleep(0.05)
                    else:
                        # Buffer isn't large enough to split yet and has no natural breaks
                        break
    
    # Send any remaining text in the buffer
    if buffer:
        yield buffer

@app.post("/generate_diet_plan")
async def generate_diet_plan(request: DietPlanRequest):
    try:
        return StreamingResponse(stream_diet_plan(request), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app directly (works in notebooks with nest_asyncio)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    # For when running in a notebook
    uvicorn.run(app, host="0.0.0.0", port=8000)
