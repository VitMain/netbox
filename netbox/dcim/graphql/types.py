from typing import Annotated, List, TYPE_CHECKING, Union

import strawberry
import strawberry_django

from core.graphql.mixins import ChangelogMixin
from dcim import models
from extras.graphql.mixins import (
    ConfigContextMixin,
    ContactsMixin,
    CustomFieldsMixin,
    ImageAttachmentsMixin,
    TagsMixin,
)
from ipam.graphql.mixins import IPAddressesMixin, VLANGroupsMixin
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import BaseObjectType, NetBoxObjectType, OrganizationalObjectType
from .filters import *
from .mixins import CabledObjectMixin, PathEndpointMixin

if TYPE_CHECKING:
    from circuits.graphql.types import CircuitTerminationType
    from extras.graphql.types import ConfigTemplateType
    from ipam.graphql.types import (
        ASNType,
        IPAddressType,
        PrefixType,
        ServiceType,
        VLANTranslationPolicyType,
        VLANType,
        VRFType,
    )
    from tenancy.graphql.types import TenantType
    from users.graphql.types import UserType
    from virtualization.graphql.types import ClusterType, VMInterfaceType, VirtualMachineType
    from vpn.graphql.types import L2VPNTerminationType
    from wireless.graphql.types import WirelessLANType, WirelessLinkType

__all__ = (
    'CableType',
    'ComponentType',
    'ConsolePortType',
    'ConsolePortTemplateType',
    'ConsoleServerPortType',
    'ConsoleServerPortTemplateType',
    'DeviceType',
    'DeviceBayType',
    'DeviceBayTemplateType',
    'DeviceRoleType',
    'DeviceTypeType',
    'FrontPortType',
    'FrontPortTemplateType',
    'InterfaceType',
    'InterfaceTemplateType',
    'InventoryItemType',
    'InventoryItemRoleType',
    'InventoryItemTemplateType',
    'LocationType',
    'MACAddressType',
    'ManufacturerType',
    'ModularComponentType',
    'ModuleType',
    'ModuleBayType',
    'ModuleBayTemplateType',
    'ModuleTypeProfileType',
    'ModuleTypeType',
    'PlatformType',
    'PowerFeedType',
    'PowerOutletType',
    'PowerOutletTemplateType',
    'PowerPanelType',
    'PowerPortType',
    'PowerPortTemplateType',
    'RackType',
    'RackReservationType',
    'RackRoleType',
    'RackTypeType',
    'RearPortType',
    'RearPortTemplateType',
    'RegionType',
    'SiteType',
    'SiteGroupType',
    'VirtualChassisType',
    'VirtualDeviceContextType',
)


#
# Base types
#


@strawberry.type
class ComponentType(
    ChangelogMixin,
    CustomFieldsMixin,
    TagsMixin,
    BaseObjectType
):
    """
    Base type for device/VM components
    """
    device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]


@strawberry.type
class ModularComponentType(ComponentType):
    module: Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')] | None


@strawberry.type
class ComponentTemplateType(
    ChangelogMixin,
    BaseObjectType
):
    """
    Base type for device/VM components
    """
    device_type: Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')]


@strawberry.type
class ModularComponentTemplateType(ComponentTemplateType):
    """
    Base type for ComponentTemplateModel which supports optional assignment to a ModuleType.
    """
    device_type: Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')] | None
    module_type: Annotated["ModuleTypeType", strawberry.lazy('dcim.graphql.types')] | None

#
# Model types
#


@strawberry_django.type(
    models.CableTermination,
    exclude=['termination_type', 'termination_id', '_device', '_rack', '_location', '_site'],
    filters=CableTerminationFilter,
    pagination=True
)
class CableTerminationType(NetBoxObjectType):
    cable: Annotated["CableType", strawberry.lazy('dcim.graphql.types')] | None
    termination: Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("CableTerminationTerminationType")] | None


