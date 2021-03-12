#! /usr/bin/env python3
from datetime import datetime
from decimal import Decimal
from typing import Union, List

try:
    from pycbrf import rates

except ImportError:
    rates = None

UNSET = object()
Amount = Union[str, Decimal]
Date = Union[str, datetime]


class Income:
    """Доход."""

    def __init__(
        self,
        date: Date,
        amount: Amount,
        *,
        rate: Amount = UNSET,
        rate_exch: Amount = '0',
        tax_rate: int = 13,
    ):
        """

        :param date: Дата фиксации дохода на счёте

        :param amount: Сумма дохода

        :param rate: Курс ЦБ РФ на дату дохода.
            Если не указан, будет вычислен автоматически.

        :param rate_exch: Курс при переводе суммы с валютного
            счёта на рублёвый.

        :param tax_rate: Налоговая ставка

        """
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')

        self.date: datetime = date

        if rate is UNSET:
            rate = self.fetch_rate()

        self.rate: Decimal = Decimal(rate)
        self.rate_exch: Decimal = Decimal(rate_exch)
        self.tax_rate: int = tax_rate

        self.amount: Decimal = Decimal(amount)
        self.amount_roubles: Decimal = self.amount * self.rate
        self.amount_roubles_exch: Decimal = self.amount * self.rate_exch

        self.tax: Decimal = (self.amount * self.tax_rate) / 100
        self.tax_roubles: Decimal = self.tax * self.rate
        self.tax_roubles_exch: Decimal = self.tax * self.rate_exch

    def fetch_rate(self) -> Decimal:
        if not rates:
            raise Exception('Чтобы автоматически вычислить курс валюты, установите pycbrf')

        return rates.ExchangeRates(on_date=self.date)['USD'].rate

    @staticmethod
    def round(val):
        return round(val, 2)


def process_incomes(incomes: List[Income]):
    """Обрабатывает указанные доходы и выводит по ним различные данные.

    :param incomes:

    """
    r = Income.round

    total_amount = Decimal(0)
    total_exch = Decimal(0)
    total_tax = Decimal(0)
    total_diff = Decimal(0)

    def get_signed(amount: Decimal):
        return f"{'+' if amount > 0 else '-'}{r(abs(amount))}"

    for idx, income in enumerate(incomes, 1):
        print()

        amount = income.amount_roubles
        total_amount += amount

        addition = ''
        if income.rate_exch:
            amount_exch = income.amount_roubles_exch
            total_exch += amount_exch
            amount_diff = amount_exch - amount

            if amount_diff > 0:
                total_diff -= amount_diff
            else:
                total_diff += amount_diff

            addition = f', обмен: {r(amount_exch)} ({get_signed(amount_diff)})'

        tax = income.tax_roubles
        total_tax += tax

        print(
            f'Доход {idx} за {income.date.date()}:\n'
            f'  $ {income.amount} [нал. {r(income.tax)}]\n'
            f'  ₽ {r(amount)} [нал. {r(tax)}]{addition}')

    print(
        '\n'
        f'Итого: {r(total_amount)} (сумма) - {r(total_tax)} (налог) = {r(total_amount - total_tax)} (доход).\n'
        f'После обмена: {r(total_exch)} (сумма) - {r(total_tax)} (налог) = {r(total_exch - total_tax)} (доход).\n'
        f'Разница доходов: {get_signed(total_diff)}.'
    )


#######################################################

process_incomes([
    # Income('2020-01-09', '3456.78', rate='61.9057', rate_exch='60.09'),
])
