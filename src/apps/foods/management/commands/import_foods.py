from django.core.management.base import BaseCommand
from apps.foods.models import Food
import os
import openfoodfacts


class Command(BaseCommand):
  help = 'Importa alimentos usando a SDK oficial do Open Food Facts'

  def handle(self, *args, **kwargs):
    self.stdout.write(self.style.SUCCESS("A iniciar a importação via SDK oficial..."))

    cookie_sessao = os.getenv("OFF_SESSION_COOKIE")

    api = openfoodfacts.API(
      user_agent="CalorAI_EngSoft_Project/1.0 (gustavo)",
      username=os.getenv("OFF_USERNAME"),
      password=os.getenv("OFF_PASSWORD"),
      session_cookie=cookie_sessao
    )

    termos_busca = ["arroz", "feijão", "frango", "leite", "pão", "ovo"]
    importados = 0

    for termo in termos_busca:
      self.stdout.write(f"A pesquisar por: {termo}...")

      try:


        resultados = api.product.text_search(termo)


        produtos = resultados.get("products", [])[:5]

        for item in produtos:

          nome = item.get('product_name_pt') or item.get('product_name')
          if not nome or 'nutriments' not in item:
            continue

          nutrientes = item['nutriments']
          kcal = nutrientes.get('energy-kcal_100g', 0)

          if kcal <= 0:
            continue

          proteina = nutrientes.get('proteins_100g', 0)
          carbos = nutrientes.get('carbohydrates_100g', 0)
          gordura = nutrientes.get('fat_100g', 0)
          fibra = nutrientes.get('fiber_100g', 0)

          allergens_tags = item.get('allergens_tags', [])
          alergios_limpos = [a.replace('en:', '').replace('pt:', '').lower() for a in allergens_tags]

          food, created = Food.objects.get_or_create(
            name=nome[:255],
            defaults={
              'kcal_per_100g': kcal,
              'protein_per_100g': proteina,
              'carbs_per_100g': carbos,
              'fat_per_100g': gordura,
              'fiber_per_100g': fibra,
              'source': 'api',
              'allergens': alergios_limpos
            }
          )
          if created:
            importados += 1

      except Exception as e:
        self.stdout.write(self.style.WARNING(f"Erro ao pesquisar '{termo}': {e}"))

    self.stdout.write(self.style.SUCCESS(f"Importação concluída! {importados} novos alimentos adicionados."))
