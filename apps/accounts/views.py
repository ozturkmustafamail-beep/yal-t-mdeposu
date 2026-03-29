from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Address
from apps.logistics.models import City, District


def register_view(request):
    """Kullanıcı kayıt."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        phone = request.POST.get('phone', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Doğrulamalar
        errors = []
        if not username:
            errors.append('Kullanıcı adı gerekli.')
        if not email:
            errors.append('E-posta adresi gerekli.')
        if not password:
            errors.append('Şifre gerekli.')
        if password != password2:
            errors.append('Şifreler eşleşmiyor.')
        if len(password) < 6:
            errors.append('Şifre en az 6 karakter olmalı.')
        if CustomUser.objects.filter(username=username).exists():
            errors.append('Bu kullanıcı adı zaten kullanılıyor.')
        if CustomUser.objects.filter(email=email).exists():
            errors.append('Bu e-posta adresi zaten kayıtlı.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'cities': City.objects.all(),
            })

        # Kullanıcı oluştur
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            company_name=company_name,
            first_name=first_name,
            last_name=last_name,
        )

        # Adres kaydet (varsa)
        city_id = request.POST.get('city')
        district_id = request.POST.get('district')
        address_line = request.POST.get('address_line', '').strip()

        if city_id and district_id and address_line:
            try:
                city = City.objects.get(pk=city_id)
                district = District.objects.get(pk=district_id)
                Address.objects.create(
                    user=user,
                    title='İşyeri',
                    city=city,
                    district=district,
                    address_line=address_line,
                    is_default=True,
                )
                # Session'a da kaydet
                request.session['city_id'] = city.pk
                request.session['district_id'] = district.pk
            except (City.DoesNotExist, District.DoesNotExist):
                pass

        login(request, user)
        messages.success(request, f'Hoş geldiniz, {user.first_name or user.username}! Hesabınız oluşturuldu.')
        return redirect('products:home')

    return render(request, 'accounts/register.html', {
        'cities': City.objects.all(),
    })


def login_view(request):
    """Kullanıcı girişi."""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Default adres varsa session'a yükle
            default_addr = user.addresses.filter(is_default=True).first()
            if default_addr:
                request.session['city_id'] = default_addr.city.pk
                request.session['district_id'] = default_addr.district.pk

            messages.success(request, f'Hoş geldiniz, {user.first_name or user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Çıkış."""
    logout(request)
    messages.info(request, 'Çıkış yapıldı.')
    return redirect('products:home')


@login_required
def dashboard(request):
    """Kullanıcı paneli."""
    addresses = request.user.addresses.all()
    orders = request.user.orders.all()[:10]
    return render(request, 'accounts/dashboard.html', {
        'addresses': addresses,
        'orders': orders,
    })


@login_required
def add_address(request):
    """Adres ekle."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        city_id = request.POST.get('city')
        district_id = request.POST.get('district')
        address_line = request.POST.get('address_line', '').strip()
        is_default = request.POST.get('is_default') == 'on'

        try:
            city = City.objects.get(pk=city_id)
            district = District.objects.get(pk=district_id)

            Address.objects.create(
                user=request.user,
                title=title or 'Adres',
                city=city,
                district=district,
                address_line=address_line,
                is_default=is_default,
            )
            messages.success(request, 'Adres eklendi.')
        except (City.DoesNotExist, District.DoesNotExist):
            messages.error(request, 'Geçersiz il/ilçe.')

    return redirect('accounts:dashboard')


@login_required
def delete_address(request, pk):
    """Adres sil."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Adres silindi.')
    return redirect('accounts:dashboard')
