from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import NestedGroupModelForm, NetBoxModelForm, OrganizationalModelForm, PrimaryModelForm
from tenancy.models import *
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField
from utilities.forms.rendering import FieldSet, ObjectAttribute

__all__ = (
    'ContactAssignmentForm',
    'ContactForm',
    'ContactGroupForm',
    'ContactRoleForm',
    'TenantForm',
    'TenantGroupForm',
)


#
# Tenants
#

class TenantGroupForm(NestedGroupModelForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=TenantGroup.objects.all(),
        required=False
    )

    fieldsets = (
        FieldSet('parent', 'name', 'slug', 'description', 'tags', name=_('Tenant Group')),
    )

    class Meta:
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'owner', 'comments', 'tags',
        ]


class TenantForm(PrimaryModelForm):
    slug = SlugField()
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=TenantGroup.objects.all(),
        required=False
    )

    fieldsets = (
        FieldSet('name', 'slug', 'group', 'description', 'tags', name=_('Tenant')),
    )

    class Meta:
        model = Tenant
        fields = (
            'name', 'slug', 'group', 'description', 'owner', 'comments', 'tags',
        )


#
# Contacts
#

class ContactGroupForm(NestedGroupModelForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=ContactGroup.objects.all(),
        required=False
    )

    fieldsets = (
        FieldSet('parent', 'name', 'slug', 'description', 'tags', name=_('Contact Group')),
    )

    class Meta:
        model = ContactGroup
        fields = ('parent', 'name', 'slug', 'description', 'owner', 'comments', 'tags')


class ContactRoleForm(OrganizationalModelForm):
    fieldsets = (
        FieldSet('name', 'slug', 'description', 'tags', name=_('Contact Role')),
    )

    class Meta:
        model = ContactRole
        fields = ('name', 'slug', 'description', 'owner', 'tags')


class ContactForm(PrimaryModelForm):
    groups = DynamicModelMultipleChoiceField(
        label=_('Groups'),
        queryset=ContactGroup.objects.all(),
        required=False
    )
    link = forms.URLField(
        label=_('Link'),
        assume_scheme='https',
        required=False,
    )

    fieldsets = (
        FieldSet(
            'groups', 'name', 'title', 'phone', 'email', 'address', 'link', 'description', 'tags',
            name=_('Contact')
        ),
    )

    class Meta:
        model = Contact
        fields = (
            'groups', 'name', 'title', 'phone', 'email', 'address', 'link', 'description', 'owner', 'comments', 'tags',
        )
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ContactAssignmentForm(NetBoxModelForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=ContactGroup.objects.all(),
        required=False,
        initial_params={
            'contact': '$contact'
        }
    )
    contact = DynamicModelChoiceField(
        label=_('Contact'),
        queryset=Contact.objects.all(),
        query_params={
            'group_id': '$group'
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=ContactRole.objects.all()
    )

    fieldsets = (
        FieldSet(ObjectAttribute('object'), 'group', 'contact', 'role', 'priority', 'tags'),
    )

    class Meta:
        model = ContactAssignment
        fields = (
            'object_type', 'object_id', 'group', 'contact', 'role', 'priority', 'tags'
        )
        widgets = {
            'object_type': forms.HiddenInput(),
            'object_id': forms.HiddenInput(),
        }
