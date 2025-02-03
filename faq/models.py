from django.db import models
from ckeditor.fields import RichTextField
from googletrans import Translator
from django.core.cache import cache

class FAQ(models.Model):
    # Main fields with WYSIWYG editor support
    question = models.TextField()
    answer = RichTextField()
    
    # Translated fields
    question_hi = models.TextField(blank=True, null=True)
    question_bn = models.TextField(blank=True, null=True)
    answer_hi = RichTextField(blank=True, null=True)
    answer_bn = RichTextField(blank=True, null=True)
    
    def translate_text(self, text, target_language):
        """Translate text using googletrans."""
        # Check cache first
        cache_key = f"faq_translation_{hash(text)}_{target_language}"
        cached_translation = cache.get(cache_key)
        
        if cached_translation:
            return cached_translation
            
        # If not in cache, translate and cache
        translator = Translator()
        translated_text = translator.translate(text, dest=target_language).text
        cache.set(cache_key, translated_text, timeout=3600)  # Cache for 1 hour
        
        return translated_text

    def save(self, *args, **kwargs):
        """Override save method to automatically translate fields."""
        if not self.pk:  # Only translate on creation
            if not self.question_hi:
                self.question_hi = self.translate_text(self.question, 'hi')
            if not self.question_bn:
                self.question_bn = self.translate_text(self.question, 'bn')
            if not self.answer_hi:
                self.answer_hi = self.translate_text(self.answer, 'hi')
            if not self.answer_bn:
                self.answer_bn = self.translate_text(self.answer, 'bn')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question
