from django.shortcuts import render
from sales.models import Sale
from categories.models import Category


def sales_by_category_report(request):
    category_id = request.GET.get('category')

    categories = Category.objects.all()
    sales = Sale.objects.none()

    if category_id:
        sales = Sale.objects.select_related(
            'customer', 'card'
        ).filter(
            category=category_id
        ).order_by('-sale_date')

    context = {
        'categories': categories,
        'sales': sales,
        'selected_category': category_id,
    }

    return render(request, 'reports/sales_by_category.html', context)
