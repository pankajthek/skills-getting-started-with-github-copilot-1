from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activities = app_module.activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Soccer Team/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Soccer Team"
    }
    assert email in app_module.activities["Soccer Team"]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "student@mergington.edu"
    app_module.activities["Soccer Team"]["participants"].append(email)

    # Act
    response = client.post(
        "/activities/Soccer Team/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert app_module.activities["Soccer Team"]["participants"].count(email) == 1


def test_unregister_removes_participant(client):
    # Arrange
    email = "student@mergington.edu"
    app_module.activities["Soccer Team"]["participants"].append(email)

    # Act
    response = client.delete(
        "/activities/Soccer Team/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Soccer Team"
    }
    assert email not in app_module.activities["Soccer Team"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_nonparticipant(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Soccer Team/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