@strawberry_django.type(
    models.Cable,
    fields='__all__',
    filters=CableFilter,
    pagination=True
)
class CableType(NetBoxObjectType):
    color: str
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    terminations: List[CableTerminationType]

    a_terminations: List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("CableTerminationTerminationType")]]

    b_terminations: List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("CableTerminationTerminationType")]]


@strawberry_django.type(
    models.ConsolePort,
    exclude=['_path'],
    filters=ConsolePortFilter,
    pagination=True
)
class ConsolePortType(ModularComponentType, CabledObjectMixin, PathEndpointMixin):
    pass


@strawberry_django.type(
    models.ConsolePortTemplate,
    fields='__all__',
    filters=ConsolePortTemplateFilter,
    pagination=True
)
class ConsolePortTemplateType(ModularComponentTemplateType):
    pass


@strawberry_django.type(
    models.ConsoleServerPort,
    exclude=['_path'],
    filters=ConsoleServerPortFilter,
    pagination=True
)
class ConsoleServerPortType(ModularComponentType, CabledObjectMixin, PathEndpointMixin):
    pass


@strawberry_django.type(
    models.ConsoleServerPortTemplate,
    fields='__all__',
    filters=ConsoleServerPortTemplateFilter,
    pagination=True
)
class ConsoleServerPortTemplateType(ModularComponentTemplateType):
    pass


