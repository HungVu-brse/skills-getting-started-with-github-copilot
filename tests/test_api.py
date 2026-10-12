from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_seeded_activity_data(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activity_data = response.json()
    assert "Soccer Team" in activity_data
    assert all("participants" in activity for activity in activity_data.values())
    assert all(
        "participant_phone_numbers" in activity
        for activity in activity_data.values()
    )


def test_signup_adds_participant_and_phone_number(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "new.student@mergington.edu"
    phone_number = "0123456789"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email, "phone_number": phone_number},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    updated_activity = client.get("/activities").json()[activity_name]
    assert email in updated_activity["participants"]
    assert updated_activity["participant_phone_numbers"][email] == phone_number


@pytest.mark.parametrize(
    "phone_number",
    ["1234567890", "012345678", "01234567890", "01234a6789"],
)
def test_signup_rejects_invalid_phone_number(client, phone_number):
    # Arrange
    activity_name = "Soccer Team"
    signup_params = {
        "email": "new.student@mergington.edu",
        "phone_number": phone_number,
    }

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=signup_params)

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Phone number must start with 0 and contain exactly 10 digits"
    )


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    signup_params = {
        "email": "new.student@mergington.edu",
        "phone_number": "0123456789",
    }

    # Act
    response = client.post("/activities/Unknown Club/signup", params=signup_params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    signup_params = {"email": email, "phone_number": "0123456789"}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=signup_params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_delete_removes_participant_and_returns_phone_number(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "student.to.remove@mergington.edu"
    phone_number = "0123456789"
    activity = activities[activity_name]
    activity["participants"].append(email)
    activity["participant_phone_numbers"][email] = phone_number

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}",
        "phone_number": phone_number,
    }
    assert email not in activity["participants"]
    assert email not in activity["participant_phone_numbers"]


def test_delete_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_returns_not_found_for_unregistered_participant(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_deleted_participant_can_be_restored_with_phone_number(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "student.to.restore@mergington.edu"
    phone_number = "0123456789"
    activity = activities[activity_name]
    activity["participants"].append(email)
    activity["participant_phone_numbers"][email] = phone_number

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    restore_response = client.post(
        f"/activities/{activity_name}/signup",
        params={
            "email": email,
            "phone_number": delete_response.json()["phone_number"],
        },
    )

    # Assert
    assert delete_response.status_code == 200
    assert restore_response.status_code == 200
    assert email in activity["participants"]
    assert activity["participant_phone_numbers"][email] == phone_number