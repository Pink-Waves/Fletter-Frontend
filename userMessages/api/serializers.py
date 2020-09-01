from rest_framework import serializers

from userMessages.models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        extra_kwargs = { 'subject': {'allow_blank': True}, 'body': {'allow_blank': True}}

    def create(self, validated_data):
        message = Message.objects.create(
            sender = self.validated_data['sender'],
            recipient = self.validated_data['recipient'],
            time = self.validated_data['time'],
            subject = self.validated_data['subject'],
            body = self.validated_data['body'],
            status = self.validated_data['status']
        )
        return message

