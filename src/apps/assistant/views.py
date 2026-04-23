from typing import TYPE_CHECKING, cast

from django.contrib.auth.decorators import login_required
import re
from django.utils import timezone

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
            user=user,
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
    titulo_enviado = request.data.get("title")

    if not conteudo:
      return Response({"error": "Nenhum conteúdo enviado."}, status=status.HTTP_400_BAD_REQUEST)

    # Cast para garantir que os tipos estáticos fiquem felizes
    user = cast("User", request.user)
    conteudo_str = str(conteudo)

    titulo_dinamico = ""

    # 1. Se o frontend enviou um título específico, usamos ele
    if titulo_enviado:
      titulo_dinamico = str(titulo_enviado).strip()[:255]

    # 2. Se não, tentamos extrair do próprio conteúdo em Markdown
    if not titulo_dinamico:
      match = re.search(r'^(#+)\s*(.+)', conteudo_str, re.MULTILINE)
      if match:
        matched_str = str(match.group(2))
        titulo_dinamico = matched_str.replace('*', '').strip()[:255]

    # 3. Fallback dinâmico usando o nome do usuário, o tipo e a data atual
    if not titulo_dinamico:
      data_atual = timezone.localtime().strftime("%d/%m/%Y %H:%M")
      nome_usuario = getattr(user, 'first_name', '') or getattr(user, 'username', 'Usuário')

      if tipo == "dieta":
        titulo_dinamico = f"Plano Alimentar de {nome_usuario} - {data_atual}"
      elif tipo == "receita":
        titulo_dinamico = f"Receita de {nome_usuario} - {data_atual}"
      else:
        titulo_dinamico = f"Conteúdo Salvo - {data_atual}"

    # ------------------------------------------

    try:
      if tipo == "dieta":
        SavedDiet.objects.create(user=user, title=titulo_dinamico, content=conteudo_str)
      elif tipo == "receita":
        SavedRecipe.objects.create(user=user, title=titulo_dinamico, content=conteudo_str)
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


@login_required
def shopping_list_page(request):
  lista_markdown = None

  # 1. Busca todos os itens para exibir as opções (checkboxes)
  dietas = SavedDiet.objects.filter(user=request.user).order_by('-created_at')
  receitas = SavedRecipe.objects.filter(user=request.user).order_by('-created_at')

  if request.method == "POST":
    # 2. Pega as listas de IDs que o utilizador marcou no HTML
    dietas_selecionadas = request.POST.getlist('dietas_selecionadas')
    receitas_selecionadas = request.POST.getlist('receitas_selecionadas')

    # 3. Filtra no banco de dados APENAS os conteúdos marcados
    conteudos_dietas = SavedDiet.objects.filter(
      id__in=dietas_selecionadas, user=request.user
    ).values_list('content', flat=True)

    conteudos_receitas = SavedRecipe.objects.filter(
      id__in=receitas_selecionadas, user=request.user
    ).values_list('content', flat=True)

    todos_conteudos = list(conteudos_dietas) + list(conteudos_receitas)

    # 4. Envia para a IA apenas se houver algo selecionado
    if todos_conteudos:
      service = DietAssistantService()
      lista_markdown = service.generate_shopping_list(todos_conteudos)
    else:
      lista_markdown = "⚠️ Por favor, selecione pelo menos uma dieta ou receita para gerar a lista."

  context = {
    "dietas": dietas,
    "receitas": receitas,
    "lista_markdown": lista_markdown
  }

  return render(request, "assistant/shopping_list.html", context)
