from fastapi.testclient import TestClient

from nurse_agents.main import app

client = TestClient(app)


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
