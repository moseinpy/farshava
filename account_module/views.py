from jalali_date.templatetags.jalali_tags import to_jalali
from .models import Leave
import datetime
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views import View
from jalali_date import datetime2jalali
from .models import User, WorkLog, Employee
from account_module.forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, LeaveForm, \
    YearMonthForm
from django.utils.crypto import get_random_string
from django.http import Http404, HttpRequest
from django.contrib.auth import login, logout
from utils.email_service import send_email
from jalali_date import date2jalali
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import ListView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import Employee, WorkLog
from .forms import WorkLogForm

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


@method_decorator(login_required, name='dispatch')
class TableWorkLogView(TemplateView):
    template_name = 'account_module/table_work_log.html'
    form_class = WorkLogForm
    success_url = reverse_lazy('table-work-log')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        workplace_code = None
        if self.request.user.is_authenticated and current_user.employee.role == 'responsible':
            if hasattr(current_user, 'employee'):
                workplace_code = current_user.employee.workplace_code

            employees = Employee.objects.filter(workplace_code=workplace_code)
            current_year = datetime.date.today().year
            worklogs = WorkLog.objects.filter(employee__workplace_code=workplace_code).order_by('-year', '-month')
            years = range(1403, 1421)
            months = [
                ('فروردین', 'فروردین'),
                ('اردیبهشت', 'اردیبهشت'),
                ('خرداد', 'خرداد'),
                ('تیر', 'تیر'),
                ('مرداد', 'مرداد'),
                ('شهریور', 'شهریور'),
                ('مهر', 'مهر'),
                ('آبان', 'آبان'),
                ('آذر', 'آذر'),
                ('دی', 'دی'),
                ('بهمن', 'بهمن'),
                ('اسفند', 'اسفند')
            ]

            context.update({
                'employees': employees,
                'worklogs': worklogs,
                'years': years,
                'months': months,
                'form': WorkLogForm(workplace_code=workplace_code, years=years, months=months),
                'form_errors': None
            })
        else:
            context.update({
                'error_message': 'شما اجازه دسترسی به این فرم را ندارید.'
            })
        return context

    def post(self, request, *args, **kwargs):
        current_user = self.request.user
        workplace_code = None
        if hasattr(current_user, 'employee'):
            workplace_code = current_user.employee.workplace_code

        context = self.get_context_data()
        form = WorkLogForm(request.POST, workplace_code=workplace_code, years=context['years'], months=context['months'])

        if 'update_worklog' in request.POST:
            worklog_id = request.POST.get('worklog_id')
            worklog = WorkLog.objects.get(id=worklog_id)
            form = WorkLogForm(request.POST, instance=worklog, workplace_code=workplace_code, years=context['years'], months=context['months'])

            if form.is_valid():
                form.save()
            else:
                context['form_errors'] = form.errors
                context['form'] = form  # افزودن این خط برای ارسال فرم با خطاها به قالب
                return self.render_to_response(context)

        elif form.is_valid():
            worklog = form.save(commit=False)
            worklog.save()
        else:
            context['form_errors'] = form.errors
            context['form'] = form  # افزودن این خط برای ارسال فرم با خطاها به قالب
            return self.render_to_response(context)

        # برای به‌روز رسانی context پس از ارسال فرم
        context.update({
            'form': WorkLogForm(workplace_code=workplace_code, years=context['years'], months=context['months']),
            'worklogs': WorkLog.objects.filter(employee__workplace_code=workplace_code).order_by('-year', '-month'),
        })
        return self.render_to_response(context)



class AllWorkLogsView(ListView):
    model = WorkLog
    template_name = 'account_module/all_work_logs.html'
    context_object_name = 'worklogs'
    paginate_by = 80

    def get_queryset(self):
        queryset = WorkLog.objects.all()
        if self.request.user.is_authenticated:
            user_code_melli = self.request.user.employee.code_melli
            valid_list = ['2559110393']
            if user_code_melli in valid_list:
                queryset = queryset.order_by('-year', '-month')
            else:
                user_workplace_code = self.request.user.employee.workplace_code
                queryset = queryset.filter(employee__workplace_code=user_workplace_code).order_by('-year', '-month')

        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = YearMonthForm(self.request.GET)
        return context


# class AllWorkLogsView(ListView):
#     model = WorkLog
#     template_name = 'account_module/all_work_logs.html'
#     context_object_name = 'worklogs'
#     paginate_by = 10
#
#     def get_queryset(self):
#         today = datetime.date.today()
#         user_code_melli = self.request.user.employee.code_melli if self.request.user.is_authenticated else None
#         valid_list = ['2559110393']
#
#         # فیلتر بر اساس سال جاری
#         queryset = WorkLog.objects.all()
#
#         # اعمال شرط برای کاربران مختلف
#         if self.request.user.is_authenticated and user_code_melli in valid_list:
#             # اگر کاربر وارد شده و در لیست خاصی قرار دارد
#             queryset = queryset.all().order_by('-year', '-month')
#         else:
#             user_workplace_code = self.request.user.employee.workplace_code if self.request.user.is_authenticated else None
#             # اگر کاربر دیگری باشد یا در لیست خاصی نباشد
#             queryset = queryset.filter(employee__workplace_code=user_workplace_code).order_by('-year', '-month')
#
#         return queryset.order_by('-year', '-month')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         today = datetime.date.today()
#         context['past_year_jalali'] = today.strftime('%d-%m-%Y')
#         return context