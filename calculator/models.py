from django.db import models
from django.forms import DecimalField
from django.core.validators import MinValueValidator

from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


def increment_loan_id():
        id_loan = '{:015d}'.format(Loan.objects.count() + 1)
        return '{}-{}-{}-{}'.format(id_loan[:3], id_loan[3:7], id_loan[7:11], id_loan[11:15])


class Client(models.Model):
    """
    Client Model
    Defines the attributes of a client
    """

    name = models.CharField("Name", max_length=30)
    surname = models.CharField("Last name", max_length=30)
    email = models.EmailField("E-mail")
    phone = models.BigIntegerField("Phone")
    cpf = models.BigIntegerField("CPF", unique=True)

    @property
    def is_indebted(self):
        
        loads = self.loan_set.all()
        mp = 0
        for load in loads:
            last_date = load.date_initial + relativedelta(months=+load.term)
            balance = load.get_balance(date_base=last_date)
            if balance > 0:
                mp = load.missed_payments
                
        if mp >= 3:
            return True
        return False

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"Client(id={self.id}, name={self.name}, surname={self.surname}, email={self.email}, phone={self.phone}, cpf={self.cpf})"


class Loan(models.Model):
    """
    Loan Model
    Defines the attributes of a loan
    """
    id = models.CharField(max_length=19, default=increment_loan_id, editable=False, primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(
        "Amount",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    term = models.IntegerField("Term", validators=[MinValueValidator(1)])
    rate = models.DecimalField(
        "Rate",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    date_initial = models.DateTimeField(
        "Date creation", auto_now=False, auto_now_add=False
    )
    instalment = models.DecimalField(
        "Instalment",
        default=Decimal('0.0'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    
    @property
    def missed_payments(self):
        return self.payment_set.filter(status="missed").count()

    def _instalment_adjustment(self):
        loans_history = self.client.loan_set.all()
        missed_payments = sum(
            [ load.missed_payments for load in loans_history]
        )
        if len(loans_history) >= 1:
            adjustment = Decimal('1')
            if missed_payments == 0:
                adjustment = -0.02
            elif 0 < missed_payments <= 3:
                adjustment = 0.04
            return Decimal(adjustment)
        return Decimal(0)

    def calculate_instalment(self):
        r = self.rate / self.term
        instalment = (
            (r + r / ((1 + r) ** self.term - 1))
            * self.amount
            * (1 + self._instalment_adjustment())
        )
        return instalment.quantize(Decimal(".01"), rounding=ROUND_DOWN)

    def get_balance(self, date_base=datetime.now().astimezone(tz=timezone.utc)):
        try:
            payments = self.payment_set.filter(
                status="made", date__lte=date_base
            ).values("amount")
            return self.amount - sum([payment["amount"] for payment in payments])
        except:
            return Decimal("0")

    def save(self, *args, **kwargs):
        self.instalment += self.calculate_instalment()
        super(Loan, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Loan"
        verbose_name_plural = "Loans"

    def __str__(self):
        return f"Loan(loan_id={self.id}, amount={self.amount}, term={self.term}, rate={self.rate}, date_initial={self.date_initial})"


class Payment(models.Model):
    """
    Payment Model
    Defines the attributes of a Payment
    """
    PAYMENT_CHOICES = (('made', 'made'), ('missed', 'missed'))

    loan_id = models.ForeignKey('Loan', on_delete=models.CASCADE)
    status = models.CharField('status', db_column='type', max_length=6, choices=PAYMENT_CHOICES)
    date = models.DateTimeField('Date', auto_now=False, auto_now_add=False)
    amount = models.DecimalField('Amount', max_digits=15, decimal_places=2,
                                 validators=[
                                    MinValueValidator(Decimal("0.01"))
                                 ])

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment(loan_id={self.loan_id}, status={self.status}, date={self.date}, amount={self.amount})"
