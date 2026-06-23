from django.db import models
from django.contrib.auth.models import User


class FrameworkBaseModel(models.Model):
  """
  Classe base que intercepta a injeção de propriedades dinâmicas (kwargs)
  e as redireciona automaticamente para os JSONFields usando os setters
  das @properties das classes filhas.
  """

  class Meta:
    abstract = True

  def __init__(self, *args, **kwargs):
    dynamic_kwargs = {}
    cls = self.__class__

    for key in list(kwargs.keys()):
      if hasattr(cls, key) and isinstance(getattr(cls, key), property):
        dynamic_kwargs[key] = kwargs.pop(key)

    super().__init__(*args, **kwargs)

    for key, value in dynamic_kwargs.items():
      setattr(self, key, value)


class BaseProfile(FrameworkBaseModel):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="%(class)s")
  metrics_data = models.JSONField(default=dict, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    abstract = True


class BaseTrackableEntity(FrameworkBaseModel):
  name = models.CharField(max_length=255, db_index=True)
  base_metrics = models.JSONField(default=dict, blank=True)

  class Meta:
    abstract = True


class BaseTrackingSession(FrameworkBaseModel):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(class)s_sessions")
  timestamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    abstract = True


class BaseTrackedItem(FrameworkBaseModel):
  quantity = models.DecimalField(max_digits=10, decimal_places=2)
  computed_metrics = models.JSONField(default=dict, blank=True)

  class Meta:
    abstract = True
