
from django.contrib.auth.models import User
from django.db import models
import datetime

# Friend Relationship Model
class Friend(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='user_friends', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending')
    
    def __str__(self):
        return f'{self.user.username} - {self.friend.username} ({self.status})'
    def save(self, *args, **kwargs):
        if self.user == self.friend:
            raise ValueError("User cannot be friends with themselves.")
        super().save(*args, **kwargs)
    class Meta:
        # A unique constraint to ensure that friendship is bidirectional
        unique_together = ('user', 'friend')
# Transaction to Split Money
class Transaction(models.Model):
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount split
    description = models.TextField()  # Description of the split
    date = models.DateTimeField(auto_now_add=True)
    friend = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} paid {self.amount} to {self.friend.username} for {self.description}"

# Category-based Spending Analysis
class SpendingCategory(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Spending(models.Model):
    user = models.ForeignKey(User, related_name='spendings', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(SpendingCategory, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} spent {self.amount} on {self.category.name if self.category else 'Uncategorized'}"
