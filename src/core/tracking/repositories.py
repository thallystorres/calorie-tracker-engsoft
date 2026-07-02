from typing import Any, Generic, TypeVar

from django.contrib.auth.models import User
from django.db import models

E = TypeVar("E", bound=models.Model)
I = TypeVar("I", bound=models.Model)


class BaseTrackerRepository(Generic[E, I]):
    def __init__(self, event_model: type[E], item_model: type[I]):
        self.event_model = event_model
        self.item_model = item_model

    def create_event(self, user: User, **event_data) -> E:
        return self.event_model.objects.create(user=user, **event_data)

    def create_items(self, event: E, items_data: list[dict[str, Any]]) -> list[I]:
        items = [self.item_model(event=event, **data) for data in items_data]
        return self.item_model.objects.bulk_create(items)
