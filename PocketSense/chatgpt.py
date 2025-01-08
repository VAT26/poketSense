# Django REST Framework Implementation for PocketSense
# Key Features: Authentication, Expense Management, Groups, Settlements, Advanced Features

# 1. SETTINGS
# settings.py configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

AUTH_USER_MODEL = 'core.StudentUser'

# 2. MODELS
from django.contrib.auth.models import AbstractUser
from django.db import models

class StudentUser(AbstractUser):
    college = models.CharField(max_length=255)
    semester = models.IntegerField()
    default_payment_methods = models.CharField(max_length=255)

class Category(models.Model):
    name = models.CharField(max_length=100)

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    members = models.ManyToManyField(StudentUser)

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    split_type = models.CharField(max_length=50, choices=[('equal', 'Equal'), ('percentage', 'Percentage')])
    date = models.DateField(auto_now_add=True)
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    created_by = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)

class Settlement(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    settlement_method = models.CharField(max_length=100)
    due_date = models.DateField()
    settled_by = models.ForeignKey(StudentUser, on_delete=models.SET_NULL, null=True)

# 3. SERIALIZERS
from rest_framework import serializers

class StudentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        fields = ['id', 'username', 'email', 'college', 'semester', 'default_payment_methods']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = '__all__'

# 4. VIEWS
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    permission_classes = [IsAuthenticated]

# 5. ROUTES
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'settlements', SettlementViewSet, basename='settlement')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]

# 6. ADDITIONAL FEATURES
# Example: Smart Bill Scanning
from PIL import Image
import pytesseract

def process_receipt(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

# Example Usage:
# Upload an image via API, and extract text for categorization.

# 7. TESTING
# Use Django's test framework for unit tests to ensure functionality.
