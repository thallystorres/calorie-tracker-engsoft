from django.db import models
from core.tracking.models import BaseCatalogItem

class StudyContent(BaseCatalogItem):
    class ContentSource(models.TextChoices):
        SYSTEM = "system", "Sistema"
        MANUAL = "manual", "Manual (Usuário)"

    class Category(models.TextChoices):
        EXATAS = "exatas", "Ciências Exatas"
        HUMANAS = "humanas", "Ciências Humanas"
        BIOLOGICAS = "biologicas", "Ciências Biológicas"
        TECH = "tech", "Tecnologia / TI"
        IDIOMAS = "idiomas", "Idiomas"
        OUTRO = "outro", "Outros"

    source = models.CharField(max_length=10, choices=ContentSource.choices, default=ContentSource.MANUAL)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OUTRO)
    difficulty_level = models.PositiveSmallIntegerField(
        default=1,
        help_text="Nível de dificuldade de 1 (Básico) a 5 (Avançado)"
    )

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
