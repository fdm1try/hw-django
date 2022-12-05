from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Article, Tag, Scope


class ScopeInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        main_tag_count = len([
            True for form in self.forms
            if form.cleaned_data.get('is_main') and not form.cleaned_data.get('DELETE')
        ])
        if main_tag_count < 1:
            raise ValidationError('Укажите основной раздел')
        elif main_tag_count > 1:
            raise ValidationError('Основным может быть только один раздел')
        return super().clean()


class ScopeInline(admin.TabularInline):
    model = Scope
    formset = ScopeInlineFormset
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ScopeInline]
    list_display = ['title', 'text', 'published_at', 'image']
