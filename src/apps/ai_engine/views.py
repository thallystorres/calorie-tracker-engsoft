import json
import logging
import re
from typing import cast

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.dependencies import get_profile_repository
from apps.profiles.models import SavedDiet, SavedRecipe, WeeklyPlan

from .dependencies import (
    get_diet_assistant_service,
    get_meal_suggester_service,
    get_shopping_list_service,
    get_weekly_planner_service,
)
from .exceptions import LLMRequestError, LLMResponseError

logger = logging.getLogger(__name__)


class WeeklyPlannerChatAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        user_message = str(request.data.get("message", "")).strip()
        user = cast("User", request.user)
        service = get_weekly_planner_service()

        ai_reply_data = service.generate_weekly_plan(
            user=user, user_message=user_message
        )
        return Response(ai_reply_data, status=status.HTTP_200_OK)


class SuggestMealView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user_prompt = request.data.get("user_prompt", "")
        user = cast("User", request.user)

        service = get_meal_suggester_service()

        suggestion = service.suggest_meal(
            user=user, user_prompt=str(user_prompt).strip()
        )

        return Response(suggestion.model_dump(), status=status.HTTP_200_OK)


@login_required
def chat_page(request):
    return render(request, "ai_engine/chat.html")


class DietAssistantChatAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        user_message = str(request.data.get("message", "")).strip()
        user = cast("User", request.user)
        service = get_diet_assistant_service()

        ai_reply_data = service.generate_diet_suggestion(
            user=user, user_message=user_message
        )

        return Response(
            {"reply": ai_reply_data["texto"], "type": ai_reply_data["tipo"]},
            status=status.HTTP_200_OK,
        )


class SaveAIContentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        profile_repo = get_profile_repository()

        tipo = request.data.get("type", "")
        conteudo = request.data.get("content", "")
        titulo_enviado = request.data.get("title", "")

        if not conteudo:
            return Response(
                {"error": "Nenhum conteúdo enviado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = cast("User", request.user)
        conteudo_str = str(conteudo)

        titulo_dinamico = ""

        if titulo_enviado:
            titulo_dinamico = str(titulo_enviado).strip()[:255]

        if not titulo_dinamico:
            match = re.search(r"^(#+)\s*(.+)", conteudo_str, re.MULTILINE)
            if match:
                matched_str = str(match.group(2))
                titulo_dinamico = matched_str.replace("*", "").strip()[:255]

        if not titulo_dinamico:
            data_atual = timezone.localtime().strftime("%d/%m/%Y %H:%M")
            nome_usuario = getattr(user, "first_name", "") or getattr(
                user, "username", "Usuário"
            )

            if tipo == "dieta":
                titulo_dinamico = f"Plano Alimentar de {nome_usuario} - {data_atual}"
            elif tipo == "receita":
                titulo_dinamico = f"Receita de {nome_usuario} - {data_atual}"
            elif tipo == "plano_semanal":
                titulo_dinamico = f"Plano Semanal de {nome_usuario} - {data_atual}"
            else:
                titulo_dinamico = f"Conteúdo Salvo - {data_atual}"

        if tipo == "dieta":
            profile_repo.create_diet(user, titulo_dinamico, conteudo_str)
        elif tipo == "receita":
            profile_repo.create_recipe(user, titulo_dinamico, conteudo_str)
        elif tipo == "plano_semanal":
            try:
                plan_data = json.loads(conteudo_str)
            except json.JSONDecodeError:
                return Response(
                    {"error": "Conteúdo do plano semanal não é um JSON válido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            target_kcal = plan_data.get("weekly_average_kcal")
            profile_repo.create_weekly_plan(user, titulo_dinamico, plan_data, target_kcal=target_kcal)
        else:
            return Response(
                {"error": "Tipo inválido."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"status": "success", "message": "Salvo com sucesso!"},
            status=status.HTTP_201_CREATED,
        )


@login_required
def saved_items_page(request):
    repo = get_profile_repository()
    dietas = repo.list_diets(request.user)
    receitas = repo.list_recipes(request.user)
    planos_semanais = repo.list_weekly_plans(request.user)

    context = {
        "dietas": dietas,
        "receitas": receitas,
        "planos_semanais": planos_semanais,
    }
    return render(request, "ai_engine/saved_items.html", context)


@login_required
@require_POST
def delete_saved_item(request):
    item_id = request.POST.get("id")
    item_type = request.POST.get("type")

    if item_type == "dieta":
        item = get_object_or_404(SavedDiet, id=item_id, user=request.user)
        item.delete()
    elif item_type == "receita":
        item = get_object_or_404(SavedRecipe, id=item_id, user=request.user)
        item.delete()
    elif item_type == "plano_semanal":
        item = get_object_or_404(WeeklyPlan, id=item_id, user=request.user)
        item.delete()

    return redirect("ai-ui:saved-items")


@login_required
@require_POST
def edit_saved_item_with_ai(request):
    item_id = request.POST.get("id")
    item_type = request.POST.get("type")
    instrucao = request.POST.get("instruction")

    if not instrucao:
        return redirect("ai-ui:saved-items")

    try:
        if item_type == "dieta":
            item = get_object_or_404(SavedDiet, id=item_id, user=request.user)
        elif item_type == "receita":
            item = get_object_or_404(SavedRecipe, id=item_id, user=request.user)
        else:
            return redirect("ai-ui:saved-items")

        service = get_diet_assistant_service()
        novo_conteudo = service.edit_content_with_ai(
            current_content=item.content, instruction=instrucao
        )

        item.content = novo_conteudo
        item.save()

    except (LLMRequestError, LLMResponseError):
        logger.exception("Erro na edicao por IA user_pk=%s", request.user.pk)
    except Exception:
        logger.exception(
            "Erro inesperado na edicao por IA user_pk=%s", request.user.pk,
        )

    return redirect("ai-ui:saved-items")


@login_required
def shopping_list_page(request):
    lista_markdown = None
    repo = get_profile_repository()

    dietas = repo.list_diets(request.user)
    receitas = repo.list_recipes(request.user)

    if request.method == "POST":
        dietas_selecionadas = request.POST.getlist("dietas_selecionadas")
        receitas_selecionadas = request.POST.getlist("receitas_selecionadas")

        conteudos_dietas = (
            repo.list_diets_from_id_list(request.user, dietas_selecionadas) or []
        )

        conteudos_receitas = (
            repo.list_recipes_from_id_list(request.user, receitas_selecionadas) or []
        )

        todos_conteudos = list(conteudos_dietas) + list(conteudos_receitas)

        if todos_conteudos:
            service = get_shopping_list_service()
            lista_markdown = service.generate_shopping_list(todos_conteudos)
        else:
            lista_markdown = "⚠️ Por favor, selecione pelo menos uma dieta ou receita para gerar a lista."

    context = {"dietas": dietas, "receitas": receitas, "lista_markdown": lista_markdown}

    return render(request, "ai_engine/shopping_list.html", context)
