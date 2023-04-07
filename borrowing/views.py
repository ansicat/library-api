from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from library_service.services import borrowing_send_notification


class BorrowingPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user").order_by(
        "-borrow_date", "-id"
    )
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = BorrowingPagination

    def get_queryset(self):
        def to_bool(value: str, default=None) -> bool:
            valid_values = {
                "True": True,
                "False": False,
                "true": True,
                "false": False,
            }

            return valid_values.get(value, default)

        queryset = self.queryset

        """Filters for list of borrowings"""
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        is_active = to_bool(self.request.query_params.get("is_active", ""))
        if is_active is not None:
            queryset = queryset.filter(actual_return_date__isnull=is_active)

        user_id = self.request.query_params.get("user_id", "")
        if user_id.isdigit() and self.request.user.is_staff:
            queryset = queryset.filter(user_id=int(user_id))

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "return_book":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        # send notification to Telegram Bot
        borrowing_id = serializer.data["id"]
        borrow_date = serializer.validated_data["borrow_date"]
        book_title = serializer.validated_data["book"].title
        user_name = self.request.user.full_name

        borrowing_send_notification(
            f"{borrow_date}: {book_title} was borrowed by "
            f"{user_name} (id={borrowing_id})"
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        url_name="return",
    )
    def return_book(self, request, pk=None):
        """Endpoint for return borrowing of book"""
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        # send notification to Telegram Bot
        borrowing_id = borrowing.id
        actual_return_date = serializer.validated_data["actual_return_date"]
        book_title = borrowing.book.title
        user_name = self.request.user.full_name

        borrowing_send_notification(
            f"{actual_return_date}: {book_title} was returned by "
            f"{user_name} (id={borrowing_id})"
        )

        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description=(
                    "Filter by state of borrowed book (ex. ?is_active=true)"
                ),
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description=(
                    "Filter by user id (for admins only) (ex. ?user_id=1)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
