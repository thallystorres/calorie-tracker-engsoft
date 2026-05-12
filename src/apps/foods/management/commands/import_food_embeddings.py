import json
from django.core.management.base import BaseCommand
from apps.foods.models import Food

class Command(BaseCommand):
    help = "Importa embeddings de alimentos a partir de um arquivo JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            type=str,
            default="food_embeddings.json",
            help="Caminho do arquivo de entrada (default: food_embeddings.json)",
        )

    def handle(self, *args, **options):
        input_file = options["input"]
        
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Arquivo não encontrado: {input_file}"))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Erro ao decodificar JSON em: {input_file}"))
            return

        total_in_file = len(data)
        self.stdout.write(f"Lidos {total_in_file} registros do arquivo.")

        updated_count = 0
        not_found_count = 0
        
        # Para otimizar, podemos carregar os alimentos em um dicionário para busca rápida
        # Mas se a base for muito grande, talvez seja melhor fazer por lotes.
        # Vamos assumir que cabe na memória por enquanto (alguns milhares de itens).
        
        for item in data:
            name = item.get("name")
            source = item.get("source")
            fdc_id = item.get("outsource_fdc_id")
            embedding = item.get("embedding")
            
            if not embedding:
                continue
                
            # Tenta encontrar o alimento
            filters = {"name": name, "source": source}
            if fdc_id is not None:
                filters["outsource_fdc_id"] = fdc_id
            
            # Usamos filter().first() para evitar erros se houver duplicados no banco
            food = Food.objects.filter(**filters).first()
            
            if food:
                food.embedding = embedding
                food.save(update_fields=["embedding"])
                updated_count += 1
            else:
                not_found_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importação concluída: {updated_count} atualizados, {not_found_count} não encontrados."
            )
        )
