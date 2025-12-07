"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path
import io
import csv
from datetime import datetime

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
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}

# In-memory student database
students = {
    "michael@mergington.edu": {
        "name": "Michael Smith",
        "email": "michael@mergington.edu",
        "grade": "10"
    },
    "daniel@mergington.edu": {
        "name": "Daniel Johnson",
        "email": "daniel@mergington.edu",
        "grade": "11"
    },
    "emma@mergington.edu": {
        "name": "Emma Wilson",
        "email": "emma@mergington.edu",
        "grade": "9"
    },
    "sophia@mergington.edu": {
        "name": "Sophia Brown",
        "email": "sophia@mergington.edu",
        "grade": "10"
    },
    "john@mergington.edu": {
        "name": "John Davis",
        "email": "john@mergington.edu",
        "grade": "12"
    },
    "olivia@mergington.edu": {
        "name": "Olivia Martinez",
        "email": "olivia@mergington.edu",
        "grade": "11"
    },
    "liam@mergington.edu": {
        "name": "Liam Anderson",
        "email": "liam@mergington.edu",
        "grade": "10"
    },
    "noah@mergington.edu": {
        "name": "Noah Taylor",
        "email": "noah@mergington.edu",
        "grade": "9"
    },
    "ava@mergington.edu": {
        "name": "Ava Thomas",
        "email": "ava@mergington.edu",
        "grade": "11"
    },
    "mia@mergington.edu": {
        "name": "Mia Jackson",
        "email": "mia@mergington.edu",
        "grade": "10"
    },
    "amelia@mergington.edu": {
        "name": "Amelia White",
        "email": "amelia@mergington.edu",
        "grade": "12"
    },
    "harper@mergington.edu": {
        "name": "Harper Harris",
        "email": "harper@mergington.edu",
        "grade": "9"
    },
    "ella@mergington.edu": {
        "name": "Ella Martin",
        "email": "ella@mergington.edu",
        "grade": "11"
    },
    "scarlett@mergington.edu": {
        "name": "Scarlett Thompson",
        "email": "scarlett@mergington.edu",
        "grade": "10"
    },
    "james@mergington.edu": {
        "name": "James Garcia",
        "email": "james@mergington.edu",
        "grade": "12"
    },
    "benjamin@mergington.edu": {
        "name": "Benjamin Rodriguez",
        "email": "benjamin@mergington.edu",
        "grade": "11"
    },
    "charlotte@mergington.edu": {
        "name": "Charlotte Lee",
        "email": "charlotte@mergington.edu",
        "grade": "9"
    },
    "henry@mergington.edu": {
        "name": "Henry Walker",
        "email": "henry@mergington.edu",
        "grade": "10"
    }
}


# Pydantic models
class Student(BaseModel):
    name: str
    email: str
    grade: str


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    grade: Optional[str] = None


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# Student Management Endpoints

@app.get("/students")
def get_students(search: Optional[str] = None, grade: Optional[str] = None):
    """Get all students with optional search and filter"""
    result = students.copy()
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        result = {
            email: student for email, student in result.items()
            if search_lower in student["name"].lower() or search_lower in student["email"].lower()
        }
    
    # Apply grade filter
    if grade:
        result = {
            email: student for email, student in result.items()
            if student["grade"] == grade
        }
    
    return result


@app.post("/students")
def create_student(student: Student):
    """Create a new student"""
    # Check if student already exists
    if student.email in students:
        raise HTTPException(status_code=400, detail="Student with this email already exists")
    
    # Add student
    students[student.email] = {
        "name": student.name,
        "email": student.email,
        "grade": student.grade
    }
    
    return {"message": "Student created successfully", "student": students[student.email]}


@app.get("/students/{email}")
def get_student(email: str):
    """Get a specific student"""
    if email not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return students[email]


@app.put("/students/{email}")
def update_student(email: str, student_update: StudentUpdate):
    """Update a student's information"""
    # Check if student exists
    if email not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update fields that are provided
    if student_update.name is not None:
        students[email]["name"] = student_update.name
    if student_update.grade is not None:
        students[email]["grade"] = student_update.grade
    
    # If email is being updated, we need to update the key
    if student_update.email is not None and student_update.email != email:
        # Check if new email already exists
        if student_update.email in students:
            raise HTTPException(status_code=400, detail="Email already in use by another student")
        
        # Update email in student record
        students[email]["email"] = student_update.email
        
        # Move the student to new email key
        students[student_update.email] = students.pop(email)
        
        # Update email in all activity participants
        for activity in activities.values():
            if email in activity["participants"]:
                activity["participants"].remove(email)
                activity["participants"].append(student_update.email)
        
        return {"message": "Student updated successfully", "student": students[student_update.email]}
    
    return {"message": "Student updated successfully", "student": students[email]}


@app.delete("/students/{email}")
def delete_student(email: str):
    """Delete a student"""
    # Check if student exists
    if email not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Remove student from all activities
    for activity in activities.values():
        if email in activity["participants"]:
            activity["participants"].remove(email)
    
    # Delete student
    del students[email]
    
    return {"message": "Student deleted successfully"}


@app.get("/students/{email}/activities")
def get_student_activities(email: str):
    """Get all activities a student is enrolled in"""
    # Check if student exists
    if email not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Find all activities the student is enrolled in
    student_activities = []
    for activity_name, activity_details in activities.items():
        if email in activity_details["participants"]:
            student_activities.append({
                "name": activity_name,
                "description": activity_details["description"],
                "schedule": activity_details["schedule"]
            })
    
    return student_activities


@app.get("/students/export/csv")
def export_students_csv():
    """Export all students as CSV"""
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Name", "Email", "Grade", "Activities Count"])
    
    # Write student data
    for email, student in students.items():
        # Count activities for this student
        activity_count = sum(1 for activity in activities.values() if email in activity["participants"])
        writer.writerow([student["name"], student["email"], student["grade"], activity_count])
    
    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

