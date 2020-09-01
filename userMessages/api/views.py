from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q
from .serializers import MessageSerializer
from userMessages.models import Message
from accounts.models import ExtendedUser
from relationships.models import Relationship
from datetime import datetime, timedelta
from django.conf import settings
from math import radians, cos, sin, asin, sqrt 

class MessageAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        def time(state1, state2):
            # converting coords into radians
            state1_lat = radians(settings.STATE_COORDS[state1][0])
            state1_long = radians(settings.STATE_COORDS[state1][1])
            state2_lat = radians(settings.STATE_COORDS[state2][0])
            state2_long = radians(settings.STATE_COORDS[state2][1])
            # haversine formula (spherical trig)
            radius_miles = 3956
            dist_lat = state2_lat - state1_lat
            dist_long = state2_long - state1_long
            a = sin(dist_lat / 2) ** 2 + cos(state1_lat) * cos(state2_lat) * sin(dist_long / 2) ** 2
            b = 2 * asin(sqrt(a))
            distance = b * radius_miles
            # calculating mail delivery time based on distance in miles
            if distance < 550:
                return 1
            elif 550 <= distance < 1000:
                return 2
            elif 1000 <= distance < 2000:
                return 3
            else:
                return 4
        modified_data = request.data
        if 'sender' not in request.data.keys():
            user = request.user
            modified_data['sender'] = user.id

        try:
            modified_data['recipient'] = ExtendedUser.objects.get(username=request.data['recipient']).id
        except:
            return Response({"username": "Sorry! We cannot find any account associated with this username!"}) 

        situation1 = Q(addressee = modified_data['sender'], requester = modified_data['recipient'], status = 'accepted')
        situation2 = Q(addressee = modified_data['recipient'], requester = modified_data['sender'], status = 'accepted')
        relationship = Relationship.objects.filter(situation1 | situation2)
        if len(relationship) == 0:
            if modified_data['sender'] == modified_data['recipient']:
                pass
            else:
                return Response({"relationships": "Oops, you're not friends with this person!\n Send a friend request!!!"})
        if 'time' not in request.data.keys():
            modified_data['time'] = datetime.now()
        if modified_data['status'] == 'delayed':
            #TIMEDELTA SHOULD BE DAYS. CAN CHANGE TO MINUTES FOR TESTING PURPOSES
            modified_data['time'] = datetime.now() + timedelta(days=time(request.user.state, ExtendedUser.objects.get(id=request.data['recipient']).state))
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        if modified_data['status'] == 'draft':
            return Response("Your fletter has been saved successfully! \nCheck your drafts to continue composing!")
        if modified_data['status'] == 'sent':
            return Response("Your fletter has been sent successfully!")
        return Response('Your fletter in on your way!')

    def get(self, request):
        self.queryset = Message.objects.all()
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

class InboxAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''

    def get(self, request, recipient):
        user = ExtendedUser()
        try:
            user = ExtendedUser.objects.get(username=recipient)
        except:
            user = request.user
        #code for checking if there are any messages that should have been sent by now
        queryset = Message.objects.filter(Q(time__lte=datetime.now(), status='delayed') | Q(time__lte=datetime.now(), status='scheduled'))
        for message in queryset:
            message.status = 'sent'
            message.save()
        #query the messages
        self.queryset = Message.objects.filter(recipient=user.id, status='sent').order_by('-time') #the - makes it sort from descending
        serializer = self.get_serializer(self.queryset, many=True)
        for i in serializer.data: #add additional addtributes
            i['sender_username'] = ExtendedUser.objects.get(id=i['sender']).username
        return Response(serializer.data)

class DraftsAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''

    def get(self, request, sender):
        user = ExtendedUser()
        try:
            user = ExtendedUser.objects.get(username=sender)
        except:
            user = request.user
        self.queryset = Message.objects.filter(sender=user.id, status='draft').order_by('-time') #the - makes it sort from descending
        serializer = self.get_serializer(self.queryset, many=True)
        for i in serializer.data: #add additional addtributes
            i['recipient_username'] = ExtendedUser.objects.get(id=i['recipient']).username
        return Response(serializer.data)

class SendingAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''

    def get(self, request, sender):
        user = ExtendedUser()
        try:
            user = ExtendedUser.objects.get(username=sender)
        except:
            user = request.user
        #code for checking if there are any messages that should have been sent by now
        queryset = Message.objects.filter(Q(time__lte=datetime.now(), status='delayed') | Q(time__lte=datetime.now(), status='scheduled'))
        for message in queryset:
            message.status = 'sent'
            message.save()
        #query the messages
        self.queryset = Message.objects.filter(Q(sender=user.id, status='delayed') | Q(sender=user.id, status='scheduled')).order_by('-time') #the - makes it sort from descending
        serializer = self.get_serializer(self.queryset, many=True)
        for i in serializer.data: #add additional addtributes
            i['recipient_username'] = ExtendedUser.objects.get(id=i['sender']).username
        return Response(serializer.data)

class FavoriteAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''

    def get(self, request, recipient):
        user = ExtendedUser()
        try:
            user = ExtendedUser.objects.get(username=recipient)
        except:
            user = request.user
        self.queryset = Message.objects.filter(recipient=user.id, status='sent', favorite=True).order_by('-time') #the - makes it sort from descending
        serializer = self.get_serializer(self.queryset, many=True)
        for i in serializer.data: #add additional addtributes
            i['sender_username'] = ExtendedUser.objects.get(id=i['sender']).username
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        message = Message.objects.get(id = request.data['id'])
        message.favorite = not message.favorite
        message.save()

        return Response({
            'favorite': message.favorite
        })

class DeleteAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''

    def get(self, request, recipient):
        user = ExtendedUser()
        try:
            user = ExtendedUser.objects.get(username=recipient)
        except:
            user = request.user
        self.queryset = Message.objects.filter(recipient=user.id, status='deleted').order_by('-time') #the - makes it sort from descending
        serializer = self.get_serializer(self.queryset, many=True)
        for i in serializer.data: #add additional addtributes
            i['sender_username'] = ExtendedUser.objects.get(id=i['sender']).username
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        for entry in request.data:
            message = Message.objects.get(id = entry['id'])
            message.status = 'deleted'
            message.save()
        return Response({})
    
    def delete(self, request, *args, **kwargs):
        for entry in request.data:
            Message.objects.get(id = entry['id']).delete()
        return Response({})

class RestoreAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''
    
    def post(self, request, *args, **kwargs):
        for entry in request.data:
            message = Message.objects.get(id = entry['id'])
            message.status = 'sent'
            message.save()
        return Response({})

class EditMessageAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        def time(state1, state2):
            # converting coords into radians
            state1_lat = radians(settings.STATE_COORDS[state1][0])
            state1_long = radians(settings.STATE_COORDS[state1][1])
            state2_lat = radians(settings.STATE_COORDS[state2][0])
            state2_long = radians(settings.STATE_COORDS[state2][1])
            # haversine formula (spherical trig)
            radius_miles = 3956
            dist_lat = state2_lat - state1_lat
            dist_long = state2_long - state1_long
            a = sin(dist_lat / 2) ** 2 + cos(state1_lat) * cos(state2_lat) * sin(dist_long / 2) ** 2
            b = 2 * asin(sqrt(a))
            distance = b * radius_miles
            # calculating mail delivery time based on distance in miles
            if distance < 550:
                return 1
            elif 550 <= distance < 1000:
                return 2
            elif 1000 <= distance < 2000:
                return 3
            else:
                return 4
        message = Message.objects.get(id = request.data['key'])
 
        try:
            message.recipient= ExtendedUser.objects.get(username=request.data['recipient'])
        except:
            return Response({"username": "Sorry! We cannot find any account associated with this username!"}) 

        message.subject = request.data['subject']
        message.body = request.data['body']
        message.status = request.data['status']

        situation1 = Q(addressee = message.sender, requester = message.recipient, status = 'accepted')
        situation2 = Q(addressee = message.recipient, requester = message.sender, status = 'accepted')
        relationship = Relationship.objects.filter(situation1 | situation2)
        if len(relationship) == 0:
            if message.sender == message.recipient:
                pass
            else:
                return Response({"relationships": "Oops, you're not friends with this person!\n Send a friend request!!!"})
        if 'time' not in request.data.keys():
            message.time = datetime.now()
        else:
            message.time = request.data['time']
        if message.status == 'delayed':
            #TIMEDELTA SHOULD BE DAYS. CAN CHANGE TO MINUTES FOR TESTING PURPOSES
            modified_data.time = datetime.now() + timedelta(days=time(request.user.state, ExtendedUser.objects.get(id=request.data['recipient']).state))

        message.save()

        if message.status == 'draft':
            return Response("Your fletter has been saved successfully! \nCheck your drafts to continue composing!")
        if message.status == 'sent':
            return Response("Your fletter has been sent successfully!")
        return Response('Your fletter in on your way!')

    def get(self, request):
        self.queryset = Message.objects.all()
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

