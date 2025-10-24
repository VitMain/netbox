from rest_framework import serializers

from .features import NetBoxModelSerializer
from users.api.serializers_.mixins import OwnerMixin

__all__ = (
    'NestedGroupModelSerializer',
    'OrganizationalModelSerializer',
    'PrimaryModelSerializer',
)


class PrimaryModelSerializer(OwnerMixin, NetBoxModelSerializer):
    """
    Base serializer class for models inheriting from PrimaryModel.
    """
    pass


class NestedGroupModelSerializer(OwnerMixin, NetBoxModelSerializer):
    """
    Base serializer class for models inheriting from NestedGroupModel.
    """
    _depth = serializers.IntegerField(source='level', read_only=True)


class OrganizationalModelSerializer(OwnerMixin, NetBoxModelSerializer):
    """
    Base serializer class for models inheriting from OrganizationalModel.
    """
    pass
