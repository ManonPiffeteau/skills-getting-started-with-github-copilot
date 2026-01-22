"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to original state before each test"""
    from app import activities
    
    original_activities = {
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
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Develop tennis skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Explore theatrical arts and perform in school productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu", "lucy@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create visual art including painting, drawing, and sculpture",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["nina@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills through organized debates",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on activities",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ryan@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_activity_contains_required_fields(self, client, reset_activities):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client, reset_activities):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds participant to the activity"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up an already registered participant fails"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_participants(self, client, reset_activities):
        """Test that multiple participants can sign up for the same activity"""
        client.post("/activities/Basketball/signup?email=student1@mergington.edu")
        client.post("/activities/Basketball/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 3  # alex + 2 new


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client, reset_activities):
        """Test successfully unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from the activity"""
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in participants
        assert len(participants) == 1
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-registered participant fails"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_and_signup_same_participant(self, client, reset_activities):
        """Test that a participant can unregister and sign up again"""
        # Unregister
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Verify unregistered
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]
        
        # Sign up again
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify registered again
        response = client.get("/activities")
        assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client, reset_activities):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
