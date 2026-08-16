"""
Endpoints de Control y Sincronización en Tiempo Real para la Matriz Maestra de Proveedores — VideoPro
Permite que la tabla visual interactiva y el backend de VideoPro compartan el mismo estado exacto.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from app.core.providers import registry, health_checker

router = APIRouter(prefix="/api/v1/matrix", tags=["matrix"])


class ToggleRequest(BaseModel):
    provider_id: str
    enabled: bool


@router.get("/data", summary="Obtiene los datos completos y actualizados de la Matriz Maestra")
def get_matrix_data():
    """Retorna la lista completa de proveedores con sus estados en vivo y configuraciones."""
    try:
        data = registry.get_matrix_table_data()
        return {"status": "ok", "items": data}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/sync", summary="Sincroniza el estado completo enviado desde la tabla interactiva")
def sync_matrix(payload: Dict[str, Any] = Body(...)):
    """Guarda en disco y persiste en Firestore cualquier cambio de opciones, checkboxes o borrados."""
    try:
        items = payload.get("items", [])
        registry.sync_from_matrix_table(items)
        return {"status": "ok", "message": f"{len(items)} proveedores sincronizados con éxito."}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/toggle", summary="Habilita o deshabilita un proveedor específico")
def toggle_provider(req: ToggleRequest):
    """Alterna el estado activo de un motor para el Generador."""
    try:
        registry.set_provider_enabled(req.provider_id, req.enabled)
        return {"status": "ok", "provider_id": req.provider_id, "enabled": req.enabled}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.delete("/provider/{provider_id}", summary="Elimina permanentemente un proveedor de la matriz")
def delete_provider_endpoint(provider_id: str):
    """Elimina un proveedor de la matriz y de los selectores del generador."""
    try:
        ok = registry.delete_provider(provider_id)
        if ok:
            return {"status": "ok", "deleted": provider_id}
        else:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
