from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from rest_framework.authtoken.models import Token
from .models import Lead

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            Token.objects.get_or_create(user=user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    recent_leads = Lead.objects.all().order_by('-created_at')[:5]
    return render(request, 'dashboard.html', {
        'api_token': token.key,
        'recent_leads': recent_leads
    })


@login_required
def leads_list_view(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    statuses = Lead.StatusChoices.choices
    return render(request, 'leads/list.html', {
        'api_token': token.key,
        'statuses': statuses
    })


@login_required
def lead_create_view(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    statuses = Lead.StatusChoices.choices
    return render(request, 'leads/create.html', {
        'api_token': token.key,
        'statuses': statuses
    })


@login_required
def lead_detail_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    token, _ = Token.objects.get_or_create(user=request.user)
    statuses = Lead.StatusChoices.choices
    return render(request, 'leads/detail.html', {
        'lead': lead,
        'api_token': token.key,
        'statuses': statuses
    })


@login_required
def lead_edit_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    token, _ = Token.objects.get_or_create(user=request.user)
    statuses = Lead.StatusChoices.choices
    return render(request, 'leads/edit.html', {
        'lead': lead,
        'api_token': token.key,
        'statuses': statuses
    })
