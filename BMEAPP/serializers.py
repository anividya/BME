from rest_framework import serializers
from .models import Workbook

class WorkbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workbook
        fields = '__all__'

from .models import Gatepass

class GatepassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gatepass
        fields = '__all__'  # Specify the fields you want to serialize
