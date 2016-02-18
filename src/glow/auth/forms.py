# -*- encoding: utf-8 -*-
'''
Created on 2012-3-26

@author: Neil
'''
from grnglow.glow.models.user import User
from grnglow.glow.models.album import Album
from grnglow.glow.auth import authenticate
from grnglow.glow.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36


class UserInfoEditForm(forms.ModelForm):
    '''
    用户修改个人信息的表单
    '''
    name = forms.RegexField(max_length=14, regex=r'^\S+$')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.name_hasExist = False
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ("name",)

    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            User.objects.get(name=name)
        except User.DoesNotExist:
            return name

        self.name_hasExist = True
        raise forms.ValidationError(_(u"该名号已存在"))

    def save(self, commit=True):
        self.user.name = self.cleaned_data["name"]
        if commit:
            self.user.save()
        return self.user


class AlbumCreationForm(forms.ModelForm):
    '''
    创建新相册
    '''
    topic = forms.CharField(max_length=32)
    caption = forms.Textarea()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Album
        fields = ("topic", "caption",)

    def clean_topic(self):
        topic = self.cleaned_data["topic"]
        if topic == "":
            raise forms.ValidationError(_(u"相册名称不能为空"))

        try:
            Album.objects.get(owner=self.user, topic=topic)
        except Album.DoesNotExist:
            return topic

        raise forms.ValidationError(_(u"已存在同名相册"))

    def clean_caption(self):
        return self.cleaned_data["caption"]

    def save(self, commit=True):
        topic = self.cleaned_data["topic"]
        caption = self.cleaned_data["caption"]
        album = Album(owner=self.user, topic=topic, caption=caption)
        self.user.album_count += 1  # 相册数加1
        if commit:
            album.save()
            self.user.save()
        return album


class AlbumInfoEditForm(forms.ModelForm):
    '''
    更新相册属性
    '''
    topic = forms.CharField(max_length=32)
    caption = forms.Textarea()

    def __init__(self, album, *args, **kwargs):
        self.album = album
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Album
        fields = ("topic", "caption",)

    def clean_topic(self):
        topic = self.cleaned_data["topic"]
        if topic == "":
            raise forms.ValidationError(_(u"相册名称不能为空"))

        try:
            album2 = Album.objects.get(owner=self.album.owner, topic=topic)
        except Album.DoesNotExist:
            return topic
        else:
            if album2.id == self.album.id:  # 与自身同名
                return topic

        raise forms.ValidationError(_(u"已存在同名相册"))

    def clean_caption(self):
        return self.cleaned_data["caption"]

    def save(self, commit=True):
        topic = self.cleaned_data["topic"]
        caption = self.cleaned_data["caption"]
        self.album.topic = topic
        self.album.caption = caption
        if commit:
            self.album.save()

        return self.album


class UserCreationForm(forms.ModelForm):
    """
    用户提交注册的表单，用来创建用户
    """
    email = forms.EmailField(label=_("email"))
    name = forms.RegexField(max_length=14, regex=r'^\S+$',
                            help_text=_(u"中、英文均可，最长14个英文或7个汉字"),  # 前面必须加u表示unicode，django输出默认用unicode编码
                            error_messages={'invalid': _(u"仅可以使用中文或英文")})
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    city = forms.CharField(label=_("city"))

    def __init__(self, *args, **kwargs):
        self.name_hasExist = False
        self.email_hasExist = False
        self.password_notMatch = True
        super(forms.ModelForm, self).__init__(*args, **kwargs)  # 必须调用父类初始化其它数据

    class Meta:
        model = User
        fields = ("name", "email", "city",)

    # clean函数会按顺序自动执行
    def clean_name(self):
        name = self.cleaned_data["name"]
        try:
            User.objects.get(name=name)
        except User.DoesNotExist:
            return name

        self.name_hasExist = True
        raise forms.ValidationError(_(u"该名号已存在"))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_(u"两次输入的密码不一致"))

        self.password_notMatch = False
        return password2

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        self.email_hasExist = True
        raise forms.ValidationError(_(u"该邮箱已存在"))

    def clean_city(self):
        city = self.cleaned_data["city"]
        return city

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    name = forms.RegexField(label=_("name"), max_length=14, regex=r'^\S+$',
                            help_text=_("中、英文均可，最长14个英文或7个汉字"),
                            error_messages={'invalid': _("仅可以使用中文或英文")})
    email = forms.EmailField(label=_("email"))
    city = forms.CharField(label=_("city"), widget=forms.Select)

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    email/password logins.
    """
    email = forms.EmailField(label=_("email"))
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    _("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(
                    _("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))

        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        """
        Validates that an active user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(
            email__iexact=email,
            is_active=True
        )
        if len(self.users_cache) == 0:
            raise forms.ValidationError(
                _("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email

    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            send_mail(_("Password reset on %s") % site_name,
                      t.render(Context(c)), None, [user.email])


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set his/her password without
    entering the old password
    """
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.password_notMatch = True  # 两次输入的密码是否匹配的标记
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))

        self.password_notMatch = False
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.old_password_correct = False  # 旧密码是否正确的标记
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))

        self.old_password_correct = True
        return old_password


PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']
