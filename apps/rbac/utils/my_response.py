def my_jwt_response_payload_handler(token, user, request):
    return {
        "token": token,
        "username": user.username,
        "id": user.id,
        "role": user.role.all()[0].name
    }
