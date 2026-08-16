"""
Contrato Base de Adaptador de Motor (Engine Adapter Interface) — VideoPro Studio
Garantiza que añadir un nuevo motor solo requiera implementar este adaptador sin tocar el resto del sistema.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.orchestration.job import JobStep


class BaseEngineAdapter(ABC):
    """Interfaz abstracta para todos los adaptadores de ejecución de motores."""

    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Identificador único del motor."""
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que los parámetros de entrada cumplan el contrato del motor."""
        pass

    @abstractmethod
    def execute(self, step: JobStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la tarea requerida y retorna el payload resultante.
        Debe registrar logs en step.log() y manejar excepciones controladas.
        """
        pass

    def check_health(self) -> str:
        """Comprueba el estado de salud del motor. Retorna 'ONLINE', 'DEGRADED' o 'OFFLINE'."""
        return "ONLINE"

    def cancel(self, step: JobStep):
        """Cancela una ejecución en curso si el motor lo soporta."""
        pass
