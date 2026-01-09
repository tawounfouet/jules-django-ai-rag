from django.db import models
from core.models import Company

class Product(models.Model):
    TYPE_CHOICES = (
        ('PHYSIQUE', 'Physique'),
        ('SERVICE', 'Service'),
    )

    # Ideally products belong to a company? The prompt didn't explicitly say "Product" has a company FK
    # but "CogniFlow est une plateforme multi-entreprise... gestion commerciale".
    # So logically everything should be scoped by Company.
    # The prompt section 3.3 "Commerce - Catalogue & ventes" lists fields but doesn't explicitly list "company".
    # However, section 3.2 Knowledge explicitly lists it.
    # Given "isolation par Company", I MUST add company FK to Product and Customer/Order.

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PHYSIQUE')
    categorie = models.CharField(max_length=100, blank=True)
    est_actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    nom = models.CharField(max_length=255, help_text="ex: 30ml")
    sku = models.CharField(max_length=100, unique=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantite = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.nom} - {self.nom}"


class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='customers')
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    ltv = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Lifetime Value")
    canal_origine = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nom


class Order(models.Model):
    STATUT_CHOICES = (
        ('created_by_bot', 'Créée par Bot'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
    )
    SOURCE_CHOICES = (
        ('chatbot', 'Chatbot'),
        ('manual', 'Manuel'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    date_creation = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='created_by_bot')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='chatbot')

    def __str__(self):
        return f"Commande #{self.id} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite}x {self.product_variant}"
