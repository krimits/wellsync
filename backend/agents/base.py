from abc import ABC, abstractmethod
from backend.events.event_types import WellnessEvent


class BaseAgent(ABC):
    @abstractmethod
    async def handle(self, event: WellnessEvent, **kwargs) -> None:
        ...
