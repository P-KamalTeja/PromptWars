"""
Legacy entry point - redirects to main.py

For new usage, please use:
  python main.py --ui web      # For web UI
  python main.py --ui gradio   # For Gradio UI

This file is kept for backward compatibility.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from main import main

if __name__ == "__main__":
    # Default to web UI for legacy compatibility
    sys.argv.append("--ui")
    sys.argv.append("web")
    main()
    Travelers: {travelers}
    
    Current Weather:
    Temperature: {weather['temperature']} C
    Condition: {weather['condition']}
    Humidity: {weather['humidity']}%
    
    Requirements:
    - Day-wise itinerary
    - Budget-conscious recommendations
    - Hotels
    - Restaurants
    - Activities
    - Local transportation
    - Indoor alternatives if weather is bad
    - Approximate costs
    - Optimized scheduling
    
    Format nicely in markdown.
    '''
    
    response = model.generate_content(prompt)
    return response.text


def update_trip(existing_plan, user_request):
    """Update an existing trip plan based on user feedback"""
    prompt = f'''
    You are an AI Travel Assistant.
    
    Existing Trip Plan:
    {existing_plan}
    
    User Update Request:
    {user_request}
    
    Update the itinerary accordingly.
    Maintain proper formatting.
    '''
    
    response = model.generate_content(prompt)
    return response.text


def planner_ui(destination, budget, days, interests, travelers):
    """UI function for Gradio"""
    return generate_trip(destination, budget, days, interests, travelers)


# Create Gradio interface
planner = gr.Interface(
    fn=planner_ui,
    inputs=[
        gr.Textbox(label="Destination", placeholder="e.g., Paris, Tokyo, New York"),
        gr.Textbox(label="Budget", placeholder="e.g., $2000, £1500"),
        gr.Slider(1, 14, value=5, step=1, label="Trip Duration (Days)"),
        gr.Textbox(label="Interests", placeholder="e.g., Museums, Hiking, Food, History"),
        gr.Textbox(label="Travelers", placeholder="e.g., Couple, Family of 4, Solo")
    ],
    outputs=gr.Markdown(label="Generated Itinerary"),
    title="AI Travel Planning Platform",
    description="Generate intelligent travel itineraries dynamically using Gemini AI.",
    theme=gr.themes.Soft()
)


if __name__ == "__main__":
    planner.launch(server_name="0.0.0.0", server_port=8080, share=False)