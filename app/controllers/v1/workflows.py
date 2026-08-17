"""
app/controllers/v1/workflows.py
Alias y re-exportación del router REST de Workflows en v1.
"""

from app.api.workflows import router

__all__ = ["router"]
