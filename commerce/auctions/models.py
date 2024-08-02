from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=256, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    followed = models.PositiveIntegerField(null=True, blank=True, default=0)
    image = models.ImageField(null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="listings_user"
    )
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="listing_winner",
        blank=True,
        null=True,
    )
    sold_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    def get_absolute_url(self):
        return reverse("ListingView", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created"]
        verbose_name = "Listing"
        verbose_name_plural = "Listings"


class WatchList(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    item = models.ForeignKey("Listing", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ["user"]
        verbose_name = "WatchList"
        verbose_name_plural = "WatchLists"

    def save(self, *args, **kwargs):
        # we have to find how many items in this instance have users
        my_listing = Listing.objects.get(pk=self.item.pk)
        my_watch_lists = WatchList.objects.filter(item=my_listing).count()
        my_listing.followed = my_watch_lists + 1
        my_listing.save()
        super(WatchList, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        my_listing = Listing.objects.get(pk=self.item.pk)
        my_watch_lists = WatchList.objects.filter(item=my_listing).count()
        my_listing.followed = my_watch_lists - 1
        my_listing.save()
        super(WatchList, self).delete(*args, **kwargs)


class Bid(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="bids_user")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    item = models.ForeignKey("Listing", on_delete=models.CASCADE)
    is_won = models.BooleanField(default=False)

    class Meta:
        ordering = ["-price"]
        verbose_name = "Bid"
        verbose_name_plural = "Bids"


class Comment(models.Model):
    item = models.ForeignKey(
        "Listing", on_delete=models.CASCADE, related_name="comments_listing"
    )
    commentary = models.TextField()
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
