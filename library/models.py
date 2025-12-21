from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Books(models.Model):
    # Book cover image
    cover_image = CloudinaryField(
        'cover_image',
        folder='books/covers/',
        blank=True,
        null=True,
        help_text="Upload book cover image",
        transformation={
            'quality': 'auto:good',
            'width': 400,
            'height': 600,
            'crop': 'fill'
        }
    )
    
    # Book file (PDF, EPUB, etc.)
    book_file = CloudinaryField(
        'book_file',
        folder='books/files/',
        blank=True,
        null=True,
        resource_type='raw',  # Important for PDF/files
        help_text="Upload book file (PDF, EPUB, etc.)",
        validators=[FileExtensionValidator(['pdf', 'epub', 'mobi', 'txt'])]
    )
    
    # Thumbnail for quick preview
    thumbnail = CloudinaryField(
        'thumbnail',
        folder='books/thumbnails/',
        blank=True,
        null=True,
        help_text="Small thumbnail for preview"
    )
    
    author = models.CharField(
        max_length=250,
        blank=False,
        null=False,
        default="Anonymous",
        verbose_name="Author Name"
    )
    
    title = models.CharField(
        max_length=250,
        blank=False,
        null=False,
        verbose_name="Book Title"
    )
    
    year = models.IntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(timezone.now().year)
        ],
        verbose_name="Publication Year"
    )
    
    isbn = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name="ISBN",
        unique=True
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Book Description"
    )
    
    # File info
    file_size = models.BigIntegerField(
        default=0,
        verbose_name="File Size (bytes)",
        help_text="Size of the book file in bytes"
    )
    
    file_format = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="File Format",
        help_text="e.g., PDF, EPUB, MOBI"
    )
    
    # Download tracking
    download_count = models.IntegerField(
        default=0,
        verbose_name="Download Count"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['year']),
            models.Index(fields=['download_count']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def save(self, *args, **kwargs):
        # Set file format and size if book_file exists
        if self.book_file and hasattr(self.book_file, 'size'):
            self.file_size = self.book_file.size
            
            # Extract file extension
            if hasattr(self.book_file, 'name'):
                import os
                ext = os.path.splitext(self.book_file.name)[1].lower().replace('.', '')
                self.file_format = ext if ext else None
        
        # Auto-generate thumbnail from cover if not provided
        if self.cover_image and not self.thumbnail:
            # You can create a thumbnail version here
            # This requires Cloudinary transformation
            pass
            
        super().save(*args, **kwargs)
    
    # Cloudinary URL methods
    def get_cover_url(self):
        """Get optimized cover image URL"""
        if self.cover_image:
            return self.cover_image.build_url(
                width=400,
                height=600,
                crop='fill',
                quality='auto:good'
            )
        return None
    
    def get_thumbnail_url(self):
        """Get thumbnail URL"""
        if self.thumbnail:
            return self.thumbnail.build_url(
                width=150,
                height=200,
                crop='fill',
                quality='auto:good'
            )
        elif self.cover_image:
            # Generate thumbnail from cover
            return self.cover_image.build_url(
                width=150,
                height=200,
                crop='fill',
                quality='auto:good'
            )
        return None
    
    def get_book_file_url(self):
        """Get direct download URL for book file"""
        if self.book_file:
            return self.book_file.url
        return None
    
    def increment_download(self):
        """Increment download counter"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    def is_pdf(self):
        """Check if book is PDF"""
        return self.file_format and self.file_format.lower() == 'pdf'