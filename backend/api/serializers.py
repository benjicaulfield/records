from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from processing.models import Record, Listing


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = "__all__"

class ListingSerializer(serializers.ModelSerializer):
    record = RecordSerializer()
    class Meta:
        model = Listing
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
