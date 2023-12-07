from datetime import timedelta, datetime
from rest_framework.viewsets import ModelViewSet
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework import filters, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from socialproject.utils import IsAuthenticated, apply_query_filter, CustomThrottle, CustomSearchFilter
from rest_framework.views import APIView
import jwt
from django.conf import settings
from rest_framework.decorators import action


class RegisterAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPI(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User Not Found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!')

        # jwt_expiration_time
        jwt_expiration_time = datetime.utcnow() + timedelta(minutes=60)

        # jwt payload(header, payload, secret)
        payload = {
            'id': str(user.id),
            'exp': jwt_expiration_time,
            'iat': jwt_expiration_time.microsecond
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').encode().decode('utf-8')

        # in the above jwt token, we have to set it as cookie
        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {"jwt": token}

        return response


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {"message": "success"}
        return response


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter]

    search_fields = ['first_name', 'last_name', 'email']

    def get_queryset(self):
        queryset = User.objects.all()

        if query := self.request.query_params.get('query'):
            queryset = apply_query_filter(queryset, query, user=self.request.user)

        return queryset

    def list(self, request, *args, **kwargs):

        if self.request.query_params.get('query') == 'pending_requests':
            self.search_fields = ['sent_from__email']
            self.serializer_class = FriendRequestSerializer

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='send_friend_request', throttle_classes=[CustomThrottle])
    def send_fr_request(self, request, pk=None):
        user1 = self.get_object()
        user2_id = request.data.get('user_id')

        try:
            user2 = User.objects.get(id=user2_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user1.send_friend_request(user2):
            return Response({"message": "Friend request sent"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Unable to send friend request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='accept_friend_request/(?P<request_id>[^/.]+)')
    def accept_fr_request(self, request, pk=None, request_id=None):
        user = self.get_object()

        try:
            friend_request = FriendRequest.objects.get(pk=request_id, sent_to=user, status=1)  # Get pending request
        except FriendRequest.DoesNotExist:
            return Response({"message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.accept_friend_request(friend_request):
            return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Unable to accept friend request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='reject_friend_request/(?P<request_id>[^/.]+)')
    def reject_fr_request(self, request, pk=None, request_id=None):
        user = self.get_object()

        try:
            friend_request = FriendRequest.objects.get(pk=request_id, sent_to=user, status=1)  # Get pending request
        except FriendRequest.DoesNotExist:
            return Response({"message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.reject_friend_request(friend_request):
            return Response({"message": "Friend request rejected"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Unable to reject friend request"}, status=status.HTTP_400_BAD_REQUEST)
