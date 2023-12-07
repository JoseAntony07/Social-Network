from .models import User, FriendRequest
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'gender', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  # without password
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class FriendRequestSerializer(serializers.ModelSerializer):
    sent_from_user = UserSerializer(source='sent_from', read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'status', 'sent_from_user', 'created_on']
