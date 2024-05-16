import datetime

from jalali_date.templatetags.jalali_tags import to_jalali
from .models import Leave
import datetime
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from jalali_date import datetime2jalali
from .models import User
from account_module.forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, LeaveForm
from django.utils.crypto import get_random_string
from django.http import Http404, HttpRequest
from django.contrib.auth import login, logout
from utils.email_service import send_email
from jalali_date import date2jalali

# Create your views here.

class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        context = {
            'register_form': register_form
        }
        return render(request, "account_module/register.html", context)

    def post(self, request: HttpRequest):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = register_form.cleaned_data.get('username')
            user_email = register_form.cleaned_data.get('email')
            user_password = register_form.cleaned_data.get('password')
            if User.objects.filter(Q(username__iexact=user_name) | Q(email__iexact=user_email)).exists():
                if User.objects.filter(username__iexact=user_name).exists():
                    register_form.add_error('username', "نام کاربری وارد شده تکراری می باشد.")
                elif User.objects.filter(email__iexact=user_email).exists():
                    register_form.add_error('email', "ایمیل وارد شده تکراری می باشد")
            else:
                new_user = User(
                    username=user_name,
                    email=user_email,
                    email_active_user=get_random_string(72),
                    is_active=False,
                )
                new_user.set_password(user_password)
                new_user.save()
                # todo: send email active code
                send_email("فعال سازی حساب کاربری", user_email,{'user': new_user},"emails/activate_account.html")
                return redirect(reverse('login_page'))
        context = {
            'register_form': register_form
        }
        return render(request, "account_module/register.html", context)


class LoginView(View):

    def get(self, request):
        login_form = LoginForm()
        context = {
            'login_form': login_form
        }
        return render(request, "account_module/login.html", context)

    def post(self, request: HttpRequest):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = login_form.cleaned_data.get('username')
            user_pass = login_form.cleaned_data.get('password')
            user: User = User.objects.filter(username__iexact=user_name).first()
            if user is not None:
                if not user.is_active:
                    # show error
                    login_form.add_error('username', "حساب کاربری شما فعال نمی باشد")
                else:
                    is_password_correct = user.check_password(user_pass)
                    if is_password_correct:
                        login(request, user)
                        return redirect(reverse('home_page'))
                    else:
                        login_form.add_error('password', "کلمه عبور اشتباه است")
            else:
                login_form.add_error('username', "کاربری با این مشخصات یافت نشد")

        context = {
            'login_form': login_form
        }
        return render(request, "account_module/login.html", context)


class ActivateAccountView(View):
    def get(self, request, email_active_user):
        user: User = User.objects.filter(email_active_user__iexact=email_active_user).first()
        if user is not None:
            if not user.is_active:
                user.is_active = True
                user.email_active_user = get_random_string(72)
                user.save()
                # todo: send success message
                return redirect(reverse('login_page'))
            else:
                # todo: send your account is active message
                pass

        raise Http404


class ForgetPasswordView(View):
    def get(self, request: HttpRequest):
        forget_pass_form = ForgotPasswordForm()
        context = {
            'forget_pass_form': forget_pass_form
        }
        return render(request, 'account_module/forgot_password.html', context)

    def post(self, request: HttpRequest):
        forget_pass_form = ForgotPasswordForm(request.POST)
        if forget_pass_form.is_valid():
            user_email = forget_pass_form.cleaned_data.get('email')
            user: User = User.objects.filter(email__iexact=user_email).first()
            if user is not None:
                send_email('فعال سازی حساب کاربری', user_email, {'user': user}, 'emails/forgot_password.html')
                return redirect(reverse('login_page'))
        context = {
            'forget_pass_form': forget_pass_form
        }
        return render(request, 'account_module/forgot_password.html', context)


class ResetPasswordView(View):
    def get(self, request: HttpRequest, active_code):
        user: User = User.objects.filter(email_active_user__iexact=active_code).first()
        if user is None:
            return redirect(reverse('login_page'))
        reset_pass_form = ResetPasswordForm()
        context = {
            'reset_pass_form': reset_pass_form,
            'user': user
        }
        return render(request, 'account_module/reset_password.html', context)

    def post(self, request: HttpRequest, active_code):
        reset_pass_form = ResetPasswordForm(request.POST)
        user: User = User.objects.filter(email_active_user__iexact=active_code).first()

        if reset_pass_form.is_valid():
            if user is None:
                return redirect(reverse('login_page'))
            user_new_pass = reset_pass_form.cleaned_data.get('password')  # type: UserNew
            user.set_password(user_new_pass)
            user.email_active_user = get_random_string(72)
            user.is_active = True
            user.save()
            # todo: send success message
            return redirect(reverse('login_page'))

        context = {
            'reset_pass_form': reset_pass_form,
            'user': user
        }
        return render(request, 'account_module/reset_password.html', context)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('login_page'))


def leave_request(request):
    jalali_join = datetime2jalali(request.user.date_joined).strftime('%y/%m/%d _ %H:%M:%S')
    user_workplace_code = request.user.employee.workplace_code if request.user.is_authenticated else None
    if request.method == 'POST':
        form = LeaveForm(request.POST, request.FILES, user_workplace_code=user_workplace_code)
        if form.is_valid():
            form.save()
            return redirect('all_leaves')  # Redirect to a success page
    else:
        form = LeaveForm(user_workplace_code=user_workplace_code)
    return render(request, 'account_module/leave_request.html', {'form': form})




def all_leaves(request):
    today = datetime.date.today()
    past_year_jalali = date2jalali(today - datetime.timedelta(days=365)).strftime('%d-%m-%Y')
    past_year = today - datetime.timedelta(days=365)
    user_code_melli = request.user.employee.code_melli if request.user.is_authenticated else None
    valid_list = ['2559110393']
    # leaves = Leave.objects.filter(start_date__gte=past_year).order_by('-start_date')
    if request.user.is_authenticated and user_code_melli in valid_list:
        # اگر کاربر وارد شده و در لیست خاصی قرار دارد
        leaves = Leave.objects.filter(start_date__gte=past_year).order_by('-start_date')
    else:
        user_workplace_code = request.user.employee.workplace_code if request.user.is_authenticated else None
        # اگر کاربر دیگری باشد یا در لیست خاصی نباشد
        leaves = Leave.objects.filter(start_date__gte=past_year, employee__workplace_code=user_workplace_code).order_by(
            '-start_date')

    context = {
        'leaves': leaves,
        'past_year_jalali': past_year_jalali,
    }
    return render(request, 'account_module/all_leaves.html', context)

