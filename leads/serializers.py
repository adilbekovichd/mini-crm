import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lead, LeadActivity

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class LeadActivitySerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()

    class Meta:
        model = LeadActivity
        fields = ['id', 'lead', 'user', 'user_display', 'action', 'old_status', 'new_status', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "System"


class LeadSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserMinimalSerializer(source='assigned_to', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'source',
            'note',
            'status',
            'status_display',
            'assigned_to',
            'assigned_to_detail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        val = value.strip() if value else ''
        if not val:
            raise serializers.ValidationError("Name is required and cannot be empty.")
        if len(val) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return val

    def validate_source(self, value):
        val = value.strip() if value else ''
        if not val:
            raise serializers.ValidationError("Source is required.")
        return val

    def validate_phone(self, value):
        if value:
            cleaned = value.strip()
            # Allow digits, +, -, spaces, parentheses
            if not re.match(r'^[+0-9\s\-()]{7,30}$', cleaned):
                raise serializers.ValidationError("Phone number format is invalid. It should contain 7-30 characters.")
            return cleaned
        return value

    def validate(self, attrs):
        # Either email or phone is strongly recommended
        email = attrs.get('email')
        phone = attrs.get('phone')
        instance = getattr(self, 'instance', None)

        cur_email = email if email is not None else (instance.email if instance else '')
        cur_phone = phone if phone is not None else (instance.phone if instance else '')

        if not cur_email and not cur_phone:
            raise serializers.ValidationError({
                "contact": "At least one contact method (email or phone) must be provided."
            })
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        lead = super().create(validated_data)
        LeadActivity.objects.create(
            lead=lead,
            user=user,
            action='CREATED',
            old_status='',
            new_status=lead.status,
            note=f"Lead created with status '{lead.get_status_display()}'"
        )
        return lead

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        lead = super().update(instance, validated_data)

        if old_status != new_status:
            LeadActivity.objects.create(
                lead=lead,
                user=user,
                action='STATUS_CHANGE',
                old_status=old_status,
                new_status=new_status,
                note=f"Status changed from '{dict(Lead.StatusChoices.choices).get(old_status, old_status)}' to '{dict(Lead.StatusChoices.choices).get(new_status, new_status)}'"
            )
        else:
            LeadActivity.objects.create(
                lead=lead,
                user=user,
                action='UPDATED',
                old_status=old_status,
                new_status=new_status,
                note="Lead details updated"
            )
        return lead
