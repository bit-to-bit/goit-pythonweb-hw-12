def test_create_contact(client, mock_redis, get_token):
    response = client.post(
        "/api/contacts/",
        json={
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email@mail.com",
            "phone": "+380501122333",
            "birthday": "2000-01-01",
            "note": "Note test text",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "email@mail.com"
    assert "id" in data


# def test_get_tag(client, get_token):
#     response = client.get(
#         "/api/tags/1", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["name"] == "test_tag"
#     assert "id" in data


# def test_get_tag_not_found(client, get_token):
#     response = client.get(
#         "/api/tags/2", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Tag not found"


# def test_get_tags(client, get_token):
#     response = client.get("/api/tags", headers={"Authorization": f"Bearer {get_token}"})
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, list)
#     assert data[0]["name"] == "test_tag"
#     assert "id" in data[0]


# def test_update_tag(client, get_token):
#     response = client.put(
#         "/api/tags/1",
#         json={"name": "new_test_tag"},
#         headers={"Authorization": f"Bearer {get_token}"},
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["name"] == "new_test_tag"
#     assert "id" in data


# def test_update_tag_not_found(client, get_token):
#     response = client.put(
#         "/api/tags/2",
#         json={"name": "new_test_tag"},
#         headers={"Authorization": f"Bearer {get_token}"},
#     )
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Tag not found"


# def test_delete_tag(client, get_token):
#     response = client.delete(
#         "/api/tags/1", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["name"] == "new_test_tag"
#     assert "id" in data


# def test_repeat_delete_tag(client, get_token):
#     response = client.delete(
#         "/api/tags/1", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Tag not found"
