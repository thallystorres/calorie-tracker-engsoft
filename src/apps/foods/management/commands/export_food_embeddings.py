import json
from django.core.management.base import BaseCommand
from apps.foods.models import Food

class Command(BaseCommand):
    help = "Exporta embeddings de alimentos para um arquivo JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="food_embeddings.json",
            help="Caminho do arquivo de saída (default: food_embeddings.json)",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        
        foods = Food.objects.filter(embedding__isnull=False).only(
            "name", "source", "outsource_fdc_id", "embedding"
        )
        
        total = foods.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("Nenhum alimento com embedding encontrado para exportar."))
            return

        self.stdout.write(f"Exportando {total} embeddings para {output_file}...")

        data = []
        for food in foods:
            embedding_list = None
            if food.embedding is not None:
                # Convert to standard Python floats to avoid JSON serialization errors with float32
                embedding_list = [float(x) for x in food.embedding]
            
            data.append({
                "name": food.name,
                "source": food.source,
                "outsource_fdc_id": food.outsource_fdc_id,
                "embedding": embedding_list
            })

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Exportação concluída com sucesso: {output_file}"))
