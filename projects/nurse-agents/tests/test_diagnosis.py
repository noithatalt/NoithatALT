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
