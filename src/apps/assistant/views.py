import json
from typing import TYPE_CHECKING, cast

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.profiles.models import SavedDiet, SavedRecipe


from .services import DietAssistantService

if TYPE_CHECKING:
    from django.contrib.auth.models import User


@login_required
def chat_page(request):
    return render(request, "assistant/chat.html")


class DietAssistantChatAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        user_message = str(request.data.get("message", "")).strip()
        user = cast("User", request.user)
        service = DietAssistantService()

        try:
          ai_reply_data = service.generate_diet_suggestion(
            user=request.user,
            user_message=user_message
          )

          # Retorna o texto e o tipo como JSON para o Frontend
          return Response({
            "reply": ai_reply_data["texto"],
            "type": ai_reply_data["tipo"]
          }, status=status.HTTP_200_OK)

        except Exception as e:
          return Response(
            {"detail": f"Erro na IA: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )


class SaveAIContentAPIView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request: Request) -> Response:
    tipo = request.data.get("type")
    conteudo = request.data.get("content")

    if not conteudo:
      return Response({"error": "Nenhum conteúdo enviado."}, status=status.HTTP_400_BAD_REQUEST)

    try:
      if tipo == "dieta":
        SavedDiet.objects.create(user=request.user, content=conteudo)
      elif tipo == "receita":
        SavedRecipe.objects.create(user=request.user, content=conteudo)
      else:
        return Response({"error": "Tipo inválido."}, status=status.HTTP_400_BAD_REQUEST)

      return Response({"status": "success", "message": "Salvo com sucesso!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def saved_items_page(request):
  # Pega as dietas e receitas do usuário logado, ordenando da mais recente para a mais antiga
  dietas = SavedDiet.objects.filter(user=request.user).order_by('-created_at')
  receitas = SavedRecipe.objects.filter(user=request.user).order_by('-created_at')

  context = {
    'dietas': dietas,
    'receitas': receitas
  }
  return render(request, "assistant/saved_items.html", context)
@login_required
@require_POST
def delete_saved_item(request):
    # Usamos request.POST para ler os dados do formulário HTML
    item_id = request.POST.get("id")
    item_type = request.POST.get("type")

    if item_type == "dieta":
        item = get_object_or_404(SavedDiet, id=item_id, user=request.user)
        item.delete()
    elif item_type == "receita":
        item = get_object_or_404(SavedRecipe, id=item_id, user=request.user)
        item.delete()

    # Após apagar do banco de dados, o Django recarrega a página de salvos
    return redirect('assistant:saved-items')


@login_required
@require_POST
def edit_saved_item_with_ai(request):
  # Lendo do formulário tradicional HTML
  item_id = request.POST.get("id")
  item_type = request.POST.get("type")
  instrucao = request.POST.get("instruction")

  if not instrucao:
    return redirect('assistant:saved-items')

  try:
    if item_type == "dieta":
      item = get_object_or_404(SavedDiet, id=item_id, user=request.user)
    elif item_type == "receita":
      item = get_object_or_404(SavedRecipe, id=item_id, user=request.user)
    else:
      return redirect('assistant:saved-items')

    service = DietAssistantService()
    novo_conteudo = service.edit_content_with_ai(current_content=item.content, instruction=instrucao)

    item.content = novo_conteudo
    item.save()

  except Exception as e:
    print(f"Erro na edição por IA: {e}")

  return redirect('assistant:saved-items')
