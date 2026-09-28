from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Lead(models.Model):
    class StatusChoices(models.TextChoices):
        NEW = 'new', 'New'
        CONTACTED = 'contacted', 'Contacted'
        QUALIFIED = 'qualified', 'Qualified'
        WON = 'won', 'Won'
        LOST = 'lost', 'Lost'

    name = models.CharField(max_length=150, help_text="Lead full name or business name")
    phone = models.CharField(max_length=30, blank=True, help_text="Contact phone number")
    email = models.EmailField(blank=True, help_text="Contact email address")
    source = models.CharField(max_length=100, help_text="Acquisition channel (e.g. telegram, website, referral)")
    note = models.TextField(blank=True, help_text="Notes and additional context about the lead")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        db_index=True,
        help_text="Current qualification status of the lead"
    )
    assigned_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='leads',
        help_text="CRM user responsible for managing this lead"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'source']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class LeadActivity(models.Model):
    ACTION_CHOICES = (
        ('CREATED', 'Lead Created'),
        ('STATUS_CHANGE', 'Status Changed'),
        ('UPDATED', 'Lead Updated'),
        ('NOTE_ADDED', 'Note Added'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=50, default='STATUS_CHANGE')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lead.name}: {self.action} ({self.old_status} -> {self.new_status}) at {self.created_at}"
