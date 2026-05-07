# apps/reviews/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
from apps.services.models import Service

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Review.objects.all().order_by('-created_at')
        elif user.role == 'employee':
            return Review.objects.filter(worker__user=user).order_by('-created_at')
        else:
            return Review.objects.filter(customer=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Auto-set the customer and handle service lookup"""
        service_id = self.request.data.get('service')
        service = None
        
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
            except (Service.DoesNotExist, ValueError):
                pass
        
        # Always provide an empty list for photos
        serializer.save(
            customer=self.request.user,
            service=service,
            photos=[],  # ✅ Ensure photos is set
        )
    
    def create(self, request, *args, **kwargs):
        """Override create to handle the review submission properly"""
        try:
            # Handle both 'comment' and 'text' field names from frontend
            data = request.data.copy()
            
            if not data.get('comment') and not data.get('text'):
                return Response(
                    {'error': 'Review text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Map 'text' to 'comment' if needed
            if 'text' in data and 'comment' not in data:
                data['comment'] = data['text']
            
            # Ensure photos is set
            if 'photos' not in data:
                data['photos'] = []
            
            if not data.get('rating'):
                return Response(
                    {'error': 'Rating is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can approve reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        review = self.get_object()
        review.is_approved = True
        review.save()
        return Response({'message': 'Review approved successfully'})
    
    @action(detail=True, methods=['post'])
    def hide(self, request, pk=None):
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can hide reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        review = self.get_object()
        review.is_approved = False
        review.save()
        return Response({'message': 'Review hidden successfully'})