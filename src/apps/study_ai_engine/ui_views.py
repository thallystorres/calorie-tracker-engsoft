from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .dependencies import get_quiz_generator_service, get_flashcard_generator_service

@require_http_methods(["GET"])
@login_required
def hub_page(request):
    return render(request, "study_ai_engine/hub.html")

@require_http_methods(["POST"])
@login_required
def generate_quiz(request):
    topic = request.POST.get("topic")
    service = get_quiz_generator_service()

    try:
        # A IA devolve o Pydantic model parseado num dict
        result = service.generate(user=request.user, user_prompt=topic)
        return render(request, "study_ai_engine/partials/quiz_result.html", {"quiz": result})
    except Exception as e:
        return render(request, "study_ai_engine/partials/error.html", {"error": str(e)})

@require_http_methods(["POST"])
@login_required
def generate_flashcards(request):
    topic = request.POST.get("topic")
    service = get_flashcard_generator_service()

    try:
        result = service.generate(user=request.user, user_prompt=topic)
        return render(request, "study_ai_engine/partials/flashcards_result.html", {"deck": result})
    except Exception as e:
        return render(request, "study_ai_engine/partials/error.html", {"error": str(e)})
