from django.db import models
from core.models import Company

class KnowledgeBase(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='knowledge_bases')
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    nombre_documents = models.IntegerField(default=0)
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.company.nom})"

class FileSource(models.Model):
    TYPE_SOURCE_CHOICES = (
        ('UPLOAD', 'Upload'),
        ('URL', 'URL'),
        ('GOOGLE_DRIVE', 'Google Drive'),
    )
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='sources')
    nom = models.CharField(max_length=255)
    type_source = models.CharField(max_length=20, choices=TYPE_SOURCE_CHOICES, default='UPLOAD')

    def __str__(self):
        return self.nom

class File(models.Model):
    TYPE_CHOICES = (
        ('TEXT', 'Text'),
        ('PDF', 'PDF'),
        ('DOCX', 'DOCX'),
        ('HTML', 'HTML'),
    )
    source = models.ForeignKey(FileSource, on_delete=models.CASCADE, related_name='files')
    titre = models.CharField(max_length=255)
    fichier_physique = models.FileField(upload_to='knowledge/%Y/%m/', blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.titre

class EmbeddingStatus(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    )
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='embedding_status')
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    collection_chroma_id = models.CharField(max_length=255, blank=True)
    nombre_de_chunks = models.IntegerField(default=0)

    def __str__(self):
        return f"Status: {self.statut} for {self.file.titre}"

class IngestionLog(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='logs')
    logs = models.TextField()
    succes = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.created_at} - {self.file.titre}"
