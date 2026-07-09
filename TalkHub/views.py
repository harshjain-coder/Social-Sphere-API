# from django.shortcuts import render
# from rest_framework import viewsets
# from .models import Person, Post, Comment, Like, Save
# from .serializers import (
#     PersonSerializer, PostSerializer, CommentSerializer, 
#     LikeSerializer, SaveSerializer
# )

# # 1. Profile / Person API 
# class PersonViewSet(viewsets.ModelViewSet):
#     queryset = Person.objects.all()
#     serializer_class = PersonSerializer

# # 2. Post API 
# class PostViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer

# # 3. Comment API 
# class CommentViewSet(viewsets.ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer

# # 4. Like API 
# class LikeViewSet(viewsets.ModelViewSet):
#     queryset = Like.objects.all()
#     serializer_class = LikeSerializer

# # 5. Save API 
# class SaveViewSet(viewsets.ModelViewSet):
#     queryset = Save.objects.all()
#     serializer_class = SaveSerializer



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Person, Post, Comment, Like, Save,SignUp
from .serializers import PersonSerializer,PostSerializer, CommentSerializer, LikeSerializer, SaveSerializer,SignUpSerializer
from rest_framework.permissions import IsAuthenticated

class PersonView(APIView):
    def get(self,request):
        data = Person.objects.all()
        serializer = PersonSerializer(data,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        Person.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SinglePersonView(APIView):
    def get(self,request,id):
        try:
            person = Person.objects.get(id=id)
            serializer = PersonSerializer(person)
            return Response(serializer.data)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        try:
            person = Person.objects.get(id=id)
            person.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self,request,id):
        try:
            person = Person.objects.get(id=id)
            serializer = PersonSerializer(person, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
        
class PostView(APIView):
    def get(self,request):
        data = Post.objects.all()
        serializer = PostSerializer(data,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        Post.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SinglePostView(APIView):
    def get(self,request,id):
        try:
            post = Post.objects.get(id=id)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        try:
            post = Post.objects.get(id=id)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self,request,id):
        try:
            post = Post.objects.get(id=id)
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
class CommentView(APIView):
    def get(self,request):
        data = Comment.objects.all()
        serializer = CommentSerializer(data,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        Comment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SingleCommentView(APIView):
    def get(self,request,id):
        try:
            comment = Comment.objects.get(id=id)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        try:
            comment = Comment.objects.get(id=id)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self,request,id):
        try:
            comment = Comment.objects.get(id=id)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
class LikeView(APIView):
    def get(self,request):
        data = Like.objects.all()
        serializer = LikeSerializer(data,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        Like.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SingleLikeView(APIView):
    def get(self,request,id):
        try:
            like = Like.objects.get(id=id)
            serializer = LikeSerializer(like)
            return Response(serializer.data)
        except Like.DoesNotExist:
            return Response({'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        try:
            like = Like.objects.get(id=id)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self,request,id):
        try:
            like = Like.objects.get(id=id)
            serializer = LikeSerializer(like, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Like.DoesNotExist:
            return Response({'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
        
class SaveView(APIView):
    def get(self,request):
        data = Save.objects.all()
        serializer = SaveSerializer(data,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = SaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        Save.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SingleSaveView(APIView):
    def get(self,request,id):
        try:
            save = Save.objects.get(id=id)
            serializer = SaveSerializer(save)
            return Response(serializer.data)
        except Save.DoesNotExist:
            return Response({'error': 'Save not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,id):
        try:
            save = Save.objects.get(id=id)
            save.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Save.DoesNotExist:
            return Response({'error': 'Save not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self,request,id):
        try:
            save = Save.objects.get(id=id)
            serializer = SaveSerializer(save, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Save.DoesNotExist:
            return Response({'error': 'Save not found'}, status=status.HTTP_404_NOT_FOUND)
        
class SinglePersonPostView(APIView):
    def post(self,request,id):
        person = Person.objects.get(id=id)
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
                serializer.save(user_id=person)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request,id):
        person = Person.objects.get(id=id)
        post = person.post_set.all()
        serializer = PostSerializer(post,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class SinglePostSoftDeleteView(APIView):
    def delete(self,request,id):
        try:
            post = Post.objects.get(id=id)
            post.is_deleted = True
            post.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self,request,id):
        try: 
            post = Post.objects.get(id=id, is_deleted=False)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class SignUpView(APIView):
     permission_classes = [IsAuthenticated]
     def post(self,request):
    
             serializer = SignUpSerializer(data=request.data)
             if serializer.is_valid():
                   serializer.save()
                   return Response({'message':'user signup successfully'},status=status.HTTP_201_CREATED)
             return Response({'message':'user already exists'},status=status.HTTP_409_CONFLICT)
     



    
    







       
     