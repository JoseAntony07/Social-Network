from datetime import datetime
from rest_framework import filters
from rest_framework.permissions import BasePermission
import jwt
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.exceptions import Throttled


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        def get_token():
            token = None

            if request.META.get('HTTP_AUTHORIZATION'):
                token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

            elif request.COOKIES.get('jwt'):
                token = request.COOKIES.get('jwt')

            return token

        if not get_token():
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(get_token(), settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token Expired....Please Login Again!')

        except jwt.InvalidSignatureError:
            raise AuthenticationFailed('InvalidSignature....Someone Hacked!')

        try:
            from user.models import User
            user = User.objects.get(id=payload['id'])
            request.user = user

        except Exception as e:
            raise AuthenticationFailed('Unauthenticated!')

        return bool(user.is_authenticated)


class CustomThrottle(SimpleRateThrottle):
    scope = 'three_requests_per_minute'
    rate = '3/min'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"{self.scope}_{request.user.id}"
        return None

    def allow_request(self, request, view):
        if request.user.is_authenticated:
            now = self.timer()
            key = self.get_cache_key(request, view)

            if key is not None:
                request_log = self.cache.get(key, [])
                if len(request_log) < self.num_requests:
                    request_log.append(now)
                    self.cache.set(key, request_log, self.duration)
                    return True
                else:
                    oldest = request_log[0]
                    elapsed = now - oldest
                    if elapsed < self.duration:
                        raise Throttled(detail='Exceeded rate limit for sending friend requests')
                    else:
                        # Reset the count if the duration has passed
                        self.cache.set(key, [now], self.duration)
                        return True
        return True


class CustomSearchFilter(filters.SearchFilter):
    search_param = 'custom-search'


def apply_query_filter(queryset, query, user=None):

    if query == 'accepted_friends':
        queryset = user.friends.filter(requests_received__status=2)

    if query == 'pending_requests':
        queryset = user.requests_received.filter(status=1)

    return queryset
