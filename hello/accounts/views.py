from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from accounts.forms import (
    UserRegisterForm,
    UserUpdateFrom,
    ProfileUpdateForm,
    UserChangePasswordForm
)


def register_view(request, *args, **kwargs):
    context = {}
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('article:list')
    context['form'] = form
    return render(request, 'registration/register.html', context=context)


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'user_detail.html'
    context_object_name = 'user_obj'
    paginate_related_by = 5
    paginate_related_orphans = 0

    def get_context_data(self, **kwargs):
        articles = self.get_object().articles.all()
        paginator = Paginator(articles, self.paginate_related_by, orphans=self.paginate_related_orphans)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        kwargs['page_obj'] = page
        kwargs['articles'] = page.object_list
        kwargs['is_paginated'] = page.has_other_pages()
        return super().get_context_data(**kwargs)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования данных пользователя.

    Так как данные пользователя хранятся в двух моделях - в представлении
    используется две формы. Работа с формой модели пользователя осуществляется
    базовым фукнционалом предствления, для работы с формой профиля - используются самописные
    методы и расширение базового функционала представления
    """

    # Атрибуты для generic-предствления UpdateView
    model = get_user_model()
    template_name = 'user_update.html'
    context_object_name = 'user_obj'
    form_class = UserUpdateFrom

    # Атрибуты для самописных методов для работы с формой модели Profile
    profile_form_class = ProfileUpdateForm

    def post(self, request, *args, **kwargs):
        # 1. Получаем объект пользователя и устанавливаем в свойство объекта представления
        self.object = self.get_object()

        # 2. Получаем форму для редактированя данных, хранящихся в
        # модели пользователя
        user_form = self.get_form()
        # 3. Получаем форму для редактированя данных, хранящихся в
        # модели профиля
        profile_form = self.get_profile_form()

        if user_form.is_valid() and profile_form.is_valid():
            # 7. В случае, если обе формы валидны - вызываем метод form_valid и возвращаем
            # ответ, который вернёт данный метод
            return self.form_valid(user_form, profile_form)

        # 11. Если формы не валидны - возвращаем ответ, который вернёт метод from_invalid
        return self.form_invalid(user_form, profile_form)

    def get_object(self, queryset=None):
        """
        Метод для получения объекта пользователя.

        Так как редактирвоание происходит только пользователя из сессии -
        данный метод возвращает пользователя, который инициировал запрос на редактирование
        профиля.
        Пользователя получаем из объекта запроса
        """
        return self.request.user

    def get_context_data(self, **kwargs):
        """
        Метод для получения контекста, который будет переда в шаблон при его рендере при GET-запросе
        и POST-запросе в случае ошибки

        Базовая реализация не учитывает обработки двух форм, потому нам его также пришлось
        переопределить, чтобы подсунуть в контекст вторую форму
        """
        # 13. Получаем контест с помощью супер-метода get_context_data
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        # 14. Из kwargs, передаваемых в метод получаем форму профиля
        context['profile_form'] = kwargs.get('profile_form')
        if context['profile_form'] is None:
            # 15. если форма профиля не была пердана в kwargs (что говорит о том, что
            # запрос был сделан методом GET, так как в случае неудачного POST-запроса мы
            # передаём форму самостоятельно (см. шаг 12)) - получаем её объект с помощью
            # метода get_profile_form (в данном методе выполнится всё, кроме шага 5.) и
            # добаляем в словарь, который будет передан в контекст шаблона
            context['profile_form'] = self.get_profile_form()
        # 16. Возвращаем словарь с контестом шаблона
        return context

    def form_invalid(self, user_form, profile_form):
        """
        Переопределённый метод для обработки запроса, в случае, если форма не валидна
        (в нашем случае - две формы, форма редактирования данных пользователя и форма
        редактирвоания данных профиля пользователя).

        Стандартная реализация подразумевает обработку одной формы, потому мы переопределили
        данный метод и переписали таким образом, чтобы он принимал и обрабатывал две формы
        """
        # 12. получаем контекст шаблона используя метод get_context_data
        context = self.get_context_data(
            form=user_form,
            profile_form=profile_form
        )
        # 17. Возращаем ответ, который вернёт метод render_to_response.
        # Данный метод вернёт ответ с отрендеренным шаблоном с контекстом, который
        # мы вернули из метода get_context_data
        return self.render_to_response(context)

    def form_valid(self, user_form, profile_form):
        """
        Переопределённый метод для обработки запроса, в случае, если форма валидна
        (в нашем случае - две формы, форма редактирования данных пользователя и форма
        редактирвоания данных профиля пользователя).

        Стандартная реализация подразумевает обработку одной формы, потому мы переопределили
        данный метод и переписали таким образом, чтобы он принимал и обрабатывал две формы
        """
        # 8. Вызываем супер-метод, который обработает форму пользователя (если
        # быть точнее, то сохранит данные формы редактирования пользователя);
        # объект ответа, возвращаемый супер-методом сохраняем в переменную
        response = super(UserUpdateView, self).form_valid(user_form)

        # 9. Сохраняем данные формы редактированя профиля
        profile_form.save()
        # 10. Возвращаем ответ
        return response

    def get_profile_form(self):
        """
        Метод для получения объекта формы редактированя данных профиля пользователя
        """
        # 4. Инициализация словаря, элементы которого будут переданы в форму
        # редактирования профиля как kwargs.
        form_kwargs = {'instance': self.object.profile}

        if self.request.method == 'POST':
            # 5. В случае, если метод запроса POST - добавляем в словарь, который
            # хранит данные для инициализации формы данные из запроса, включая
            # файлы (напр., аватар пользователя)
            # Мы передаём все данные из обеих форм, поскольку формы не
            # "жадные" и "заберут" только данные для тех полей, которые
            # мы указали у данных форм
            form_kwargs['data'] = self.request.POST
            form_kwargs['files'] = self.request.FILES
        # 6. Создаём объект формы, используя словарь, который был объявлен выше,
        # распаковывая его в kwargs конструктора формы и возвращаем его (объект формы)

        return self.profile_form_class(**form_kwargs)

    def get_success_url(self):
        return reverse('accounts:user-detail', kwargs={'pk': self.object.pk})


class UserChangePasswordView(LoginRequiredMixin, UpdateView):
    template_name = 'user_change_password.html'
    model = get_user_model()
    form_class = UserChangePasswordForm
    context_object_name = 'user_obj'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super(UserChangePasswordView, self).form_valid(form)

        # Перед тем, как вернуть пользователю ответ - обновляем его сессию,
        # чтобы пользователя не разлогинивало после смены пароля
        update_session_auth_hash(self.request, self.request.user)
        return response

    def get_success_url(self):
        return reverse('accounts:user-detail', kwargs={'pk': self.object.pk})
