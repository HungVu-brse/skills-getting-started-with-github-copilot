"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participant_phone_numbers": {},
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participant_phone_numbers": {},
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participant_phone_numbers": {},
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Practice passing, teamwork, and competitive matches",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participant_phone_numbers": {},
        "participants": ["alex@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Train shooting, defense, and game strategy",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participant_phone_numbers": {},
        "participants": ["jordan@mergington.edu"]
    },
    "Drama Club": {
        "description": "Explore acting, stage performance, and dramatic storytelling",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participant_phone_numbers": {},
        "participants": ["ava@mergington.edu"]
    },
    "Art Club": {
        "description": "Create paintings, sketches, and mixed-media projects",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participant_phone_numbers": {},
        "participants": ["noah@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Fridays, 2:30 PM - 3:30 PM",
        "max_participants": 10,
        "participant_phone_numbers": {},
        "participants": ["liam@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific discoveries",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participant_phone_numbers": {},
        "participants": ["grace@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, phone_number: str):
    """Sign up a student for an activity"""
    if len(phone_number) != 10 or not phone_number.isdigit() or not phone_number.startswith("0"):
        raise HTTPException(
            status_code=422,
            detail="Phone number must start with 0 and contain exactly 10 digits",
        )

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    activity["participants"].append(email)
    activity["participant_phone_numbers"][email] = phone_number
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def remove_participant(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    participants = activity["participants"]
    if email not in participants:
        raise HTTPException(status_code=404, detail="Participant not found")

    participants.remove(email)
    phone_number = activity["participant_phone_numbers"].pop(email, "")
    return {
        "message": f"Removed {email} from {activity_name}",
        "phone_number": phone_number,
    }
