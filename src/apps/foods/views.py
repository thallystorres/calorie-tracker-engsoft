from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_food_service
from .serializers import FoodCreateSerializer, FoodSerializer


class FoodListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        service = get_food_service()
        query = request.query_params.get("q")
        foods = service.list_foods(query=query)

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(foods, request, view=self)
        serializer = FoodSerializer(page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    def post(self, request: Request) -> Response:
        service = get_food_service()
        serializer = FoodCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        food = service.create_food(validated_data=validated_data)
        output = FoodSerializer(food)
        return Response(output.data, status=status.HTTP_201_CREATED)


class FoodDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, food_id: int) -> Response:
        service = get_food_service()
        food = service.get_food_or_404(food_id=food_id)
        serializer = FoodSerializer(food)
        return Response(serializer.data, status=status.HTTP_200_OK)
