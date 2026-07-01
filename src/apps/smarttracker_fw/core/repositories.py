from typing import Generic, TypeVar

from django.db import models

T = TypeVar("T", bound=models.Model)


class BaseRepository(Generic[T]):
    def __init__(self, model_class: type[T]):
        self.model = model_class

    def get_by_id(self, id: int) -> T | None:
        return self.model.objects.filter(pk=id).first()

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def delete(self, instance: T) -> None:
        instance.delete()
