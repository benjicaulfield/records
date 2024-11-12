# schema.py
import graphene
from graphene_django import DjangoObjectType
from .models import Record, Seller, Listing

class RecordType(DjangoObjectType):
    class Meta:
        model = Record
        fields = "__all__"

class SellerType(DjangoObjectType):
    class Meta:
        model = Seller
        fields = "__all__"

class ListingType(DjangoObjectType):
    class Meta:
        model = Listing
        fields = "__all__"

class Query(graphene.ObjectType):
    records = graphene.List(RecordType)
    sellers = graphene.List(SellerType)
    listings = graphene.List(ListingType)
    record = graphene.Field(RecordType, id=graphene.ID(required=True))
    seller = graphene.Field(SellerType, id=graphene.ID(required=True))
    listing = graphene.Field(ListingType, id=graphene.ID(required=True))

    def resolve_records(self, info, **kwargs):
        return Record.objects.all()

    def resolve_sellers(self, info, **kwargs):
        return Seller.objects.all()

    def resolve_listings(self, info, **kwargs):
        return Listing.objects.all()

    def resolve_record(self, info, id):
        return Record.objects.get(id=id)

    def resolve_seller(self, info, id):
        return Seller.objects.get(id=id)

    def resolve_listing(self, info, id):
        return Listing.objects.get(id=id)

schema = graphene.Schema(query=Query)