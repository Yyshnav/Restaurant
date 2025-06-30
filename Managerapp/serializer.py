
from Accountapp.models import BillTable, BranchTable, DiningTable, ManagerTable, PaymentTable, PrinterTable, SubSubCategoryTable
from Adminapp.serializer import BranchTableSerializer, OrderTableSerializer
from Userapp.serializer import OrderItemTableSerializer
from rest_framework import serializers

from Waiterapp.serializer import WaiterTableSerializer


class PaymentTableSerializer(serializers.ModelSerializer):
    order = OrderItemTableSerializer(read_only=True)

    class Meta:
        model = PaymentTable
        fields = '__all__'

class PrinterTableSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=BranchTable.objects.all())
    subsubcategories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SubSubCategoryTable.objects.all(),
        required=False
    )

    class Meta:
        model = PrinterTable
        fields = [
            'id',
            'name',
            'branch',
            'subsubcategories',
            'ip_address',
        ]

class ManagerTableSerializer(serializers.ModelSerializer):
    userid = serializers.LoginTableSerializer(read_only=True)

    class Meta:
        model = ManagerTable
        fields = [
            'id',
            'userid',
            'name',
            'phone',
            'image',
            'address',
            'idproof',
            'qualification',
            'created_at',
        ]

class DiningTableSerializer(serializers.ModelSerializer):
    branch = BranchTableSerializer()  # Nested branch details (read-only)

    class Meta:
        model = DiningTable
        fields = ['id', 'branch', 'floor', 'table_number', 'seating_capacity', 'is_available', 'created_at']

class BillTableSerializer(serializers.ModelSerializer):
    order = OrderTableSerializer(read_only=True)
    branch = BranchTableSerializer(read_only=True)
    table = DiningTableSerializer(read_only=True)
    waiter = WaiterTableSerializer(read_only=True)

    class Meta:
        model = BillTable
        fields = [
            'id',
            'order',
            'branch',
            'table',
            'waiter',
            'bill_number',
            'subtotal',
            'tax',
            'discount',
            'total_amount',
            'status',
            'payment_method',
            'paid_at',
            'created_at'
        ]