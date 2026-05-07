# apps/inventory/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models  # ✅ ADD THIS IMPORT
from .models import InventoryItem, InventoryTransaction
from .serializers import InventoryItemSerializer, InventoryTransactionSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_inventory(request):
    """List all inventory items or create a new one"""
    if request.method == 'GET':
        items = InventoryItem.objects.filter(is_active=True).order_by('-updated_at')
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            
            # Create initial transaction record
            InventoryTransaction.objects.create(
                item=item,
                transaction_type='purchase',
                quantity=item.quantity,
                previous_quantity=0,
                new_quantity=item.quantity,
                notes='Initial stock',
                created_by=request.user
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def inventory_detail(request, pk):
    """Retrieve, update or delete an inventory item"""
    item = get_object_or_404(InventoryItem, pk=pk)
    
    if request.method == 'GET':
        serializer = InventoryItemSerializer(item)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        previous_quantity = item.quantity
        serializer = InventoryItemSerializer(
            item, 
            data=request.data, 
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            updated_item = serializer.save()
            
            # If quantity changed, create a transaction record
            new_quantity = updated_item.quantity
            if previous_quantity != new_quantity:
                quantity_diff = new_quantity - previous_quantity
                transaction_type = 'adjustment'
                if quantity_diff > 0:
                    notes = f'Stock increased by {quantity_diff}'
                else:
                    notes = f'Stock decreased by {abs(quantity_diff)}'
                
                InventoryTransaction.objects.create(
                    item=updated_item,
                    transaction_type=transaction_type,
                    quantity=abs(quantity_diff),
                    previous_quantity=previous_quantity,
                    new_quantity=new_quantity,
                    notes=notes,
                    created_by=request.user
                )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Soft delete - mark as inactive
        item.is_active = False
        item.save()
        return Response(
            {'message': f'Item "{item.name}" deleted successfully'},
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_inventory_item(request):
    """Add a new inventory item"""
    serializer = InventoryItemSerializer(data=request.data)
    if serializer.is_valid():
        item = serializer.save()
        
        # Create initial transaction
        InventoryTransaction.objects.create(
            item=item,
            transaction_type='purchase',
            quantity=item.quantity,
            previous_quantity=0,
            new_quantity=item.quantity,
            notes='Initial stock added',
            created_by=request.user
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_stock_alerts(request):
    """Get items that are low in stock"""
    low_stock_items = InventoryItem.objects.filter(
        is_active=True,
        quantity__lte=models.F('min_stock_level')  # ✅ Now models is defined
    ).order_by('quantity')
    
    serializer = InventoryItemSerializer(low_stock_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restock_item(request, pk):
    """Restock an inventory item"""
    item = get_object_or_404(InventoryItem, pk=pk)
    quantity_to_add = request.data.get('quantity', 0)
    
    if not quantity_to_add or int(quantity_to_add) <= 0:
        return Response(
            {'error': 'Quantity must be greater than 0'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    quantity_to_add = int(quantity_to_add)
    previous_quantity = item.quantity
    item.quantity += quantity_to_add
    item.save()
    
    # Create transaction record
    InventoryTransaction.objects.create(
        item=item,
        transaction_type='purchase',
        quantity=quantity_to_add,
        previous_quantity=previous_quantity,
        new_quantity=item.quantity,
        notes=f'Restocked: Added {quantity_to_add} units',
        created_by=request.user
    )
    
    serializer = InventoryItemSerializer(item)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_transactions(request, pk=None):
    """Get transactions for an item or all transactions"""
    if pk:
        item = get_object_or_404(InventoryItem, pk=pk)
        transactions = item.transactions.all().order_by('-created_at')
    else:
        transactions = InventoryTransaction.objects.all().order_by('-created_at')[:100]
    
    serializer = InventoryTransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_stats(request):
    """Get inventory statistics"""
    items = InventoryItem.objects.filter(is_active=True)
    
    total_items = items.count()
    total_stock = items.aggregate(total=models.Sum('quantity'))['total'] or 0
    total_value = sum(item.quantity * item.unit_price for item in items)
    low_stock_count = items.filter(quantity__lte=models.F('min_stock_level')).count()
    out_of_stock_count = items.filter(quantity=0).count()
    categories_count = items.values_list('category', flat=True).distinct().count()
    
    return Response({
        'total_items': total_items,
        'total_stock': total_stock,
        'total_value': float(total_value),
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'categories': categories_count,
    })