from rest_framework import serializers

from Accountapp.models import *

class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonTable
        fields = [
            'id',
            'item',
            'name',
            'description',
            'image',
            'price',
            'created_at',
            'updated_at',
        ]

class ItemSerializer(serializers.ModelSerializer):
    addons = AddonSerializer(many=True, read_only=True)

    class Meta:
        model = ItemTable
        fields = [
            'id',
            'name',
            'category',
            'subcategory',
            'type',
            'image',
            'description',
            'voice_description',
            'price',
            'quantity',
            'created_at',
            'updated_at',
            'fast_delivery',
            'newest',
            'addons',
        ]


class SubCategorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = SubCategoryTable
        fields = [
            'id',
            'category',
            'name',
            'created_at',
            'updated_at',
            'items',
        ]


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    items = ItemSerializer(many=True, read_only=True)  # Optional: all items under this category

    class Meta:
        model = CategoryTable
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
            'subcategories',
            'items',
        ]

# class ItemBriefSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ItemTable
#         fields = ['id', 'name', 'price']


class OfferTableSerializer(serializers.ModelSerializer):
    itemid = ItemSerializer(read_only=True)

    class Meta:
        model = OfferTable
        fields = [
            'id',
            'name',
            'startdate',
            'enddate',
            'offer_percentage',
            'itemid',
            'offerdescription',
            'createdat',
            'updatedat',
        ]
