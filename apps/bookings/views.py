from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Booking, BookingItem, WorkCompletion
from .serializers import BookingSerializer, WorkCompletionSerializer

User = get_user_model()


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Booking.objects.select_related(
                'customer', 'worker', 'worker__user'
            ).prefetch_related('items__service').all()
        elif user.role == 'employee':
            from apps.employees.models import Worker
            try:
                worker = Worker.objects.get(user=user)
                return Booking.objects.select_related(
                    'customer', 'worker', 'worker__user'
                ).prefetch_related('items__service').filter(worker=worker)
            except Worker.DoesNotExist:
                return Booking.objects.none()
        return Booking.objects.select_related(
            'customer', 'worker'
        ).prefetch_related('items__service').filter(customer=user)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        # --- Resolve worker ---
        worker_id = data.get('worker') or data.get('worker_id')
        worker = None
        if worker_id:
            from apps.employees.models import Worker
            try:
                worker = Worker.objects.get(id=worker_id)
            except Worker.DoesNotExist:
                return Response(
                    {'error': 'Worker not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # --- Validate date & time ---
        booking_date = data.get('booking_date')
        time_slot    = data.get('time_slot')
        if not booking_date or not time_slot:
            return Response(
                {'error': 'booking_date and time_slot are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Resolve customer ---
        customer = user
        if user.role == 'admin':
            customer_user_id = data.get('customer')
            if customer_user_id:
                try:
                    customer = User.objects.get(id=customer_user_id)
                except User.DoesNotExist:
                    pass

        # --- Create booking ---
        try:
            booking = Booking.objects.create(
                customer=customer,
                worker=worker,
                booking_date=booking_date,
                time_slot=time_slot,
                type=data.get('type', 'in_salon'),
                notes=data.get('notes', ''),
                status='confirmed',  # auto-confirm so employees can act on it immediately
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create booking: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Resolve service items ---
        from apps.services.models import Service

        service_items = data.get('service_items', [])
        single_service_id = data.get('service') or data.get('service_id')
        if not service_items and single_service_id:
            service_items = [{'service': single_service_id, 'quantity': 1}]

        if not service_items:
            booking.delete()
            return Response(
                {'error': 'At least one service is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in service_items:
            service_id = item.get('service') or item.get('service_id')
            quantity   = int(item.get('quantity', 1))
            try:
                service = Service.objects.get(id=service_id)
            except Service.DoesNotExist:
                booking.delete()
                return Response(
                    {'error': f'Service {service_id} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            price = (
                service.mobile_price
                if data.get('type') == 'mobile' and hasattr(service, 'mobile_price')
                else service.base_price
            )

            BookingItem.objects.create(
                booking=booking,
                service=service,
                quantity=quantity,
                price_at_time=price,
            )

        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in ['pending', 'confirmed']:
            booking.status = 'cancelled'
            booking.save()
            return Response({'message': 'Booking cancelled successfully'})
        return Response(
            {'error': 'Booking cannot be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def complete_work(self, request, pk=None):
        booking = self.get_object()

        # Allow completion from any non-terminal status
        if booking.status in ['completed', 'cancelled', 'no_show']:
            return Response(
                {'error': f'Cannot complete a booking with status: {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        completion, _ = WorkCompletion.objects.get_or_create(
            booking=booking,
            defaults={'worker': booking.worker}
        )
        completion.notes          = request.data.get('notes', '')
        completion.photos         = request.data.get('photos', [])
        completion.products_used  = request.data.get('products_used', [])
        completion.save()

        booking.status = 'completed'
        booking.save()

        serializer = self.get_serializer(booking)
        return Response({
            'message': 'Work marked as completed',
            'booking': serializer.data
        })

    @action(detail=True, methods=['post'])
    def start_work(self, request, pk=None):
        """Mark a booking as in_progress."""
        booking = self.get_object()
        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {'error': f'Cannot start a booking with status: {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'in_progress'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response({
            'message': 'Booking started',
            'booking': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        booking    = self.get_object()
        new_status = request.data.get('status')
        valid      = [s[0] for s in Booking.STATUS_CHOICES]
        if new_status not in valid:
            return Response(
                {'error': f'Invalid status. Choose from: {valid}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = new_status
        booking.save()
        serializer = self.get_serializer(booking)
        return Response({
            'message': f'Status updated to {new_status}',
            'booking': serializer.data
        })