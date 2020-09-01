from rest_framework import serializers

from relationships.models import Relationship

class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'

    def create(self, validated_data):
        relationship = Relationship.objects.create(
            requester = self.validated_data['requester'],
            addressee = self.validated_data['addressee'],
            created_time = self.validated_data['created_time'],
            status = self.validated_data['status']
        )
        return relationship
