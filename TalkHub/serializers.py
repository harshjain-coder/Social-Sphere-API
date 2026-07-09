from rest_framework import serializers
from .models import Person
from .models import Post
from .models import Comment
from .models import Like
from .models import Save
from .models import SignUp  



class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class SaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Save
        fields = '__all__'

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignUp
        fields = '__all__'

