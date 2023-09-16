from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CheckConstraint, Q
from django.db import models


class Currency(models.Model):
    code = models.CharField("3 letter representation of a currency(USD)", max_length=3)
    name = models.CharField("Name of currency(dollar)", max_length=50)

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(code__regex=r"^[A-Z]+$"),
                name="code_all_uppercase",
                violation_error_message="Code must be all uppercase",
            ),
            CheckConstraint(
                check=Q(name__regex=r"^[a-z]+$"),
                name="name_all_lowercase",
                violation_error_message="Name must be all lowercase",
            ),
        ]


class Stock(models.Model):
    name = models.CharField("Name of the stock", max_length=100)
    code = models.CharField("Code of the stock", max_length=50)
    currency = models.ForeignKey(
        "Currency", verbose_name="Currency for this stock", on_delete=models.CASCADE
    )


class Report(models.Model):
    title = models.CharField("Title of the report", max_length=200)
    stock = models.ForeignKey(
        "Stock", verbose_name="Related stock", on_delete=models.CASCADE
    )
    url = models.URLField("URL where report is published")
    target_price = models.DecimalField(
        "Target price for related stock", max_digits=10, decimal_places=2
    )
    price_on_publish = models.DecimalField(
        "Price of related stock when published", max_digits=10, decimal_places=2
    )
    publish_date = models.DateField("Date when the report was published")

    is_newest = models.BooleanField(default=False)
    next_publish_date = models.DateField(
        "The date of next publication if known",
        null=True,
    )

    SENTIMENT_CHOICES = (
        ("BUY", "Buy"),
        ("HOLD", "Hold"),
        ("SELL", "Sell"),
    )

    HIDDEN_SENTIMENT_CHOICES = (
        ("BUY", "Buy"),
        ("SELL", "Sell"),
    )

    written_sentiment = models.CharField(
        "Sentiment written in the report (Buy/Hold/Sell)",
        max_length=4,
        choices=SENTIMENT_CHOICES,
        default="HOLD",
    )
    hidden_sentiment = models.CharField(
        "Hidden sentiment (not explicitly mentioned but implied)",
        max_length=4,
        choices=HIDDEN_SENTIMENT_CHOICES,
        blank=True,
    )

    hit_rate = models.FloatField(
        "Hit rate as a percentage (0-1)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True,
    )
    days_hit = models.IntegerField("Number of days the sentiment has hit", null=True)
    days_missed = models.IntegerField(
        "Number of days it missed target after publication", null=True
    )
    days_to_first_hit = models.IntegerField(
        "Number of days it took to first hit target after publication", null=True
    )
    days_to_first_miss = models.IntegerField(
        "Number of days it took to first miss target after publication", null=True
    )

    class Meta:
        constraints = [
            CheckConstraint(
                check=(Q(hit_rate__gte=0.0) & Q(hit_rate__lte=1.0)),
                name="report_hitrate_range",
            )
        ]


class Analyst(models.Model):
    name = models.CharField("Name of the analyst", max_length=100)
    company = models.CharField("Company name", max_length=100)

    hit_rate = models.FloatField(
        "Hit rate as a percentage (0-1)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True,
    )
    avg_days_hit = models.FloatField("Average days hit", null=True)
    avg_days_missed = models.FloatField("Average days missed", null=True)
    avg_days_to_first_hit = models.FloatField("Average days to first hit", null=True)
    avg_days_to_first_miss = models.FloatField("Average days to first miss", null=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=(Q(hit_rate__gte=0.0) & Q(hit_rate__lte=1.0)),
                name="analyst_hitrate_range",
            )
        ]


class Point(models.Model):
    content = models.TextField("Content of the point")
    report = models.ForeignKey(
        "Report", verbose_name="Related report", on_delete=models.CASCADE
    )
    is_positive = models.BooleanField("Is this a positive point?", default=True)


class Writes(models.Model):
    analyst = models.ForeignKey(
        "Analyst", verbose_name="Related analyst", on_delete=models.CASCADE
    )
    report = models.ForeignKey(
        "Report", verbose_name="Related report", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["analyst", "report"], name="unique_analyst_report"
            )
        ]
