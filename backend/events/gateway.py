from typing import Callable, Dict
from backend.events.event_types import EventType, WellnessEvent


class EventGateway:
    def __init__(self) -> None:
        self._routes: Dict[EventType, Callable] = {}

    def register(self, event_type: EventType, handler: Callable) -> None:
        self._routes[event_type] = handler

    def get_handler(self, event_type: EventType) -> Callable:
        handler = self._routes.get(event_type)
        if handler is None:
            raise ValueError(f"No handler registered for event type: {event_type}")
        return handler

    async def dispatch(self, event: WellnessEvent, **kwargs) -> None:
        handler = self.get_handler(event.type)
        await handler(event, **kwargs)
