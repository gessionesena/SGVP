from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from django.forms import ValidationError
from installments.models import Installment
from payments_allocations.models import Payment_Allocation


@transaction.atomic
def generate_sale_installments(sale_instance):
    Installment.objects.filter(sale=sale_instance).delete()

    total_price = sale_instance.selling_price
    quantity = sale_instance.installment_quantity
    payment_day = sale_instance.card.payment_due_day
    sale_date = sale_instance.sale_date

    total_price_decimal = Decimal(str(total_price))
    base_amount = (total_price_decimal / Decimal(quantity)).quantize(
        Decimal('0.01'), rounding=ROUND_DOWN
    )
    total_base_amount = base_amount * (Decimal(quantity) - 1)
    last_amount = total_price_decimal - total_base_amount

    current_due_date = sale_date
    DEADLINE_DAY = sale_instance.card.payment_due_day - 5

    if DEADLINE_DAY <= 0:
        DEADLINE_DAY = 0

    if sale_date.day > DEADLINE_DAY:
        current_due_date = (current_due_date + relativedelta(months=1)).replace(day=payment_day)
    else:
        current_due_date = current_due_date.replace(day=payment_day)

    installments_to_create = []
    for i in range(1, quantity + 1):
        amount_for_this_installment = base_amount if i < quantity else last_amount

        commission = Decimal('0.00')
        late_fee = Decimal('0.00')

        amount_total = amount_for_this_installment + commission + late_fee

        installments_to_create.append(
            Installment(
                sale=sale_instance,
                number=i,
                due_date=current_due_date,
                amount=amount_for_this_installment,
                commission_value=commission,
                late_fee_value=late_fee,
                amount_total=amount_total,
            )
        )
        current_due_date = current_due_date + relativedelta(months=1)

    Installment.objects.bulk_create(installments_to_create)


@transaction.atomic
def update_sale_with_installments(sale_instance_to_update, new_sale_data):

    sale_instance_to_update.refresh_from_db()

    fields_that_trigger_recreation = [
        'selling_price',
        'installment_quantity',
        'card',
        'sale_date'
    ]

    has_relevant_change = False
    for field in fields_that_trigger_recreation:
        if new_sale_data[field] != getattr(sale_instance_to_update, field):
            has_relevant_change = True
            break

    if not has_relevant_change:
        sale_instance_to_update.title = new_sale_data['title']
        sale_instance_to_update.customer = new_sale_data['customer']
        sale_instance_to_update.category = new_sale_data['category']
        sale_instance_to_update.cost_price = new_sale_data['cost_price']
        sale_instance_to_update.description = new_sale_data['description']
        sale_instance_to_update.save()
        return sale_instance_to_update

    has_payments = Payment_Allocation.objects.filter(
        installment__sale=sale_instance_to_update
    ).exists()

    if has_payments:
        raise ValidationError(
            'Não é possível alterar dados financeiros. Pois já existem pagamentos registrados para esta venda.',
            code='payments_exist'
        )

    sale_instance_to_update.selling_price = new_sale_data['selling_price']
    sale_instance_to_update.installment_quantity = new_sale_data['installment_quantity']
    sale_instance_to_update.card = new_sale_data['card']
    sale_instance_to_update.sale_date = new_sale_data['sale_date']
    sale_instance_to_update.title = new_sale_data['title']
    sale_instance_to_update.customer = new_sale_data['customer']
    sale_instance_to_update.category = new_sale_data['category']
    sale_instance_to_update.cost_price = new_sale_data['cost_price']
    sale_instance_to_update.description = new_sale_data['description']

    sale_instance_to_update.save()

    generate_sale_installments(sale_instance_to_update)

    return sale_instance_to_update
