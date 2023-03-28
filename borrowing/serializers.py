import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from book.models import Book
from book.serializers import BookDetailSerializer
from borrowing.models import Borrowing
from user.serializers import CustomerSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(many=False, read_only=True)
    user = CustomerSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]

    def save(self, **kwargs):
        pass


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]
        read_only_fields = [
            "actual_return_date",
            "user",
        ]

    def create(self, validated_data):
        try:
            instance = super().create(validated_data)

            with transaction.atomic():
                book = get_object_or_404(Book, id=instance.book.id)

                if book.inventory == 0:
                    raise serializers.ValidationError(
                        "The book is out of stock"
                    )

                book.inventory -= 1
                book.save()
                instance.save()

                return instance

        except ValidationError as e:
            raise serializers.ValidationError(e.messages)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(required=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]
        read_only_fields = [
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
        ]

    def update(self, instance, validated_data):
        try:
            instance.actual_return_date = validated_data.get(
                "actual_return_date", instance.actual_return_date
            )

            with transaction.atomic():
                borrowing = get_object_or_404(Borrowing, id=instance.id)
                book = get_object_or_404(Book, id=instance.book.id)

                if borrowing.actual_return_date is not None:
                    raise serializers.ValidationError(
                        "The book has already been returned by user"
                    )

                book.inventory += 1
                book.save()
                instance.save()

                return instance

        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
