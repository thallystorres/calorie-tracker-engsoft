import logging
from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_content_service, get_content_repository
from .serializers import StudyContentCreateSerializer, StudyContentSerializer

logger = logging.getLogger(__name__)

class ContentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        service = get_content_service()
        query = request.query_params.get("q")
        contents = service.list_contents(query=query)

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(contents, request, view=self)
        serializer = StudyContentSerializer(page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    def post(self, request: Request) -> Response:
        service = get_content_service()
        serializer = StudyContentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        content = service.create_content(validated_data=validated_data)
        output = StudyContentSerializer(content)
        return Response(output.data, status=status.HTTP_201_CREATED)

class ContentSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = request.query_params.get("q", "")
        if not query:
            return Response([], status=status.HTTP_200_OK)

        from core.ai_engine.clients.gemini import GeminiLLMClient

        client = GeminiLLMClient()
        repo = get_content_repository()

        try:
            query_embedding = client.get_embedding(query, task_type="search_query")
            contents = repo.search_semantic(query_embedding, limit=10)
        except Exception as e:
            logger.warning("Busca semântica falhou, fallback para texto: %s", e)
            contents = repo.list_contents(query=query)[:10]

        data = [
            {
                "id": c.id,
                "name": c.name,
                "category": c.category,
                "difficulty_level": c.difficulty_level,
            }
            for c in contents
        ]
        return Response(data, status=status.HTTP_200_OK)

class ContentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, content_id: int) -> Response:
        service = get_content_service()
        content = service.get_content_or_404(content_id=content_id)
        serializer = StudyContentSerializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)
