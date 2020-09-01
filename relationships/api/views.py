from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q

from .serializers import RelationshipSerializer

from relationships.models import Relationship
from accounts.models import ExtendedUser

from datetime import datetime

class RelationshipAPIView(generics.GenericAPIView):
    serializer_class = RelationshipSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        modified_data = request.data
        if 'requester' not in request.data.keys():
            user = request.user
            modified_data['requester'] = user.id
            
        try:
            modified_data['addressee'] = ExtendedUser.objects.get(username=request.data['addressee']).id
        except:
            return Response("This username does not exist!")

        if modified_data['requester'] == modified_data['addressee']:
            return Response("Sorry! You cannot send friend requests to yourself!")

        situation1 = Q(addressee = modified_data['addressee'], requester = modified_data['requester'], status = 'accepted')            
        situation2 = Q(addressee = modified_data['requester'], requester = modified_data['addressee'], status = 'accepted')
        friends = Relationship.objects.filter(situation1 | situation2)
        if len(friends) != 0:
            return Response("You are already friends with this user!")

        sent = Relationship.objects.filter(Q(addressee = modified_data['addressee'], requester = modified_data['requester'], status = 'pending'))
        if len(sent) != 0:
            return Response("You have already sent a friend request to this user!")
            
        pending = Relationship.objects.filter(Q(addressee = modified_data['requester'], requester = modified_data['addressee'], status = 'pending'))
        if len(pending) != 0:
            return Response("This user has already sent you a friend request! \nCheck your contacts to accept the request!")

        if 'created_time' not in request.data.keys():
            modified_data['created_time'] = datetime.now()
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        relationship = serializer.save()
        return Response("Your request has been sent!")

    def get(self, request):
        self.queryset = Relationship.objects.all()
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)


class FriendRequestAPIView(generics.GenericAPIView):
    serializer_class = RelationshipSerializer
    queryset = ''

    def get(self, request, addressee):
        user = ExtendedUser()
        try:
            user = ExtendedUser.objects.get(username=addressee)
        except:
            user = request.user
        self.queryset = Relationship.objects.filter(addressee=user.id, status='pending').order_by('-created_time') #the - makes it sort from descending
        serializer = self.get_serializer(self.queryset, many=True)
        for i in serializer.data: #add additional addtributes
            i['requester_username'] = ExtendedUser.objects.get(id=i['requester']).username
            i['requester_birdColor'] = ExtendedUser.objects.get(id=i['requester']).bird_color
        return Response(serializer.data)

class AcceptAPIView(generics.GenericAPIView):
    serializer_class = RelationshipSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):
        addressee = request.user.id
        requester = ExtendedUser.objects.get(username=request.data['requester']).id
        modified_id = Relationship.objects.get(addressee=addressee, requester=requester).id

        modified_data = Relationship.objects.get(id = modified_id)

        modified_data.created_time = datetime.now()
        modified_data.status = "accepted"
        modified_data.save()

        return Response("accepted")

class DeleteAPIView(generics.GenericAPIView):
    serializer_class = RelationshipSerializer
    queryset = ''

    def post(self, request, *args, **kwargs):    
        addressee = request.user.id
        requester = ExtendedUser.objects.get(username=request.data['requester']).id
        
        situation1 = Q(addressee=addressee, requester=requester)            
        situation2 = Q(addressee=requester, requester=addressee)
        modified_id = Relationship.objects.get(situation1 | situation2).id

        modified_data = Relationship.objects.get(id = modified_id)
        modified_data.delete()

        return Response("deleted")

class ContactAPIView(generics.GenericAPIView):
    serializer_class = RelationshipSerializer
    queryset = ''

    def get(self, request, addressee):
        user = ExtendedUser()
        try:
            user = ExtendedUser.objects.get(username=addressee)
        except:
            user = request.user
        self.queryset = Relationship.objects.filter( (Q(addressee=user.id) | Q(requester=user.id) ), status='accepted').order_by('-created_time') #the - makes it sort from descending
        serializer = self.get_serializer(self.queryset, many=True)
        for i in serializer.data: #add additional addtributes
            if(i['addressee']==user.id):
                i['contact_username'] = ExtendedUser.objects.get(id=i['requester']).username
                i['contact_birdColor'] = ExtendedUser.objects.get(id=i['requester']).bird_color
                i['contact_address'] = ExtendedUser.objects.get(id=i['requester']).number + " " + ExtendedUser.objects.get(id=i['requester']).address + ", " + ExtendedUser.objects.get(id=i['requester']).state
            else:
                i['contact_username'] = ExtendedUser.objects.get(id=i['addressee']).username
                i['contact_birdColor'] = ExtendedUser.objects.get(id=i['addressee']).bird_color
                i['contact_address'] = ExtendedUser.objects.get(id=i['addressee']).number + " " + ExtendedUser.objects.get(id=i['addressee']).address + ", " + ExtendedUser.objects.get(id=i['addressee']).state
        return Response(serializer.data)