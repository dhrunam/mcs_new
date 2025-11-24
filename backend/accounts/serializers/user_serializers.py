from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import UserProfile
from accounts.serializers import UserProfileSerializer
from accounts.serializers import GroupSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    related_profile = UserProfileSerializer(source='user_profile', many=False, read_only =True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name','related_profile')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        user = User.objects.create(**validated_data)

        user.set_password(validated_data['password'])
        user.save()

        return user
    

class UserSerializer(serializers.ModelSerializer):
    related_profile = UserProfileSerializer(source='user_profile', many=False, read_only =True)
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        fields ='__all__'