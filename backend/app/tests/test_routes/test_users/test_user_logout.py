
# Teste para a rota de logout
def test_logout(client):
    # Chama a rota de logout
    response = client.post("/logout/")

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json() == {"message": "Logout realizado com sucesso"}

    # Verifica se o cookie de acesso foi removido
    assert "access_token" not in response.cookies