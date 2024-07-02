from rest_framework import serializers
from .models import *

class MedecinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medecin
        fields = ('id', 'email', 'username', 'password', 'specialite', 'first_name', 'last_name', 'is_staff')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Medecin.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            specialite=validated_data.get('specialite', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=validated_data.get('is_staff', False)
        )
        return user
    
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class TraitementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traitement
        fields = '__all__'

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'

class AntecedantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antecedants
        fields = '__all__'

class TraitementpatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traitement_Patient
        fields = '__all__'

class TraitementPatientidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traitement_Patient
        fields = ['Id_T']