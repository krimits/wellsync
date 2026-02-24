import pytest
import asyncio
from backend.events.event_types import WellnessEvent, EventType
from backend.events.queue import get_event_queue
from backend.events.gateway import EventGateway


def test_wellness_event_creation():
    event = WellnessEvent(type=EventType.MORNING_RECOMMENDATION)
    assert event.type == EventType.MORNING_RECOMMENDATION
    assert event.user_ids == []


def test_wellness_event_specific_users():
    event = WellnessEvent(type=EventType.MORNING_RECOMMENDATION, user_ids=[1, 2, 3])
    assert event.user_ids == [1, 2, 3]


def test_gateway_register_and_get():
    gateway = EventGateway()
    async def dummy_handler(event, **kwargs): pass
    gateway.register(EventType.MORNING_RECOMMENDATION, dummy_handler)
    handler = gateway.get_handler(EventType.MORNING_RECOMMENDATION)
    assert handler is dummy_handler


def test_gateway_missing_handler():
    gateway = EventGateway()
    with pytest.raises(ValueError):
        gateway.get_handler(EventType.MORNING_RECOMMENDATION)


@pytest.mark.asyncio
async def test_queue_put_and_get():
    queue = asyncio.Queue()
    event = WellnessEvent(type=EventType.MORNING_RECOMMENDATION)
    await queue.put(event)
    result = await queue.get()
    assert result.type == EventType.MORNING_RECOMMENDATION


@pytest.mark.asyncio
async def test_gateway_dispatch():
    gateway = EventGateway()
    results = []
    async def mock_handler(event, **kwargs):
        results.append(event.type)
    gateway.register(EventType.EVENING_SUMMARY, mock_handler)
    event = WellnessEvent(type=EventType.EVENING_SUMMARY)
    await gateway.dispatch(event)
    assert results == [EventType.EVENING_SUMMARY]
