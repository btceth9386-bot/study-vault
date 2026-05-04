def compose_two(outer, inner):
    def composed(request, execute):
        def call_inner(req):
            return inner(req, execute)
        return outer(request, call_inner)
    return composed