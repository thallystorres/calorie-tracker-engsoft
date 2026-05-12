import concurrent.futures

from django.core.management.base import BaseCommand

from apps.ai_engine.dependencies import get_gemini_client
from apps.foods.models import Food


class Command(BaseCommand):
    help = "Gera embeddings para alimentos que ainda não possuem (com concorrência)."

    def handle(self, *args, **options):
        client = get_gemini_client()
        foods_without_embedding = Food.objects.filter(embedding__isnull=True)

        total = foods_without_embedding.count()
        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("Todos os alimentos já possuem embeddings.")
            )
            return

        self.stdout.write(
            f"Iniciando processamento de {total} alimentos com concorrência..."
        )

        # Função de processamento para cada alimento
        def process_food(food_id):
            try:
                # Recupera o objeto do banco para evitar problemas de thread safety com objetos compartilhados
                food = Food.objects.get(id=food_id)
                doc_text = f"title: {food.name} | text: {food.name}"

                result = client.client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=doc_text,
                )

                food.embedding = result.embeddings[0].values
                food.save(update_fields=["embedding"])
                return True, food.name
            except Exception as e:
                return False, f"{food_id}: {str(e)}"

        # Usando ThreadPoolExecutor para paralelismo I/O
        # Limitamos a 10 threads para não estourar rate limits da API rapidamente
        max_workers = 10
        food_ids = list(foods_without_embedding.values_list("id", flat=True))

        success_count = 0
        error_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_food = {
                executor.submit(process_food, fid): fid for fid in food_ids
            }

            for i, future in enumerate(
                concurrent.futures.as_completed(future_to_food), 1
            ):
                success, message = future.result()
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    self.stderr.write(f"Erro: {message}")

                if i % 20 == 0 or i == total:
                    self.stdout.write(
                        f"Progresso: {i}/{total} (Sucessos: {success_count}, Erros: {error_count})"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído! {success_count} alimentos atualizados, {error_count} erros."
            )
        )
