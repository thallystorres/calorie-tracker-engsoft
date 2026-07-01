from django.db import models
from pgvector.django import VectorField


class BaseCatalogItem(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    embedding = VectorField(dimensions=3072, null=True, blank=True)

    class Meta:
        abstract = True


class BaseTrackedEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseTrackedItem(models.Model):
    class Meta:
        abstract = True

    def get_metric(self):
        raise NotImplementedError("Subclasses must implement get_metric()")


class BaseAIGeneratedContent(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Conteúdo em Markdown gerado pela IA")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
