from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from .models import *
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext_lazy as _

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

        # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable.
    return render(request, 'catalog/index.html', context=context)


class BookListView(ListView):
    model = Book
    paginate_by = 2

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context


class AuthorListView(ListView):
    model = Author
    paginate_by = 2


class BookDetailView(DetailView):
    model = Book


class AuthorDetailView(DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    model = BookInstance
    template_name = 'catalog/my_borrowed.html'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

    
class BorrowedBooksListView(PermissionRequiredMixin, ListView):
    model = BookInstance
    template_name = 'catalog/all_borrowed.html'
    permission_required = 'can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').all()

class BookInstanceUpdateView(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    fields = 'due_back',
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('catalog:borrowed')
    initial = {'due_back': datetime.date.today() + datetime.timedelta(weeks=3)}
    


