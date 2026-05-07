# apps/employees/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Worker, Availability
from .serializers import WorkerSerializer, AvailabilitySerializer
import re

User = get_user_model()


class WorkerViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Worker.objects.select_related('user').order_by(
            'user__first_name', 'user__last_name'
        )
        if self.request.user.role == 'admin':
            return queryset
        elif self.request.user.role == 'employee':
            return queryset.filter(user=self.request.user)
        return Worker.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data

        # --- Validate required fields ---
        for field in ['email', 'first_name', 'last_name']:
            if not data.get(field, '').strip():
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        email = data['email'].strip().lower()

        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'A user with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Build unique username ---
        base = re.sub(r'[^a-z0-9]', '', email.split('@')[0].lower()) or 'employee'
        username, counter = base, 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{counter}'
            counter += 1

        # --- Create User ---
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=data.get('password') or 'Employee@123',
                first_name=data.get('first_name', '').strip(),
                last_name=data.get('last_name', '').strip(),
                phone=data.get('phone', ''),
                role='employee',
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create user account: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Set position if the field exists on User ---
        if hasattr(user, 'position'):
            user.position = data.get('position', 'Staff')
            user.save(update_fields=['position'])

        # --- Parse skills ---
        skills = data.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]

        # --- Parse commission rate ---
        try:
            commission = float(data.get('commission_rate', 12))
        except (TypeError, ValueError):
            commission = 12.0

        # --- Create Worker ---
        try:
            worker = Worker.objects.create(
                user=user,
                skills=skills,
                working_hours=data.get('working_hours') or {},
                commission_rate=commission,
                is_active=True,
            )
        except Exception as e:
            # Roll back the user if worker creation fails
            user.delete()
            return Response(
                {'error': f'Failed to create worker profile: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Return serialized response ---
        try:
            serializer = self.get_serializer(worker)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Worker was created — return minimal safe response instead of crashing
            return Response({
                'id': worker.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'phone': getattr(user, 'phone', '') or '',
                'position': getattr(user, 'position', 'Staff') or 'Staff',
                'skills': worker.skills,
                'commission_rate': float(worker.commission_rate),
                'is_active': worker.is_active,
                'hire_date': str(worker.hire_date),
            }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        worker = self.get_object()
        data = request.data
        user = worker.user

        # --- Update user fields ---
        for field in ['first_name', 'last_name', 'phone']:
            if field in data:
                setattr(user, field, data[field])

        if hasattr(user, 'position') and 'position' in data:
            user.position = data['position']

        if data.get('password'):
            user.set_password(data['password'])

        try:
            user.save()
        except Exception as e:
            return Response(
                {'error': f'Failed to update user: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Update worker fields ---
        skills = data.get('skills', worker.skills)
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
        worker.skills = skills

        if 'commission_rate' in data:
            try:
                worker.commission_rate = float(data['commission_rate'])
            except (TypeError, ValueError):
                pass

        if 'working_hours' in data:
            worker.working_hours = data['working_hours'] or {}

        if 'is_active' in data:
            worker.is_active = data['is_active']

        try:
            worker.save()
        except Exception as e:
            return Response(
                {'error': f'Failed to update worker: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer = self.get_serializer(worker)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'id': worker.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'phone': getattr(user, 'phone', '') or '',
                'position': getattr(user, 'position', 'Staff') or 'Staff',
                'skills': worker.skills,
                'commission_rate': float(worker.commission_rate),
                'is_active': worker.is_active,
                'hire_date': str(worker.hire_date),
            })


class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Availability.objects.select_related(
            'worker', 'worker__user'
        ).order_by('-date').filter(
            **({} if self.request.user.role == 'admin'
               else {'worker__user': self.request.user}
               if self.request.user.role == 'employee'
               else {'pk__in': []})
        )