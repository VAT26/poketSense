from rest_framework import viewsets,serializers, status
from django.contrib import messages
from rest_framework.viewsets import ModelViewSet
from .serializers import SpendingSerializer,TransactionSerializer,FriendSerializer,SpendingCategorySerializer
from .forms import SignupForm,LoginForm
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Friend, Transaction, Spending, SpendingCategory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.db.models import Sum
from members.templatetags import custom_filters
from django.db.models import Q
from django.contrib.auth.models import User


def signup_view(request):
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Create a new user
            User.objects.create_user(username=username, email=email, password=password)
            return render(request, 'signup_success.html')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method=='POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Log in the user
                login(request, user)
                return redirect('dashboard')  # Redirect to a dashboard or home page
                
            else:
                # Invalid credentials
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    users = User.objects.exclude(id=request.user.id)
    
    user_friend_requests = {}
    friend = Friend.objects.filter(
    Q(user=request.user, status='accepted') | Q(friend=request.user, status='accepted')
    ).values('user', 'friend')

# Create a set of unique friends by eliminating reverse relationships (e.g., 1-2 and 2-1)
    friend_ids = set()
    for friendship in friend:
        if friendship['user'] != request.user.id:
            friend_ids.add(friendship['user'])
        if friendship['friend'] != request.user.id:
            friend_ids.add(friendship['friend'])
    print(friend_ids)
# Filter users to show only those who are actual friends
    friends = User.objects.filter(id__in=friend_ids)
    friends = set(friends)
    print(friends)
    # Get pending friend requests
    pending_requests = Friend.objects.filter(friend=request.user, status='pending')
    
    # Get recent transactions where the user is involved in money split (either as payer or receiver)
    transactions = Transaction.objects.filter(user=request.user) | Transaction.objects.filter(friend=request.user)
    
    # Get spending data for monthly analysis
    current_month = Spending.objects.filter(user=request.user, date__month=datetime.now().month)
    spending_by_category = current_month.values('category__name').annotate(total_spent=Sum('amount'))
    total_spent = current_month.aggregate(Sum('amount'))['amount__sum'] or 0

    
    return render(request, 'dashboard.html', {
        'users':users,
        'friends': friends,
        'pending_requests': pending_requests,
        'transactions': transactions,
        'user_friend_requests': friend_ids,
        'spending_by_category': spending_by_category,
        'total_spent': total_spent

    })
@login_required
def split_money(request):
    if request.method == 'POST':
        # Get split details from the form
        amount = float(request.POST.get('amount'))
        description = request.POST.get('description')
        friend_ids = request.POST.getlist('friends')  # List of friend IDs to split money among
        
        # Calculate individual share
        share = amount / (len(friend_ids) + 1)  # Including the logged-in user
        
        # Create transactions for each friend
        for friend_id in friend_ids:
            friend = User.objects.get(id=friend_id)
            Transaction.objects.create(
                user=request.user,
                friend=friend,
                amount=share,
                description=f"{friend}-{description}",
                #status='pending'  # Mark transaction as pending
            )

        messages.success(request, "Bill split successfully!")
        return redirect('dashboard')  # Redirect to the dashboard after splitting money

    # Get list of friends to show in the form
    friends = Friend.objects.filter(
        Q(user=request.user, status='accepted') | Q(friend=request.user, status='accepted')
    ).distinct()
    return render(request, 'split_money.html', {'friends': friends})

# @login_required
# def split_money(request):
#     if request.method == 'POST':
#         # Get split details from the form
#         amount = float(request.POST.get('amount'))
#         description = request.POST.get('description')
#         friend_ids = request.POST.getlist('friends')  # List of friend IDs to split money among
        
#         for friend_id in friend_ids:
#             friend = User.objects.get(id=friend_id)
#             # Create a transaction for the split
#             transaction = Transaction.objects.create(
#                 user=request.user,
#                 friend=friend,
#                 amount=amount / (len(friend_ids)+1),
#                 description=description
#             )
# 
        # return redirect('dashboard')  # Redirect to the dashboard after splitting money

    # Get list of friends to show in the form
    friends = Friend.objects.filter(user=request.user, status='accepted')
    return render(request, 'split_money.html', {'friends': friends})


@login_required
def send_friend_request(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)

    # Prevent sending a request to yourself
    if friend == request.user:
        messages.error(request, "You cannot send a friend request to yourself.")
        return redirect('dashboard')
    if Friend.objects.filter((Q(user=request.user, friend=friend) | Q(user=friend, friend=request.user)) & Q(status='accepted')).exists():
        messages.info(request, "You are already friends with this user.")
        return redirect('dashboard')
    
    # Check if a friend request already exists
    if Friend.objects.filter(user=request.user, friend=friend, status='accepted').exists():
        messages.info(request, "You already sent a friend request to this user.")
        return redirect('dashboard')
    else:
        # Create a new friend request
        friend_request = Friend.objects.create(user=request.user, friend=friend, status='pending')

        messages.success(request, "Friend request sent successfully.")

    return redirect('dashboard')


@login_required
def accept_friend_request(request, friend_id):
    friend_request = get_object_or_404(Friend, user=friend_id, friend=request.user, status='pending')
    friend_request.status = 'accepted'
    friend_request.save()
    #Friend.objects.get_or_create(user=request.user, friend=friend_request.user, status='accepted')
    return redirect('dashboard')



@login_required
def reject_friend_request(request, friend_id):
    friend_request = get_object_or_404(Friend, user=friend_id, friend=request.user, status='pending')
    friend_request.delete()
    return redirect('dashboard')

def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

class FriendListView(APIView):
    def get(self, request, format=None):
        friends = Friend.objects.filter(user=request.user, status='accepted')
        serializer = FriendSerializer(friends, many=True)
        return Response(serializer.data)

class TransactionCreateView(APIView):
    def post(self, request, format=None):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Attach user to the transaction
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MonthlySpendingAnalysisView(APIView):
    def get(self, request, format=None):
        current_month_spendings = Spending.objects.filter(user=request.user, date__month=datetime.datetime.now().month)
        spending_by_category = current_month_spendings.values('category__name').annotate(total_spent=Sum('amount'))
        
        return Response(spending_by_category, status=status.HTTP_200_OK)