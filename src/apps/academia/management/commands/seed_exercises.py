from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academia.models import Exercise
from core.ai.services import GeminiLLMClient

EXERCISES_DATA = [
    # --- CHEST (Peitoral) ---
    {
        "name": "Supino Reto com Barra",
        "muscle_group": "chest",
        "description": "Exercício composto clássico para ganho de volume e força no peitoral maior. Realizado deitado em um banco plano empurrando a barra para cima.",
    },
    {
        "name": "Supino Inclinado com Halteres",
        "muscle_group": "chest",
        "description": "Focado na porção clavicular (superior) do peitoral. O uso de halteres permite uma maior amplitude de movimento.",
    },
    {
        "name": "Crossover na Polia",
        "muscle_group": "chest",
        "description": "Exercício isolador realizado no cabo que mantém a tensão contínua no peitoral, excelente para hipertrofia e alongamento das fibras.",
    },
    # --- BACK (Costas) ---
    {
        "name": "Puxada Frontal na Polia",
        "muscle_group": "back",
        "description": "Movimento vertical que visa principalmente o grande dorsal (latíssimo do dorso), ajudando a desenvolver a largura das costas.",
    },
    {
        "name": "Remada Curvada com Barra",
        "muscle_group": "back",
        "description": "Exercício composto de puxada horizontal fundamental para o desenvolvimento da espessura e densidade das costas.",
    },
    {
        "name": "Barra Fixa (Pull-up)",
        "muscle_group": "back",
        "description": "Exercício calistênico de peso corporal que trabalha as costas de forma completa, com grande ênfase no latíssimo do dorso e bíceps sinergistas.",
    },
    # --- QUADS (Quadríceps) ---
    {
        "name": "Agachamento Livre com Barra",
        "muscle_group": "quads",
        "description": "O principal exercício construtor de força e hipertrofia para as pernas, com foco pesado nos quadríceps, glúteos e core.",
    },
    {
        "name": "Leg Press 45º",
        "muscle_group": "quads",
        "description": "Exercício de empurrar para membros inferiores feito em máquina, removendo a carga da lombar e focando no trabalho de força dos quadríceps.",
    },
    {
        "name": "Cadeira Extensora",
        "muscle_group": "quads",
        "description": "Exercício isolador excelente para focar exclusivamente nos músculos do quadríceps, promovendo o chamado 'pump' e finalização do treino.",
    },
    # --- HAMSTRINGS (Posteriores de Coxa) ---
    {
        "name": "Cadeira Flexora",
        "muscle_group": "hamstrings",
        "description": "Movimento isolado de flexão de joelho executado sentado, isolando perfeitamente a parte posterior da coxa.",
    },
    {
        "name": "Stiff com Barra",
        "muscle_group": "hamstrings",
        "description": "Exercício focado na extensão de quadril com joelhos semi-estendidos, trabalhando o alongamento profundo dos isquiotibiais e glúteos.",
    },
    {
        "name": "Mesa Flexora",
        "muscle_group": "hamstrings",
        "description": "Exercício de flexão de joelho realizado deitado, garantindo alta ativação nas fibras dos posteriores sem o auxílio do quadril.",
    },
    # --- SHOULDERS (Ombros) ---
    {
        "name": "Desenvolvimento com Halteres",
        "muscle_group": "shoulders",
        "description": "Exercício de empurrada vertical com foco principal na porção anterior e medial dos deltoides, essencial para ombros largos.",
    },
    {
        "name": "Elevação Lateral",
        "muscle_group": "shoulders",
        "description": "Movimento de abdução de ombro isolador, crucial para desenvolver a cabeça lateral (o 'cap') do deltoide.",
    },
    {
        "name": "Crucifixo Inverso na Máquina",
        "muscle_group": "shoulders",
        "description": "Isolador voltado para a porção posterior do ombro, frequentemente negligenciada, fundamental para a postura do atleta.",
    },
    # --- BICEPS (Bíceps) ---
    {
        "name": "Rosca Direta com Barra",
        "muscle_group": "biceps",
        "description": "O movimento mais clássico de flexão de cotovelo, construtor primário de força e massa para o bíceps braquial.",
    },
    {
        "name": "Rosca Martelo com Halteres",
        "muscle_group": "biceps",
        "description": "Executado com pegada neutra, foca no braquial e no braquiorradial, dando espessura ao braço e antebraço.",
    },
    {
        "name": "Rosca Scott",
        "muscle_group": "biceps",
        "description": "Exercício feito em um banco com suporte para os braços, removendo o roubo com o tronco e isolando completamente o bíceps.",
    },
    # --- TRICEPS (Tríceps) ---
    {
        "name": "Tríceps Pulley (Polia)",
        "muscle_group": "triceps",
        "description": "Extensão de cotovelo utilizando a polia alta, excelente para manter tensão contínua em todas as cabeças do tríceps.",
    },
    {
        "name": "Tríceps Testa com Barra W",
        "muscle_group": "triceps",
        "description": "Realizado deitado, é um poderoso construtor de massa que enfatiza bastante a cabeça longa do tríceps.",
    },
    {
        "name": "Tríceps Francês com Halter",
        "muscle_group": "triceps",
        "description": "Movimento *overhead* (acima da cabeça) que permite alongar o tríceps profundamente durante a fase excêntrica.",
    },
    # --- GLUTES (Glúteos) ---
    {
        "name": "Elevação Pélvica com Barra",
        "muscle_group": "glutes",
        "description": "Também chamado de Hip Thrust, é o rei dos exercícios para hipertrofia isolada da musculatura dos glúteos.",
    },
    {
        "name": "Agachamento Búlgaro",
        "muscle_group": "glutes",
        "description": "Variação unilateral de agachamento com um pé elevado atrás, foca massivamente no trabalho dos glúteos e quadríceps de cada perna individualmente.",
    },
    {
        "name": "Cadeira Abdutora",
        "muscle_group": "glutes",
        "description": "Máquina que trabalha a abdução do quadril, focando no glúteo médio e mínimo, responsáveis pela estabilização pélvica.",
    },
    # --- CALVES (Panturrilhas) ---
    {
        "name": "Elevação de Panturrilha em Pé",
        "muscle_group": "calves",
        "description": "Trabalha com os joelhos estendidos, o que ativa fortemente o músculo gastrocnêmio (a parte 'gêmea' da panturrilha).",
    },
    {
        "name": "Elevação de Panturrilha Sentado",
        "muscle_group": "calves",
        "description": "Com os joelhos flexionados, este exercício foca no músculo sóleo, uma parte mais profunda e muito forte da panturrilha.",
    },
    # --- ABS (Abdômen) ---
    {
        "name": "Crunch (Abdominal Tradicional)",
        "muscle_group": "abs",
        "description": "Flexão de tronco no solo que atinge diretamente o músculo reto abdominal (a região dos 'gominhos').",
    },
    {
        "name": "Prancha Isométrica",
        "muscle_group": "abs",
        "description": "Sustentação estática focada na resistência do *core*, estabilidade lombar e fortalecimento do músculo transverso abdominal.",
    },
    {
        "name": "Elevação de Pernas em Suspensão",
        "muscle_group": "abs",
        "description": "Pendurado em uma barra, o movimento de elevar as pernas trabalha fortemente a porção inferior do abdômen e os flexores do quadril.",
    },
]


class Command(BaseCommand):
    help = "Popula o catálogo de exercícios com embeddings vetoriais"

    def handle(self, *args, **options):
        client = GeminiLLMClient()
        created = 0

        with transaction.atomic():
            Exercise.objects.all().delete()

            for data in EXERCISES_DATA:
                embedding = client.get_embedding(
                    f"{data['name']}: {data['description']}",
                    task_type="search_document",
                )
                Exercise.objects.create(
                    name=data["name"],
                    muscle_group=data["muscle_group"],
                    description=data["description"],
                    embedding=embedding,
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created} exercícios criados com embeddings.")
        )
