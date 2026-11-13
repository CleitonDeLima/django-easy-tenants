def tenant_not_required(view_func):
    """Mark a view as accessible without an active tenant."""
    view_func.tenant_required = False
    return view_func
