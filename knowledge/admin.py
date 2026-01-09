from django.contrib import admin
from .models import KnowledgeBase, FileSource, File, EmbeddingStatus, IngestionLog

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'company', 'is_default', 'nombre_documents', 'est_active')
    list_filter = ('company', 'est_active')

@admin.register(FileSource)
class FileSourceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'knowledge_base', 'type_source')

class EmbeddingStatusInline(admin.StackedInline):
    model = EmbeddingStatus
    can_delete = False

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('titre', 'source', 'type')
    inlines = [EmbeddingStatusInline]

@admin.register(IngestionLog)
class IngestionLogAdmin(admin.ModelAdmin):
    list_display = ('file', 'succes', 'created_at')
    list_filter = ('succes', 'created_at')
