token = request.headers.get("Authorization").replace("Bearer ", "")
introspection = await auth_server.introspect_token(token)

if not introspection.active:
    raise Unauthorized("Invalid token")