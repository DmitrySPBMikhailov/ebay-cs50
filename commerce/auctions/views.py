from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from .forms import ListingCreateForm, ListingUpdateForm
from django.views.generic import DetailView
from .models import User, Listing, Category, Bid, WatchList, Comment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
import pytz


def index(request):
    # Copy request for filtering by categories
    get_query = request.GET.copy()
    cat = None
    if "filter" in get_query:
        # Check if category exists
        category_pk = get_query["filter"]
        try:
            cat = Category.objects.get(pk=category_pk)
            listings = Listing.objects.filter(active=True, category=cat.pk)
        except:
            listings = Listing.objects.filter(active=True)
    else:
        listings = Listing.objects.filter(active=True)
    queryset = []
    if request.user.is_authenticated:
        watch_list = WatchList.objects.filter(user=request.user).values_list(
            "item", flat=True
        )
        for listing in listings:
            for watch in watch_list:
                if watch == listing.pk:
                    listing.watch = True
                    break
                else:
                    listing.watch = False
            queryset.append(listing)

    if request.user.is_authenticated:
        context = {"listings": queryset, "cat": cat}
    else:
        context = {"listings": listings, "cat": cat}
    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class ListingCreateView(CreateView, LoginRequiredMixin):
    model = Listing
    form_class = ListingCreateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("index")


class ListingUpdateView(UpdateView, LoginRequiredMixin):
    model = Listing
    form_class = ListingUpdateForm
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        print("works")
        return super().form_valid(form)


class CategoryListView(ListView):
    model = Category


def get_time_limit():
    """We get range from now and 24 hours before

    function returns list: start date and end date
    """
    MoscowTz = pytz.timezone("Europe/Moscow")
    enddate = datetime.now(MoscowTz)
    startdate = enddate - timedelta(days=1)
    result = [startdate, enddate]
    return result


class ListingView(DetailView):
    model = Listing
    template_name = "auctions/listing_view.html"

    def get_context_data(self, **kwargs):
        data = super(ListingView, self).get_context_data(**kwargs)
        data["bid"] = Bid.objects.select_related().filter(item=self.object.pk).first()
        data["count_bids"] = (
            Bid.objects.select_related().filter(item=self.object.pk).count()
        )
        if self.request.user.is_authenticated:
            data["watch"] = WatchList.objects.select_related().filter(
                user=self.request.user, item=self.object
            )
        startdate, enddate = get_time_limit()
        data["recently"] = (
            WatchList.objects.select_related()
            .filter(created__range=[startdate, enddate], item=self.object)
            .count()
        )
        data["comments"] = Comment.objects.select_related().filter(item=self.object)
        return data


@login_required
def get_bid(request, pk):
    user = request.user
    listing = Listing.objects.get(pk=pk)
    # Check current user can't bid for his own listing
    if listing.user == user:
        messages.warning(request, "You can't bid for your own listing!")
        return redirect(listing.get_absolute_url())
    # Try to assign user's input to a variable
    try:
        sent_bid = float(request.POST["bid"])
    except:
        messages.warning(request, "Enter valid number")
        return redirect(listing.get_absolute_url())
    current_bid_obj = Bid.objects.select_related().filter(item=pk).first()
    # If this is a first bid for the item: it can be == to price or less
    if not current_bid_obj:
        if sent_bid > listing.price:
            messages.warning(request, "Your bid should be equal or less than the price")
            return redirect(listing.get_absolute_url())
    else:
        # The new bid should be greater than the current one
        if sent_bid <= current_bid_obj.price:
            messages.warning(
                request, "Your bid should be greater than the current one."
            )
            return redirect(listing.get_absolute_url())
    Bid.objects.create(user=user, price=sent_bid, item=listing)
    messages.success(request, "You have placed your bid. Good luck!")
    return redirect(listing.get_absolute_url())


@login_required
def add_to_watch_list(request, pk):
    listing = Listing.objects.get(pk=pk)
    WatchList.objects.create(user=request.user, item=listing)
    messages.success(request, "Added to watch list.")
    return redirect(listing.get_absolute_url())


@login_required
def remove_from_watch_list(request, pk):
    listing = Listing.objects.get(pk=pk)
    my_watch_item = WatchList.objects.get(user=request.user, item=listing)
    my_watch_item.delete()
    messages.success(request, "You have stopped following this item")
    return redirect(listing.get_absolute_url())


def show_watch_list(request):
    watch_list = WatchList.objects.filter(user=request.user)
    context = {"watch_list": watch_list}
    return render(request, "auctions/watch-list.html", context)


@login_required
def add_to_watch_list_htmx(request, pk):
    listing = Listing.objects.get(pk=pk)
    WatchList.objects.create(user=request.user, item=listing)
    listing = Listing.objects.get(pk=pk)
    listing.watch = True
    context = {"listing": listing}
    return render(request, "auctions/inner/inner_index.html", context)


@login_required
def remove_from_watch_list_htmx(request, pk):
    listing = Listing.objects.get(pk=pk)
    my_watch_item = WatchList.objects.get(user=request.user, item=listing)
    my_watch_item.delete()
    listing = Listing.objects.get(pk=pk)
    listing.watch = False
    context = {"listing": listing}
    return render(request, "auctions/inner/inner_index.html", context)


@login_required
def remove_from_watch_list_htmx_hard(request, pk):
    listing = Listing.objects.get(pk=pk)
    my_watch_item = WatchList.objects.get(user=request.user, item=listing)
    my_watch_item.delete()
    watch_list = WatchList.objects.filter(user=request.user)
    context = {"watch_list": watch_list}
    return render(request, "auctions/inner/inner_watch.html", context)


@login_required
def show_my_bids(request):
    # search list of Listings that user has bidded
    my_only_listing = set(
        Bid.objects.filter(user=request.user).values_list("item", flat=True)
    )
    my_only_listing = list(my_only_listing)

    # For each listing we have to find the most pricy value
    queryset = []
    for only in my_only_listing:
        bd = Bid.objects.select_related().filter(user=request.user, item=only).first()
        # check if this is the latest bid
        total_bd = Bid.objects.select_related().filter(item=only).first()
        if bd == total_bd:
            bd.leader = True
        else:
            bd.leader = False
        queryset.append(bd)

    context = {"my_bids": queryset}
    return render(request, "auctions/bids.html", context)


@login_required
def close_the_auction(request, pk):
    listing = Listing.objects.get(pk=pk)
    # Check if user the author of the listing
    if request.user != listing.user:
        messages.warning(request, "You are not the author of this listing")
        return redirect(listing.get_absolute_url())

    # Set listing to close
    listing.active = False

    # Find the user with the highest bid
    bid = Bid.objects.select_related().filter(item=listing).first()
    if bid:
        listing.winner = User.objects.get(pk=bid.user.pk)
        listing.sold_price = bid.price
    listing.save()
    messages.success(request, "You have closed the listing!")
    return redirect(listing.get_absolute_url())


@login_required
def add_comment(request, pk):
    listing = Listing.objects.get(pk=pk)
    sent_comment = request.POST["comment"]
    Comment.objects.create(item=listing, commentary=sent_comment, user=request.user)
    return redirect(listing.get_absolute_url())
