from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer, ItemSerializer
from .models import Item, fetch_article


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = ItemSerializer
    model = Item

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)

    def pre_save(self, item):
        item.owner = self.request.user
        item.title, item.readable_article = fetch_article(item.url)
        try:
            original_item = self.model.objects.get(url=item.url, owner=item.owner)
        except self.model.DoesNotExist:
            pass
        else:
            item.id = original_item.id


    def post_save(self, item, *args, **kwargs):
        if type(item.tags) is list:
            # If tags were provided in the request
            saved_bookmark = Item.objects.get(pk=item.pk)
            for tag in item.tags:
                saved_bookmark.tags.add(tag)

