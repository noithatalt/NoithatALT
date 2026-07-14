from datetime import datetime

from fastapi.testclient import TestClient

from nurse_agents.main import app

client = TestClient(app)


_BASE_PAYLOAD = {
    "project_name": "base-project",
    "summary": "Base payload reused across multiple tests.",
    "target_user": "Test engineers",
    "mvp": "Basic endpoint testing",
}


def test_project_start_diagnosis() -> None:
    payload = {
        "project_name": "nurse-agents",
        "summary": "Du an giup nguoi moi nhin thay diem yeu va dung nen tang chac truoc khi mo rong.",
        "target_user": "Nguoi moi bat dau du an",
        "mvp": "Co health check, docs co ban va endpoint chan doan dau tien.",
    }

    response = client.post("/diagnosis/project-start", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "project_id" in body
    assert "foundation_score" in body
    assert body["risk_level"] in {"low", "medium", "high"}
    assert len(body["priority_actions"]) >= 1
    assert len(body["strengths"]) >= 1
    assert len(body["missing_foundations"]) >= 1
    assert body["honest_advice"]


def test_project_start_diagnosis_flags_scope_risk() -> None:
    payload = {
        "project_name": "super-app",
        "summary": "Day la mot nen tang day du lam tat ca moi viec cho moi nguoi.",
        "target_user": "Tat ca",
        "mvp": "Dang nhap thanh toan bao cao dashboard admin.",
    }

    response = client.post("/diagnosis/project-start", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] == "high"
    assert any("rong" in item or "qua nhieu" in item for item in body["weak_points"])


def test_get_diagnosis_success() -> None:
    """Test retrieving a diagnosis by project_id."""
    # First, create a diagnosis
    payload = {
        "project_name": "test-project",
        "summary": "A test project for diagnosis retrieval.",
        "target_user": "Test users",
        "mvp": "Basic MVP for testing",
    }

    create_response = client.post("/diagnosis/project-start", json=payload)
    assert create_response.status_code == 200
    create_body = create_response.json()
    project_id = create_body["project_id"]

    # Now retrieve it using the GET endpoint
    get_response = client.get(f"/diagnosis/{project_id}")

    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["project_id"] == project_id
    assert get_body["foundation_score"] == create_body["foundation_score"]
    assert get_body["risk_level"] == create_body["risk_level"]
    assert get_body["honest_advice"] == create_body["honest_advice"]
    assert get_body["priority_actions"] == create_body["priority_actions"]
    assert get_body["strengths"] == create_body["strengths"]
    assert get_body["weak_points"] == create_body["weak_points"]
    assert get_body["missing_foundations"] == create_body["missing_foundations"]


def test_get_diagnosis_not_found() -> None:
    """Test retrieving a diagnosis with non-existent project_id."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(f"/diagnosis/{non_existent_id}")

    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    assert "not found" in body["detail"].lower()


def test_list_diagnoses() -> None:
    """Test listing all stored diagnoses returns summaries."""
    payload = {
        "project_name": "list-test-project",
        "summary": "A project created to test the list endpoint behavior.",
        "target_user": "QA engineers testing the API",
        "mvp": "List endpoint returns correct summary fields",
    }
    create_response = client.post("/diagnosis/project-start", json=payload)
    assert create_response.status_code == 200
    project_id = create_response.json()["project_id"]

    response = client.get("/diagnosis")

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1

    ids = [item["project_id"] for item in body["items"]]
    assert project_id in ids

    matching = next(item for item in body["items"] if item["project_id"] == project_id)
    assert matching["project_name"] == "list-test-project"
    assert "foundation_score" in matching
    assert matching["risk_level"] in {"low", "medium", "high"}


def test_delete_diagnosis() -> None:
    """Test deleting a stored diagnosis removes it from storage."""
    payload = {
        "project_name": "delete-test-project",
        "summary": "A project created specifically to test the delete endpoint.",
        "target_user": "Developers verifying delete behavior",
        "mvp": "Delete removes the record and returns 204",
    }
    create_response = client.post("/diagnosis/project-start", json=payload)
    assert create_response.status_code == 200
    project_id = create_response.json()["project_id"]

    delete_response = client.delete(f"/diagnosis/{project_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/diagnosis/{project_id}")
    assert get_response.status_code == 404


def test_delete_diagnosis_not_found() -> None:
    """Test deleting a non-existent project_id returns 404."""
    response = client.delete("/diagnosis/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    body = response.json()
    assert "not found" in body["detail"].lower()


def test_validation_error_format() -> None:
    """Test that validation errors return consistent ErrorResponseWrapper format."""
    response = client.post("/diagnosis/project-start", json={"project_name": "x"})

    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
    assert len(body["error"]["details"]) > 0
    detail = body["error"]["details"][0]
    assert "field" in detail
    assert "message" in detail


def test_timestamps_in_diagnosis_response() -> None:
    """Test that created_at and updated_at are present and valid ISO-8601 timestamps."""
    response = client.post("/diagnosis/project-start", json=_BASE_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert "created_at" in body
    assert "updated_at" in body
    created_at = datetime.fromisoformat(body["created_at"])
    updated_at = datetime.fromisoformat(body["updated_at"])
    assert created_at == updated_at


def test_timestamps_in_list_response() -> None:
    """Test that list endpoint includes timestamps in each summary item."""
    client.post("/diagnosis/project-start", json=_BASE_PAYLOAD)
    response = client.get("/diagnosis")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    item = body["items"][0]
    assert "created_at" in item
    assert "updated_at" in item
    datetime.fromisoformat(item["created_at"])


def test_list_pagination_limit() -> None:
    """Test that limit query param restricts returned items while total stays accurate."""
    for i in range(3):
        client.post("/diagnosis/project-start", json={**_BASE_PAYLOAD, "project_name": f"page-project-{i}"})

    response = client.get("/diagnosis?limit=2&offset=0")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total"] >= 3


def test_list_pagination_offset() -> None:
    """Test that offset skips the correct number of items."""
    for i in range(3):
        client.post("/diagnosis/project-start", json={**_BASE_PAYLOAD, "project_name": f"offset-project-{i}"})

    all_response = client.get("/diagnosis?limit=100&offset=0")
    all_ids = [item["project_id"] for item in all_response.json()["items"]]

    offset_response = client.get("/diagnosis?limit=1&offset=1")
    offset_ids = [item["project_id"] for item in offset_response.json()["items"]]
    assert offset_ids[0] == all_ids[1]


def test_put_diagnosis_updates_fields() -> None:
    """Test that PUT re-runs diagnosis and updates fields, preserving created_at."""
    create_response = client.post("/diagnosis/project-start", json=_BASE_PAYLOAD)
    assert create_response.status_code == 200
    project_id = create_response.json()["project_id"]
    original_created_at = create_response.json()["created_at"]

    new_payload = {
        "project_name": "updated-project",
        "summary": "Completely new focused summary for a lean startup with one target user.",
        "target_user": "Solo founders",
        "mvp": "Single landing page",
    }
    put_response = client.put(f"/diagnosis/{project_id}", json=new_payload)
    assert put_response.status_code == 200
    put_body = put_response.json()
    assert put_body["project_id"] == project_id
    assert put_body["created_at"] == original_created_at
    assert "updated_at" in put_body


def test_put_diagnosis_not_found() -> None:
    """Test that PUT on unknown project_id returns 404."""
    response = client.put("/diagnosis/00000000-0000-0000-0000-000000000000", json=_BASE_PAYLOAD)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
