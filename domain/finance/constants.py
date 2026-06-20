from django.db import models
from django.utils.translation import gettext_lazy as _


class FeeCategory(models.TextChoices):
    REGISTRATION = "REGISTRATION", _("Inscription")
    TUITION = "TUITION", _("Scolarité")
    MATERIAL = "MATERIAL", _("Fournitures")
    EXAM = "EXAM", _("Examen")
    TRANSPORT = "TRANSPORT", _("Transport")
    MEAL = "MEAL", _("Cantine")
    PTA = "PTA", _("APE")
    OTHER = "OTHER", _("Autre")


class PaymentFrequency(models.TextChoices):
    ANNUAL = "ANNUAL", _("Annuel")
    TERM = "TERM", _("Trimestriel")
    MONTHLY = "MONTHLY", _("Mensuel")


class PaymentMethod(models.TextChoices):
    CASH = "CASH", _("Espèces")
    BANK_TRANSFER = "BANK_TRANSFER", _("Virement bancaire")
    MOBILE_MONEY = "MOBILE_MONEY", _("Monnaie mobile")
    CHECK = "CHECK", _("Chèque")


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", _("En attente")
    PAID = "PAID", _("Payé")
    PARTIAL = "PARTIAL", _("Partiel")
    OVERDUE = "OVERDUE", _("En retard")
    EXEMPTED = "EXEMPTED", _("Exonéré")
