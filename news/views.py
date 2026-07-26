from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from news.forms import (
    RedactorCreationForm,
    RedactorYearsOfExperienceUpdateForm,
    NewspaperForm,
    NewspaperSearchForm,
    RedactorSearchForm,
    TopicSearchForm,
    PublicSignUpForm,
)
from news.models import Topic, Newspaper, Redactor


@login_required
def index(request):
    num_redactors = Redactor.objects.count()
    num_newspapers = Newspaper.objects.count()
    num_topics = Topic.objects.count()

    request.user.visit_count += 1
    request.user.save(update_fields=["visit_count"])

    context = {
        "num_redactors": num_redactors,
        "num_newspapers": num_newspapers,
        "num_topics": num_topics,
        "num_visits": request.user.visit_count,
    }
    return render(request, "news/index.html", context=context)


class StaffRequiredMixin(UserPassesTestMixin):
    """Only staff (actual redactors) can create/edit/delete content."""

    def test_func(self):
        return self.request.user.is_staff


class SignUpView(generic.CreateView):
    model = Redactor
    form_class = PublicSignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    context_object_name = "topic_list"
    template_name = "news/topic_list.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TopicSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Topic.objects.all()
        form = TopicSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class TopicCreateView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.CreateView
):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("news:topic-list")


class TopicUpdateView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.UpdateView
):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("news:topic-list")


class TopicDeleteView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.DeleteView
):
    model = Topic
    success_url = reverse_lazy("news:topic-list")


class NewspaperListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Newspaper
    paginate_by = 5
    queryset = Newspaper.objects.all().select_related("topic")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        context["search_form"] = NewspaperSearchForm(initial={"title": title})
        topic_id = self.request.GET.get("topic")
        if topic_id:
            context["selected_topic"] = Topic.objects.filter(
                pk=topic_id,
            ).first()
        return context

    def get_queryset(self):
        queryset = Newspaper.objects.all().select_related("topic")
        form = NewspaperSearchForm(self.request.GET)
        if form.is_valid():
            queryset = queryset.filter(
                title__icontains=form.cleaned_data["title"],
            )
        topic_id = self.request.GET.get("topic")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        return queryset


class NewspaperDetailView(LoginRequiredMixin, generic.DetailView):
    model = Newspaper


class NewspaperCreateView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.CreateView
):
    model = Newspaper
    form_class = NewspaperForm
    success_url = reverse_lazy("news:newspaper-list")


class NewspaperUpdateView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.UpdateView
):
    model = Newspaper
    form_class = NewspaperForm
    success_url = reverse_lazy("news:newspaper-list")


class NewspaperDeleteView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.DeleteView
):
    model = Newspaper
    success_url = reverse_lazy("news:newspaper-list")


class RedactorListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form"] = RedactorSearchForm(
            initial={"username": username},
        )
        return context

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        form = RedactorSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                username__icontains=form.cleaned_data["username"],
            )
        return queryset


class RedactorDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.all().prefetch_related(
        "newspapers__topic",
    )


class RedactorCreateView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.CreateView
):
    model = get_user_model()
    form_class = RedactorCreationForm
    success_url = reverse_lazy("news:redactor-list")


class RedactorUpdateView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.UpdateView
):
    model = get_user_model()
    form_class = RedactorYearsOfExperienceUpdateForm
    template_name = "news/redactor_experience_update_form.html"
    success_url = reverse_lazy("news:redactor-list")


class RedactorDeleteView(
    LoginRequiredMixin,
    StaffRequiredMixin,
    generic.DeleteView
):
    model = get_user_model()
    success_url = reverse_lazy("news:redactor-list")