@strawberry_django.type(
    models.Device,
    fields='__all__',
    filters=DeviceFilter,
    pagination=True
)
class DeviceType(ConfigContextMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    console_port_count: BigInt
    console_server_port_count: BigInt
    power_port_count: BigInt
    power_outlet_count: BigInt
    interface_count: BigInt
    front_port_count: BigInt
    rear_port_count: BigInt
    device_bay_count: BigInt
    module_bay_count: BigInt
    inventory_item_count: BigInt
    config_template: Annotated["ConfigTemplateType", strawberry.lazy('extras.graphql.types')] | None
    device_type: Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')]
    role: Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    platform: Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')] | None
    site: Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]
    location: Annotated["LocationType", strawberry.lazy('dcim.graphql.types')] | None
    rack: Annotated["RackType", strawberry.lazy('dcim.graphql.types')] | None
    primary_ip4: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None
    primary_ip6: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None
    oob_ip: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None
    cluster: Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')] | None
    virtual_chassis: Annotated["VirtualChassisType", strawberry.lazy('dcim.graphql.types')] | None

    virtual_machines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    modules: List[Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')]]
    interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    rearports: List[Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')]]
    consoleports: List[Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')]]
    powerports: List[Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')]]
    cabletermination_set: List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]
    consoleserverports: List[Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')]]
    poweroutlets: List[Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')]]
    frontports: List[Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')]]
    devicebays: List[Annotated["DeviceBayType", strawberry.lazy('dcim.graphql.types')]]
    modulebays: List[Annotated["ModuleBayType", strawberry.lazy('dcim.graphql.types')]]
    services: List[Annotated["ServiceType", strawberry.lazy('ipam.graphql.types')]]
    inventoryitems: List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]
    vdcs: List[Annotated["VirtualDeviceContextType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def vc_master_for(self) -> Annotated["VirtualChassisType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.vc_master_for if hasattr(self, 'vc_master_for') else None

    @strawberry_django.field
    def parent_bay(self) -> Annotated["DeviceBayType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent_bay if hasattr(self, 'parent_bay') else None


@strawberry_django.type(
    models.DeviceBay,
    fields='__all__',
    filters=DeviceBayFilter,
    pagination=True
)
class DeviceBayType(ComponentType):
    installed_device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None


@strawberry_django.type(
    models.DeviceBayTemplate,
    fields='__all__',
    filters=DeviceBayTemplateFilter,
    pagination=True
)
class DeviceBayTemplateType(ComponentTemplateType):
    pass


@strawberry_django.type(
    models.InventoryItemTemplate,
    exclude=['component_type', 'component_id', 'parent'],
    filters=InventoryItemTemplateFilter,
    pagination=True
)
class InventoryItemTemplateType(ComponentTemplateType):
    role: Annotated["InventoryItemRoleType", strawberry.lazy('dcim.graphql.types')] | None
    manufacturer: Annotated["ManufacturerType", strawberry.lazy('dcim.graphql.types')]

    @strawberry_django.field
    def parent(self) -> Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    child_items: List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]

    component: Annotated[Union[
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("InventoryItemTemplateComponentType")] | None


@strawberry_django.type(
    models.DeviceRole,
    fields='__all__',
    filters=DeviceRoleFilter,
    pagination=True
)
class DeviceRoleType(OrganizationalObjectType):
    parent: Annotated['DeviceRoleType', strawberry.lazy('dcim.graphql.types')] | None
    children: List[Annotated['DeviceRoleType', strawberry.lazy('dcim.graphql.types')]]
    color: str
    config_template: Annotated["ConfigTemplateType", strawberry.lazy('extras.graphql.types')] | None

    virtual_machines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.DeviceType,
    fields='__all__',
    filters=DeviceTypeFilter,
    pagination=True
)
class DeviceTypeType(NetBoxObjectType):
    console_port_template_count: BigInt
    console_server_port_template_count: BigInt
    power_port_template_count: BigInt
    power_outlet_template_count: BigInt
    interface_template_count: BigInt
    front_port_template_count: BigInt
    rear_port_template_count: BigInt
    device_bay_template_count: BigInt
    module_bay_template_count: BigInt
    inventory_item_template_count: BigInt
    front_image: strawberry_django.fields.types.DjangoImageType | None
    rear_image: strawberry_django.fields.types.DjangoImageType | None
    manufacturer: Annotated["ManufacturerType", strawberry.lazy('dcim.graphql.types')]
    default_platform: Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')] | None

    frontporttemplates: List[Annotated["FrontPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    modulebaytemplates: List[Annotated["ModuleBayTemplateType", strawberry.lazy('dcim.graphql.types')]]
    instances: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    poweroutlettemplates: List[Annotated["PowerOutletTemplateType", strawberry.lazy('dcim.graphql.types')]]
    powerporttemplates: List[Annotated["PowerPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    inventoryitemtemplates: List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]
    rearporttemplates: List[Annotated["RearPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    consoleserverporttemplates: List[Annotated["ConsoleServerPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    interfacetemplates: List[Annotated["InterfaceTemplateType", strawberry.lazy('dcim.graphql.types')]]
    devicebaytemplates: List[Annotated["DeviceBayTemplateType", strawberry.lazy('dcim.graphql.types')]]
    consoleporttemplates: List[Annotated["ConsolePortTemplateType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.FrontPort,
    fields='__all__',
    filters=FrontPortFilter,
    pagination=True
)
class FrontPortType(ModularComponentType, CabledObjectMixin):
    color: str
    rear_port: Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')]


@strawberry_django.type(
    models.FrontPortTemplate,
    fields='__all__',
    filters=FrontPortTemplateFilter,
    pagination=True
)
class FrontPortTemplateType(ModularComponentTemplateType):
    color: str
    rear_port: Annotated["RearPortTemplateType", strawberry.lazy('dcim.graphql.types')]


@strawberry_django.type(
    models.MACAddress,
    exclude=['assigned_object_type', 'assigned_object_id'],
    filters=MACAddressFilter,
    pagination=True
)
class MACAddressType(NetBoxObjectType):
    mac_address: str

    @strawberry_django.field
    def assigned_object(self) -> Annotated[Union[
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["VMInterfaceType", strawberry.lazy('virtualization.graphql.types')],
    ], strawberry.union("MACAddressAssignmentType")] | None:
        return self.assigned_object


@strawberry_django.type(
    models.Interface,
    exclude=['_path'],
    filters=InterfaceFilter,
    pagination=True
)
class InterfaceType(IPAddressesMixin, ModularComponentType, CabledObjectMixin, PathEndpointMixin):
    _name: str
    wwn: str | None
    parent: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')] | None
    bridge: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')] | None
    lag: Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')] | None
    wireless_link: Annotated["WirelessLinkType", strawberry.lazy('wireless.graphql.types')] | None
    untagged_vlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    vrf: Annotated["VRFType", strawberry.lazy('ipam.graphql.types')] | None
    primary_mac_address: Annotated["MACAddressType", strawberry.lazy('dcim.graphql.types')] | None
    qinq_svlan: Annotated["VLANType", strawberry.lazy('ipam.graphql.types')] | None
    vlan_translation_policy: Annotated["VLANTranslationPolicyType", strawberry.lazy('ipam.graphql.types')] | None
    l2vpn_termination: Annotated["L2VPNTerminationType", strawberry.lazy('vpn.graphql.types')] | None

    vdcs: List[Annotated["VirtualDeviceContextType", strawberry.lazy('dcim.graphql.types')]]
    tagged_vlans: List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]
    bridge_interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    wireless_lans: List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]
    member_interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    child_interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    mac_addresses: List[Annotated["MACAddressType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.InterfaceTemplate,
    fields='__all__',
    filters=InterfaceTemplateFilter,
    pagination=True
)
class InterfaceTemplateType(ModularComponentTemplateType):
    _name: str
    bridge: Annotated["InterfaceTemplateType", strawberry.lazy('dcim.graphql.types')] | None

    bridge_interfaces: List[Annotated["InterfaceTemplateType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.InventoryItem,
    exclude=['component_type', 'component_id', 'parent'],
    filters=InventoryItemFilter,
    pagination=True
)
class InventoryItemType(ComponentType):
    role: Annotated["InventoryItemRoleType", strawberry.lazy('dcim.graphql.types')] | None
    manufacturer: Annotated["ManufacturerType", strawberry.lazy('dcim.graphql.types')] | None

    child_items: List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def parent(self) -> Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    component: Annotated[Union[
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("InventoryItemComponentType")] | None


@strawberry_django.type(
    models.InventoryItemRole,
    fields='__all__',
    filters=InventoryItemRoleFilter,
    pagination=True
)
class InventoryItemRoleType(OrganizationalObjectType):
    color: str

    inventory_items: List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]
    inventory_item_templates: List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.Location,
    # fields='__all__',
    exclude=['parent'],  # bug - temp
    filters=LocationFilter,
    pagination=True
)
class LocationType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, OrganizationalObjectType):
    site: Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    parent: Annotated["LocationType", strawberry.lazy('dcim.graphql.types')] | None

    powerpanel_set: List[Annotated["PowerPanelType", strawberry.lazy('dcim.graphql.types')]]
    cabletermination_set: List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]
    racks: List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    children: List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.Manufacturer,
    fields='__all__',
    filters=ManufacturerFilter,
    pagination=True
)
class ManufacturerType(OrganizationalObjectType, ContactsMixin):

    platforms: List[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]
    device_types: List[Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')]]
    inventory_item_templates: List[Annotated["InventoryItemTemplateType", strawberry.lazy('dcim.graphql.types')]]
    inventory_items: List[Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')]]
    module_types: List[Annotated["ModuleTypeType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.Module,
    fields='__all__',
    filters=ModuleFilter,
    pagination=True
)
class ModuleType(NetBoxObjectType):
    device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]
    module_bay: Annotated["ModuleBayType", strawberry.lazy('dcim.graphql.types')]
    module_type: Annotated["ModuleTypeType", strawberry.lazy('dcim.graphql.types')]

    interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
    powerports: List[Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')]]
    consoleserverports: List[Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')]]
    consoleports: List[Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')]]
    poweroutlets: List[Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')]]
    rearports: List[Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')]]
    frontports: List[Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.ModuleBay,
    # fields='__all__',
    exclude=['parent'],
    filters=ModuleBayFilter,
    pagination=True
)
class ModuleBayType(ModularComponentType):

    installed_module: Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')] | None
    children: List[Annotated["ModuleBayType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def parent(self) -> Annotated["ModuleBayType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent


@strawberry_django.type(
    models.ModuleBayTemplate,
    fields='__all__',
    filters=ModuleBayTemplateFilter,
    pagination=True
)
class ModuleBayTemplateType(ModularComponentTemplateType):
    pass


@strawberry_django.type(
    models.ModuleTypeProfile,
    fields='__all__',
    filters=ModuleTypeProfileFilter,
    pagination=True
)
class ModuleTypeProfileType(NetBoxObjectType):
    module_types: List[Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.ModuleType,
    fields='__all__',
    filters=ModuleTypeFilter,
    pagination=True
)
class ModuleTypeType(NetBoxObjectType):
    profile: Annotated["ModuleTypeProfileType", strawberry.lazy('dcim.graphql.types')] | None
    manufacturer: Annotated["ManufacturerType", strawberry.lazy('dcim.graphql.types')]

    frontporttemplates: List[Annotated["FrontPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    consoleserverporttemplates: List[Annotated["ConsoleServerPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    interfacetemplates: List[Annotated["InterfaceTemplateType", strawberry.lazy('dcim.graphql.types')]]
    powerporttemplates: List[Annotated["PowerPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    poweroutlettemplates: List[Annotated["PowerOutletTemplateType", strawberry.lazy('dcim.graphql.types')]]
    rearporttemplates: List[Annotated["RearPortTemplateType", strawberry.lazy('dcim.graphql.types')]]
    instances: List[Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')]]
    consoleporttemplates: List[Annotated["ConsolePortTemplateType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.Platform,
    fields='__all__',
    filters=PlatformFilter,
    pagination=True
)
class PlatformType(OrganizationalObjectType):
    manufacturer: Annotated["ManufacturerType", strawberry.lazy('dcim.graphql.types')] | None
    config_template: Annotated["ConfigTemplateType", strawberry.lazy('extras.graphql.types')] | None

    virtual_machines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.PowerFeed,
    exclude=['_path'],
    filters=PowerFeedFilter,
    pagination=True
)
class PowerFeedType(NetBoxObjectType, CabledObjectMixin, PathEndpointMixin):
    power_panel: Annotated["PowerPanelType", strawberry.lazy('dcim.graphql.types')]
    rack: Annotated["RackType", strawberry.lazy('dcim.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None


@strawberry_django.type(
    models.PowerOutlet,
    exclude=['_path'],
    filters=PowerOutletFilter,
    pagination=True
)
class PowerOutletType(ModularComponentType, CabledObjectMixin, PathEndpointMixin):
    power_port: Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')] | None
    color: str


@strawberry_django.type(
    models.PowerOutletTemplate,
    fields='__all__',
    filters=PowerOutletTemplateFilter,
    pagination=True
)
class PowerOutletTemplateType(ModularComponentTemplateType):
    power_port: Annotated["PowerPortTemplateType", strawberry.lazy('dcim.graphql.types')] | None


@strawberry_django.type(
    models.PowerPanel,
    fields='__all__',
    filters=PowerPanelFilter,
    pagination=True
)
class PowerPanelType(NetBoxObjectType, ContactsMixin):
    site: Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]
    location: Annotated["LocationType", strawberry.lazy('dcim.graphql.types')] | None

    powerfeeds: List[Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.PowerPort,
    exclude=['_path'],
    filters=PowerPortFilter,
    pagination=True
)
class PowerPortType(ModularComponentType, CabledObjectMixin, PathEndpointMixin):

    poweroutlets: List[Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.PowerPortTemplate,
    fields='__all__',
    filters=PowerPortTemplateFilter,
    pagination=True
)
class PowerPortTemplateType(ModularComponentTemplateType):
    poweroutlet_templates: List[Annotated["PowerOutletTemplateType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.RackType,
    fields='__all__',
    filters=RackTypeFilter,
    pagination=True
)
class RackTypeType(NetBoxObjectType):
    manufacturer: Annotated["ManufacturerType", strawberry.lazy('dcim.graphql.types')]


@strawberry_django.type(
    models.Rack,
    fields='__all__',
    filters=RackFilter,
    pagination=True
)
class RackType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    site: Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]
    location: Annotated["LocationType", strawberry.lazy('dcim.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    role: Annotated["RackRoleType", strawberry.lazy('dcim.graphql.types')] | None

    rack_type: Annotated["RackTypeType", strawberry.lazy('dcim.graphql.types')] | None
    reservations: List[Annotated["RackReservationType", strawberry.lazy('dcim.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    powerfeeds: List[Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')]]
    cabletermination_set: List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.RackReservation,
    fields='__all__',
    filters=RackReservationFilter,
    pagination=True
)
class RackReservationType(NetBoxObjectType):
    units: List[int]
    rack: Annotated["RackType", strawberry.lazy('dcim.graphql.types')]
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')]


@strawberry_django.type(
    models.RackRole,
    fields='__all__',
    filters=RackRoleFilter,
    pagination=True
)
class RackRoleType(OrganizationalObjectType):
    color: str

    racks: List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.RearPort,
    fields='__all__',
    filters=RearPortFilter,
    pagination=True
)
class RearPortType(ModularComponentType, CabledObjectMixin):
    color: str

    frontports: List[Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.RearPortTemplate,
    fields='__all__',
    filters=RearPortTemplateFilter,
    pagination=True
)
class RearPortTemplateType(ModularComponentTemplateType):
    color: str

    frontport_templates: List[Annotated["FrontPortTemplateType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.Region,
    exclude=['parent'],
    filters=RegionFilter,
    pagination=True
)
class RegionType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):

    sites: List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]
    children: List[Annotated["RegionType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def parent(self) -> Annotated["RegionType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.Site,
    fields='__all__',
    filters=SiteFilter,
    pagination=True
)
class SiteType(VLANGroupsMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    time_zone: str | None
    region: Annotated["RegionType", strawberry.lazy('dcim.graphql.types')] | None
    group: Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    prefixes: List[Annotated["PrefixType", strawberry.lazy('ipam.graphql.types')]]
    virtual_machines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    racks: List[Annotated["RackType", strawberry.lazy('dcim.graphql.types')]]
    cabletermination_set: List[Annotated["CableTerminationType", strawberry.lazy('dcim.graphql.types')]]
    powerpanel_set: List[Annotated["PowerPanelType", strawberry.lazy('dcim.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    locations: List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]
    asns: List[Annotated["ASNType", strawberry.lazy('ipam.graphql.types')]]
    circuit_terminations: List[Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]]
    clusters: List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]
    vlans: List[Annotated["VLANType", strawberry.lazy('ipam.graphql.types')]]

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.SiteGroup,
    exclude=['parent'],  # bug - temp
    filters=SiteGroupFilter,
    pagination=True
)
class SiteGroupType(VLANGroupsMixin, ContactsMixin, OrganizationalObjectType):

    sites: List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]
    children: List[Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')]]

    @strawberry_django.field
    def parent(self) -> Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')] | None:
        return self.parent

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.cluster_set.all()

    @strawberry_django.field
    def circuit_terminations(self) -> List[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')]
    ]:
        return self.circuit_terminations.all()


@strawberry_django.type(
    models.VirtualChassis,
    fields='__all__',
    filters=VirtualChassisFilter,
    pagination=True
)
class VirtualChassisType(NetBoxObjectType):
    member_count: BigInt
    master: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None

    members: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.VirtualDeviceContext,
    fields='__all__',
    filters=VirtualDeviceContextFilter,
    pagination=True
)
class VirtualDeviceContextType(NetBoxObjectType):
    device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
    primary_ip4: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None
    primary_ip6: Annotated["IPAddressType", strawberry.lazy('ipam.graphql.types')] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None

    interfaces: List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]
