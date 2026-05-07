import csv
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.accounts.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_bookings(request):
    if request.user.role != 'admin':
        return HttpResponse('Unauthorized', status=401)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Customer', 'Date', 'Status', 'Total Amount'])
    
    bookings = Booking.objects.select_related('customer')
    for booking in bookings:
        writer.writerow([
            str(booking.id),
            booking.customer.get_full_name(),
            booking.booking_date,
            booking.status,
            float(booking.total_amount)
        ])
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_payments(request):
    if request.user.role != 'admin':
        return HttpResponse('Unauthorized', status=401)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Booking', 'Amount', 'Method', 'Status'])
    
    payments = Payment.objects.select_related('booking')
    for payment in payments:
        writer.writerow([
            payment.id,
            str(payment.booking.id),
            float(payment.amount),
            payment.method,
            payment.status
        ])
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_employees(request):
    if request.user.role != 'admin':
        return HttpResponse('Unauthorized', status=401)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Role'])
    
    employees = User.objects.filter(role='employee')
    for emp in employees:
        writer.writerow([
            emp.id,
            emp.get_full_name(),
            emp.email,
            emp.role
        ])
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_customers(request):
    if request.user.role != 'admin':
        return HttpResponse('Unauthorized', status=401)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Total Bookings'])
    
    customers = User.objects.filter(role='customer')
    for customer in customers:
        bookings_count = Booking.objects.filter(customer=customer, status='completed').count()
        writer.writerow([
            customer.id,
            customer.get_full_name(),
            customer.email,
            bookings_count
        ])
    
    return response
