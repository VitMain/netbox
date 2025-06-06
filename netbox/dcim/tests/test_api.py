import json

from django.test import override_settings, tag
from django.urls import reverse
from django.utils.translation import gettext as _
from rest_framework import status

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.models import ConfigTemplate
from ipam.choices import VLANQinQRoleChoices
from ipam.models import ASN, RIR, VLAN, VRF
from netbox.api.serializers import GenericObjectSerializer
from tenancy.models import Tenant
from users.models import User
from utilities.testing import APITestCase, APIViewTestCases, create_test_device, disable_logging
from virtualization.models import Cluster, ClusterType
from wireless.choices import WirelessChannelChoices
from wireless.models import WirelessLAN


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('dcim-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class Mixins:

    class ComponentTraceMixin(APITestCase):
        peer_termination_type = None

        def test_trace(self):
            """
            Test tracing a device component's attached cable.
            """
            obj = self.model.objects.first()
            peer_device = Device.objects.create(
                site=Site.objects.first(),
                device_type=DeviceType.objects.first(),
                role=DeviceRole.objects.first(),
                name='Peer Device'
            )
            if self.peer_termination_type is None:
                raise NotImplementedError(_("Test case must set peer_termination_type"))
            peer_obj = self.peer_termination_type.objects.create(
                device=peer_device,
                name='Peer Termination'
            )
            cable = Cable(a_terminations=[obj], b_terminations=[peer_obj], label='Cable 1')
            cable.save()

            self.add_permissions(f'dcim.view_{self.model._meta.model_name}')
            url = reverse(f'dcim-api:{self.model._meta.model_name}-trace', kwargs={'pk': obj.pk})
            response = self.client.get(url, **self.header)

            self.assertHttpStatus(response, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            segment1 = response.data[0]
            self.assertEqual(segment1[0][0]['name'], obj.name)
            self.assertEqual(segment1[1]['label'], cable.label)
            self.assertEqual(segment1[2][0]['name'], peer_obj.name)


class RegionTest(APIViewTestCases.APIViewTestCase):
    model = Region
    brief_fields = ['_depth', 'description', 'display', 'id', 'name', 'site_count', 'slug', 'url']
    create_data = [
        {
            'name': 'Region 4',
            'slug': 'region-4',
            'comments': 'this is region 4, not region 5',
        },
        {
            'name': 'Region 5',
            'slug': 'region-5',
        },
        {
            'name': 'Region 6',
            'slug': 'region-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
        'comments': 'New comments',
    }

    @classmethod
    def setUpTestData(cls):

        Region.objects.create(name='Region 1', slug='region-1')
        Region.objects.create(name='Region 2', slug='region-2', comments='what in the world is happening?')
        Region.objects.create(name='Region 3', slug='region-3')


class SiteGroupTest(APIViewTestCases.APIViewTestCase):
    model = SiteGroup
    brief_fields = ['_depth', 'description', 'display', 'id', 'name', 'site_count', 'slug', 'url']
    create_data = [
        {
            'name': 'Site Group 4',
            'slug': 'site-group-4',
            'comments': '',
        },
        {
            'name': 'Site Group 5',
            'slug': 'site-group-5',
            'comments': 'not actually empty',
        },
        {
            'name': 'Site Group 6',
            'slug': 'site-group-6',
            'comments': 'Do I really exist?',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
        'comments': 'I do exist!',
    }

    @classmethod
    def setUpTestData(cls):

        SiteGroup.objects.create(name='Site Group 1', slug='site-group-1')
        SiteGroup.objects.create(name='Site Group 2', slug='site-group-2', comments='')
        SiteGroup.objects.create(name='Site Group 3', slug='site-group-3', comments='Hi!')


class SiteTest(APIViewTestCases.APIViewTestCase):
    model = Site
    brief_fields = ['description', 'display', 'id', 'name', 'slug', 'url']
    bulk_update_data = {
        'status': 'planned',
    }

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name='Region 1', slug='region-1'),
            Region.objects.create(name='Region 2', slug='region-2'),
        )

        groups = (
            SiteGroup.objects.create(name='Site Group 1', slug='site-group-1'),
            SiteGroup.objects.create(name='Site Group 2', slug='site-group-2'),
        )

        sites = (
            Site(region=regions[0], group=groups[0], name='Site 1', slug='site-1'),
            Site(region=regions[0], group=groups[0], name='Site 2', slug='site-2'),
            Site(region=regions[0], group=groups[0], name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        rir = RIR.objects.create(name='RFC 6996', is_private=True)
        tenant = Tenant.objects.create(name='Tenant 1', slug='tenant-1')

        asns = [
            ASN(asn=65000 + i, rir=rir) for i in range(8)
        ]
        ASN.objects.bulk_create(asns)

        cls.create_data = [
            {
                'name': 'Site 4',
                'slug': 'site-4',
                'region': regions[1].pk,
                'group': groups[1].pk,
                'status': SiteStatusChoices.STATUS_ACTIVE,
                'asns': [asns[0].pk, asns[1].pk],
                'tenant': tenant.pk,
            },
            {
                'name': 'Site 5',
                'slug': 'site-5',
                'region': regions[1].pk,
                'group': groups[1].pk,
                'status': SiteStatusChoices.STATUS_ACTIVE,
                'asns': [asns[2].pk, asns[3].pk],
            },
            {
                'name': 'Site 6',
                'slug': 'site-6',
                'region': regions[1].pk,
                'group': groups[1].pk,
                'status': SiteStatusChoices.STATUS_ACTIVE,
                'asns': [asns[4].pk, asns[5].pk],
            },
        ]


class LocationTest(APIViewTestCases.APIViewTestCase):
    model = Location
    brief_fields = ['_depth', 'description', 'display', 'id', 'name', 'rack_count', 'slug', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_site',)

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        parent_locations = (
            Location.objects.create(
                site=sites[0],
                name='Parent Location 1',
                slug='parent-location-1',
                status=LocationStatusChoices.STATUS_ACTIVE,
                comments='First!'
            ),
            Location.objects.create(
                site=sites[1],
                name='Parent Location 2',
                slug='parent-location-2',
                status=LocationStatusChoices.STATUS_ACTIVE,
                comments='Second!'
            ),
        )

        Location.objects.create(
            site=sites[0],
            name='Location 1',
            slug='location-1',
            parent=parent_locations[0],
            status=LocationStatusChoices.STATUS_ACTIVE,
            comments='Third!'
        )
        Location.objects.create(
            site=sites[0],
            name='Location 2',
            slug='location-2',
            parent=parent_locations[0],
            status=LocationStatusChoices.STATUS_ACTIVE,
        )
        Location.objects.create(
            site=sites[0],
            name='Location 3',
            slug='location-3',
            parent=parent_locations[0],
            status=LocationStatusChoices.STATUS_ACTIVE,
        )

        cls.create_data = [
            {
                'name': 'Test Location 4',
                'slug': 'test-location-4',
                'site': sites[1].pk,
                'parent': parent_locations[1].pk,
                'status': LocationStatusChoices.STATUS_PLANNED,
                'comments': '',
            },
            {
                'name': 'Test Location 5',
                'slug': 'test-location-5',
                'site': sites[1].pk,
                'parent': parent_locations[1].pk,
                'status': LocationStatusChoices.STATUS_PLANNED,
                'comments': 'Somebody should check on this location',
            },
            {
                'name': 'Test Location 6',
                'slug': 'test-location-6',
                'site': sites[1].pk,
                # Omit parent to test uniqueness constraint
                'status': LocationStatusChoices.STATUS_PLANNED,
            },
        ]


class RackRoleTest(APIViewTestCases.APIViewTestCase):
    model = RackRole
    brief_fields = ['description', 'display', 'id', 'name', 'rack_count', 'slug', 'url']
    create_data = [
        {
            'name': 'Rack Role 4',
            'slug': 'rack-role-4',
            'color': 'ffff00',
        },
        {
            'name': 'Rack Role 5',
            'slug': 'rack-role-5',
            'color': 'ffff00',
        },
        {
            'name': 'Rack Role 6',
            'slug': 'rack-role-6',
            'color': 'ffff00',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1', color='ff0000'),
            RackRole(name='Rack Role 2', slug='rack-role-2', color='00ff00'),
            RackRole(name='Rack Role 3', slug='rack-role-3', color='0000ff'),
        )
        RackRole.objects.bulk_create(rack_roles)


class RackTypeTest(APIViewTestCases.APIViewTestCase):
    model = RackType
    brief_fields = ['description', 'display', 'id', 'manufacturer', 'model', 'slug', 'url']
    bulk_update_data = {
        'description': 'new description',
    }
    user_permissions = ('dcim.view_manufacturer',)

    @classmethod
    def setUpTestData(cls):
        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        rack_types = (
            RackType(
                manufacturer=manufacturers[0],
                model='Rack Type 1',
                slug='rack-type-1',
                form_factor=RackFormFactorChoices.TYPE_CABINET,
            ),
            RackType(
                manufacturer=manufacturers[0],
                model='Rack Type 2',
                slug='rack-type-2',
                form_factor=RackFormFactorChoices.TYPE_CABINET,
            ),
            RackType(
                manufacturer=manufacturers[0],
                model='Rack Type 3',
                slug='rack-type-3',
                form_factor=RackFormFactorChoices.TYPE_CABINET,
            ),
        )
        RackType.objects.bulk_create(rack_types)

        cls.create_data = [
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Rack Type 4',
                'slug': 'rack-type-4',
                'form_factor': RackFormFactorChoices.TYPE_CABINET,
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Rack Type 5',
                'slug': 'rack-type-5',
                'form_factor': RackFormFactorChoices.TYPE_CABINET,
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Rack Type 6',
                'slug': 'rack-type-6',
                'form_factor': RackFormFactorChoices.TYPE_CABINET,
            },
        ]


class RackTest(APIViewTestCases.APIViewTestCase):
    model = Rack
    brief_fields = ['description', 'device_count', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'status': 'planned',
    }
    user_permissions = ('dcim.view_site', )

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location.objects.create(site=sites[0], name='Location 1', slug='location-1'),
            Location.objects.create(site=sites[1], name='Location 2', slug='location-2'),
        )

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1', color='ff0000'),
            RackRole(name='Rack Role 2', slug='rack-role-2', color='00ff00'),
        )
        RackRole.objects.bulk_create(rack_roles)

        racks = (
            Rack(site=sites[0], location=locations[0], role=rack_roles[0], name='Rack 1'),
            Rack(site=sites[0], location=locations[0], role=rack_roles[0], name='Rack 2'),
            Rack(site=sites[0], location=locations[0], role=rack_roles[0], name='Rack 3'),
        )
        Rack.objects.bulk_create(racks)

        cls.create_data = [
            {
                'name': 'Test Rack 4',
                'site': sites[1].pk,
                'location': locations[1].pk,
                'role': rack_roles[1].pk,
            },
            {
                'name': 'Test Rack 5',
                'site': sites[1].pk,
                'location': locations[1].pk,
                'role': rack_roles[1].pk,
            },
            {
                'name': 'Test Rack 6',
                'site': sites[1].pk,
                'location': locations[1].pk,
                'role': rack_roles[1].pk,
            },
        ]

    def test_get_rack_elevation(self):
        """
        GET a single rack elevation.
        """
        rack = Rack.objects.first()
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-elevation', kwargs={'pk': rack.pk})

        # Retrieve all units
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 84)

        # Search for specific units
        response = self.client.get(f'{url}?q=3', **self.header)
        self.assertEqual(response.data['count'], 26)
        response = self.client.get(f'{url}?q=U3', **self.header)
        self.assertEqual(response.data['count'], 22)
        response = self.client.get(f'{url}?q=U10', **self.header)
        self.assertEqual(response.data['count'], 2)

    def test_get_rack_elevation_svg(self):
        """
        GET a single rack elevation in SVG format.
        """
        rack = Rack.objects.first()
        self.add_permissions('dcim.view_rack')
        url = '{}?render=svg'.format(reverse('dcim-api:rack-elevation', kwargs={'pk': rack.pk}))

        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Type'), 'image/svg+xml')


class RackReservationTest(APIViewTestCases.APIViewTestCase):
    model = RackReservation
    brief_fields = ['description', 'display', 'id', 'units', 'url', 'user']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_rack', 'users.view_user')

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='user1', is_active=True)
        site = Site.objects.create(name='Test Site 1', slug='test-site-1')

        racks = (
            Rack(site=site, name='Rack 1'),
            Rack(site=site, name='Rack 2'),
        )
        Rack.objects.bulk_create(racks)

        rack_reservations = (
            RackReservation(rack=racks[0], units=[1, 2, 3], user=user, description='Reservation #1'),
            RackReservation(rack=racks[0], units=[4, 5, 6], user=user, description='Reservation #2'),
            RackReservation(rack=racks[0], units=[7, 8, 9], user=user, description='Reservation #3'),
        )
        RackReservation.objects.bulk_create(rack_reservations)

        cls.create_data = [
            {
                'rack': racks[1].pk,
                'units': [10, 11, 12],
                'user': user.pk,
                'description': 'Reservation #4',
            },
            {
                'rack': racks[1].pk,
                'units': [13, 14, 15],
                'user': user.pk,
                'description': 'Reservation #5',
            },
            {
                'rack': racks[1].pk,
                'units': [16, 17, 18],
                'user': user.pk,
                'description': 'Reservation #6',
            },
        ]


class ManufacturerTest(APIViewTestCases.APIViewTestCase):
    model = Manufacturer
    brief_fields = ['description', 'devicetype_count', 'display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Manufacturer 4',
            'slug': 'manufacturer-4',
        },
        {
            'name': 'Manufacturer 5',
            'slug': 'manufacturer-5',
        },
        {
            'name': 'Manufacturer 6',
            'slug': 'manufacturer-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)


class DeviceTypeTest(APIViewTestCases.APIViewTestCase):
    model = DeviceType
    brief_fields = ['description', 'device_count', 'display', 'id', 'manufacturer', 'model', 'slug', 'url']
    bulk_update_data = {
        'part_number': 'ABC123',
    }
    user_permissions = ('dcim.view_manufacturer', )

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        device_types = (
            DeviceType(manufacturer=manufacturers[0], model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturers[0], model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturers[0], model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        cls.create_data = [
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Device Type 4',
                'slug': 'device-type-4',
                'u_height': 0,
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Device Type 5',
                'slug': 'device-type-5',
                'u_height': 0.5,
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Device Type 6',
                'slug': 'device-type-6',
                'u_height': 1,
            },
        ]


class ModuleTypeTest(APIViewTestCases.APIViewTestCase):
    model = ModuleType
    brief_fields = ['description', 'display', 'id', 'manufacturer', 'model', 'profile', 'url']
    bulk_update_data = {
        'part_number': 'ABC123',
    }
    user_permissions = ('dcim.view_manufacturer', )

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        module_types = (
            ModuleType(manufacturer=manufacturers[0], model='Module Type 1'),
            ModuleType(manufacturer=manufacturers[0], model='Module Type 2'),
            ModuleType(manufacturer=manufacturers[0], model='Module Type 3'),
        )
        ModuleType.objects.bulk_create(module_types)

        cls.create_data = [
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Module Type 4',
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Module Type 5',
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Module Type 6',
            },
        ]


class ModuleTypeProfileTest(APIViewTestCases.APIViewTestCase):
    model = ModuleTypeProfile
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    SCHEMAS = [
        {
            "properties": {
                "foo": {
                    "type": "string"
                }
            }
        },
        {
            "properties": {
                "foo": {
                    "type": "integer"
                }
            }
        },
        {
            "properties": {
                "foo": {
                    "type": "boolean"
                }
            }
        },
    ]
    create_data = [
        {
            'name': 'Module Type Profile 4',
            'schema': SCHEMAS[0],
        },
        {
            'name': 'Module Type Profile 5',
            'schema': SCHEMAS[1],
        },
        {
            'name': 'Module Type Profile 6',
            'schema': SCHEMAS[2],
        },
    ]
    bulk_update_data = {
        'description': 'New description',
        'comments': 'New comments',
    }

    @classmethod
    def setUpTestData(cls):
        module_type_profiles = (
            ModuleTypeProfile(
                name='Module Type Profile 1',
                schema=cls.SCHEMAS[0]
            ),
            ModuleTypeProfile(
                name='Module Type Profile 2',
                schema=cls.SCHEMAS[1]
            ),
            ModuleTypeProfile(
                name='Module Type Profile 3',
                schema=cls.SCHEMAS[2]
            ),
        )
        ModuleTypeProfile.objects.bulk_create(module_type_profiles)


class ConsolePortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ConsolePortTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        moduletype = ModuleType.objects.create(
            manufacturer=manufacturer, model='Module Type 1'
        )

        console_port_templates = (
            ConsolePortTemplate(device_type=devicetype, name='Console Port Template 1'),
            ConsolePortTemplate(device_type=devicetype, name='Console Port Template 2'),
            ConsolePortTemplate(device_type=devicetype, name='Console Port Template 3'),
        )
        ConsolePortTemplate.objects.bulk_create(console_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Console Port Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Console Port Template 5',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Console Port Template 6',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Console Port Template 7',
            },
        ]


class ConsoleServerPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ConsoleServerPortTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        moduletype = ModuleType.objects.create(
            manufacturer=manufacturer, model='Module Type 1'
        )

        console_server_port_templates = (
            ConsoleServerPortTemplate(device_type=devicetype, name='Console Server Port Template 1'),
            ConsoleServerPortTemplate(device_type=devicetype, name='Console Server Port Template 2'),
            ConsoleServerPortTemplate(device_type=devicetype, name='Console Server Port Template 3'),
        )
        ConsoleServerPortTemplate.objects.bulk_create(console_server_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Console Server Port Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Console Server Port Template 5',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Console Server Port Template 6',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Console Server Port Template 7',
            },
        ]


class PowerPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = PowerPortTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        moduletype = ModuleType.objects.create(
            manufacturer=manufacturer, model='Module Type 1'
        )

        power_port_templates = (
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 1'),
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 2'),
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 3'),
        )
        PowerPortTemplate.objects.bulk_create(power_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Power Port Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Power Port Template 5',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Power Port Template 6',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Power Port Template 7',
            },
        ]


class PowerOutletTemplateTest(APIViewTestCases.APIViewTestCase):
    model = PowerOutletTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_devicetype', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        moduletype = ModuleType.objects.create(
            manufacturer=manufacturer, model='Module Type 1'
        )

        power_port_templates = (
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 1'),
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 2'),
        )
        PowerPortTemplate.objects.bulk_create(power_port_templates)

        power_outlet_templates = (
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 1'),
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 2'),
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 3'),
        )
        PowerOutletTemplate.objects.bulk_create(power_outlet_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Power Outlet Template 4',
                'power_port': power_port_templates[0].pk,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Power Outlet Template 5',
                'power_port': power_port_templates[1].pk,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Power Outlet Template 6',
                'power_port': None,
            },
            {
                'module_type': moduletype.pk,
                'name': 'Power Outlet Template 7',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Power Outlet Template 8',
            },
        ]


class InterfaceTemplateTest(APIViewTestCases.APIViewTestCase):
    model = InterfaceTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        moduletype = ModuleType.objects.create(
            manufacturer=manufacturer, model='Module Type 1'
        )

        interface_templates = (
            InterfaceTemplate(device_type=devicetype, name='Interface Template 1', type='1000base-t'),
            InterfaceTemplate(device_type=devicetype, name='Interface Template 2', type='1000base-t'),
            InterfaceTemplate(device_type=devicetype, name='Interface Template 3', type='1000base-t'),
        )
        InterfaceTemplate.objects.bulk_create(interface_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Interface Template 4',
                'type': '1000base-t',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Interface Template 5',
                'type': '1000base-t',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Interface Template 6',
                'type': '1000base-t',
            },
            {
                'module_type': moduletype.pk,
                'name': 'Interface Template 7',
                'type': '1000base-t',
            },
        ]


class FrontPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = FrontPortTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_rearporttemplate', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        moduletype = ModuleType.objects.create(
            manufacturer=manufacturer, model='Module Type 1'
        )

        rear_port_templates = (
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 1', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 2', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 3', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 4', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(module_type=moduletype, name='Rear Port Template 5', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(module_type=moduletype, name='Rear Port Template 6', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(module_type=moduletype, name='Rear Port Template 7', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(module_type=moduletype, name='Rear Port Template 8', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_port_templates)

        front_port_templates = (
            FrontPortTemplate(
                device_type=devicetype,
                name='Front Port Template 1',
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_port_templates[0]
            ),
            FrontPortTemplate(
                device_type=devicetype,
                name='Front Port Template 2',
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_port_templates[1]
            ),
            FrontPortTemplate(
                module_type=moduletype,
                name='Front Port Template 5',
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_port_templates[4]
            ),
            FrontPortTemplate(
                module_type=moduletype,
                name='Front Port Template 6',
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_port_templates[5]
            ),
        )
        FrontPortTemplate.objects.bulk_create(front_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Front Port Template 3',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_port_templates[2].pk,
                'rear_port_position': 1,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Front Port Template 4',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_port_templates[3].pk,
                'rear_port_position': 1,
            },
            {
                'module_type': moduletype.pk,
                'name': 'Front Port Template 7',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_port_templates[6].pk,
                'rear_port_position': 1,
            },
            {
                'module_type': moduletype.pk,
                'name': 'Front Port Template 8',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_port_templates[7].pk,
                'rear_port_position': 1,
            },
        ]


class RearPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = RearPortTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        moduletype = ModuleType.objects.create(
            manufacturer=manufacturer, model='Module Type 1'
        )

        rear_port_templates = (
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 1', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 2', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 3', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Rear Port Template 4',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Rear Port Template 5',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'module_type': moduletype.pk,
                'name': 'Rear Port Template 6',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'module_type': moduletype.pk,
                'name': 'Rear Port Template 7',
                'type': PortTypeChoices.TYPE_8P8C,
            },
        ]


class ModuleBayTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ModuleBayTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_devicetype', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Device Type 1',
            slug='device-type-1',
            subdevice_role=SubdeviceRoleChoices.ROLE_PARENT
        )

        module_bay_templates = (
            ModuleBayTemplate(device_type=devicetype, name='Module Bay Template 1'),
            ModuleBayTemplate(device_type=devicetype, name='Module Bay Template 2'),
            ModuleBayTemplate(device_type=devicetype, name='Module Bay Template 3'),
        )
        ModuleBayTemplate.objects.bulk_create(module_bay_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Module Bay Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Module Bay Template 5',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Module Bay Template 6',
            },
        ]


class DeviceBayTemplateTest(APIViewTestCases.APIViewTestCase):
    model = DeviceBayTemplate
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_devicetype', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Device Type 1',
            slug='device-type-1',
            subdevice_role=SubdeviceRoleChoices.ROLE_PARENT
        )

        device_bay_templates = (
            DeviceBayTemplate(device_type=devicetype, name='Device Bay Template 1'),
            DeviceBayTemplate(device_type=devicetype, name='Device Bay Template 2'),
            DeviceBayTemplate(device_type=devicetype, name='Device Bay Template 3'),
        )
        DeviceBayTemplate.objects.bulk_create(device_bay_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Device Bay Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Device Bay Template 5',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Device Bay Template 6',
            },
        ]


class InventoryItemTemplateTest(APIViewTestCases.APIViewTestCase):
    model = InventoryItemTemplate
    brief_fields = ['_depth', 'description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_devicetype', 'dcim.view_manufacturer',)

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Device Type 1',
            slug='device-type-1'
        )
        role = InventoryItemRole.objects.create(name='Inventory Item Role 1', slug='inventory-item-role-1')

        inventory_item_templates = (
            InventoryItemTemplate(
                device_type=devicetype, name='Inventory Item Template 1', manufacturer=manufacturer, role=role
            ),
            InventoryItemTemplate(
                device_type=devicetype, name='Inventory Item Template 2', manufacturer=manufacturer, role=role
            ),
            InventoryItemTemplate(
                device_type=devicetype, name='Inventory Item Template 3', manufacturer=manufacturer, role=role
            ),
            InventoryItemTemplate(
                device_type=devicetype, name='Inventory Item Template 4', manufacturer=manufacturer, role=role
            ),
        )
        for item in inventory_item_templates:
            item.save()

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Inventory Item Template 5',
                'manufacturer': manufacturer.pk,
                'role': role.pk,
                'parent': inventory_item_templates[3].pk,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Inventory Item Template 6',
                'manufacturer': manufacturer.pk,
                'role': role.pk,
                'parent': inventory_item_templates[3].pk,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Inventory Item Template 7',
                'manufacturer': manufacturer.pk,
                'role': role.pk,
                'parent': inventory_item_templates[3].pk,
            },
        ]


class DeviceRoleTest(APIViewTestCases.APIViewTestCase):
    model = DeviceRole
    brief_fields = [
        '_depth', 'description', 'device_count', 'display', 'id', 'name', 'slug', 'url', 'virtualmachine_count'
    ]
    create_data = [
        {
            'name': 'Device Role 4',
            'slug': 'device-role-4',
            'color': 'ffff00',
        },
        {
            'name': 'Device Role 5',
            'slug': 'device-role-5',
            'color': 'ffff00',
        },
        {
            'name': 'Device Role 6',
            'slug': 'device-role-6',
            'color': 'ffff00',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')
        DeviceRole.objects.create(name='Device Role 2', slug='device-role-2', color='00ff00')
        DeviceRole.objects.create(name='Device Role 3', slug='device-role-3', color='0000ff')


class PlatformTest(APIViewTestCases.APIViewTestCase):
    model = Platform
    brief_fields = ['description', 'device_count', 'display', 'id', 'name', 'slug', 'url', 'virtualmachine_count']
    create_data = [
        {
            'name': 'Platform 4',
            'slug': 'platform-4',
        },
        {
            'name': 'Platform 5',
            'slug': 'platform-5',
        },
        {
            'name': 'Platform 6',
            'slug': 'platform-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        Platform.objects.bulk_create(platforms)


class DeviceTest(APIViewTestCases.APIViewTestCase):
    model = Device
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'status': 'failed',
    }
    user_permissions = (
        'dcim.view_site', 'dcim.view_rack', 'dcim.view_location', 'dcim.view_devicerole', 'dcim.view_devicetype',
        'extras.view_configtemplate',
    )

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
        )
        Rack.objects.bulk_create(racks)

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2', u_height=2),
        )
        DeviceType.objects.bulk_create(device_types)

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1', color='ff0000'),
            DeviceRole(name='Device Role 2', slug='device-role-2', color='00ff00'),
        )
        for role in roles:
            role.save()

        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')

        clusters = (
            Cluster(name='Cluster 1', type=cluster_type),
            Cluster(name='Cluster 2', type=cluster_type),
        )
        Cluster.objects.bulk_create(clusters)

        devices = (
            Device(
                device_type=device_types[0],
                role=roles[0],
                name='Device 1',
                site=sites[0],
                rack=racks[0],
                cluster=clusters[0],
                local_context_data={'A': 1}
            ),
            Device(
                device_type=device_types[0],
                role=roles[0],
                name='Device 2',
                site=sites[0],
                rack=racks[0],
                cluster=clusters[0],
                local_context_data={'B': 2}
            ),
            Device(
                device_type=device_types[0],
                role=roles[0],
                name='Device 3',
                site=sites[0],
                rack=racks[0],
                cluster=clusters[0],
                local_context_data={'C': 3}
            ),
        )
        Device.objects.bulk_create(devices)

        cls.create_data = [
            {
                'device_type': device_types[1].pk,
                'role': roles[1].pk,
                'name': 'Test Device 4',
                'site': sites[1].pk,
                'rack': racks[1].pk,
                'cluster': clusters[1].pk,
            },
            {
                'device_type': device_types[1].pk,
                'role': roles[1].pk,
                'name': 'Test Device 5',
                'site': sites[1].pk,
                'rack': racks[1].pk,
                'cluster': clusters[1].pk,
            },
            {
                'device_type': device_types[1].pk,
                'role': roles[1].pk,
                'name': 'Test Device 6',
                'site': sites[1].pk,
                'rack': racks[1].pk,
                'cluster': clusters[1].pk,
            },
        ]

    def test_config_context_included_by_default_in_list_view(self):
        """
        Check that config context data is included by default in the devices list.
        """
        self.add_permissions('dcim.view_device')
        url = reverse('dcim-api:device-list') + '?slug=device-with-context-data'
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['results'][0].get('config_context', {}).get('A'), 1)

    def test_config_context_excluded(self):
        """
        Check that config context data can be excluded by passing ?exclude=config_context.
        """
        self.add_permissions('dcim.view_device')
        url = reverse('dcim-api:device-list') + '?exclude=config_context'
        response = self.client.get(url, **self.header)

        self.assertFalse('config_context' in response.data['results'][0])

    def test_unique_name_per_site_constraint(self):
        """
        Check that creating a device with a duplicate name within a site fails.
        """
        device = Device.objects.first()
        data = {
            'device_type': device.device_type.pk,
            'role': device.role.pk,
            'site': device.site.pk,
            'name': device.name,
        }

        self.add_permissions('dcim.add_device')
        url = reverse('dcim-api:device-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_rack_fit(self):
        """
        Check that creating multiple devices with overlapping position fails.
        """
        device = Device.objects.first()
        device_type = DeviceType.objects.all()[1]
        data = [
            {
                'device_type': device_type.pk,
                'role': device.role.pk,
                'site': device.site.pk,
                'name': 'Test Device 7',
                'rack': device.rack.pk,
                'face': 'front',
                'position': 1
            },
            {
                'device_type': device_type.pk,
                'role': device.role.pk,
                'site': device.site.pk,
                'name': 'Test Device 8',
                'rack': device.rack.pk,
                'face': 'front',
                'position': 2
            }
        ]

        self.add_permissions('dcim.add_device')
        url = reverse('dcim-api:device-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_render_config(self):
        configtemplate = ConfigTemplate.objects.create(
            name='Config Template 1',
            template_code='Config for device {{ device.name }}'
        )

        device = Device.objects.first()
        device.config_template = configtemplate
        device.save()

        self.add_permissions('dcim.add_device')
        url = reverse('dcim-api:device-detail', kwargs={'pk': device.pk}) + 'render-config/'
        response = self.client.post(url, {}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], f'Config for device {device.name}')


class ModuleTest(APIViewTestCases.APIViewTestCase):
    model = Module
    brief_fields = ['description', 'device', 'display', 'id', 'module_bay', 'module_type', 'url']
    bulk_update_data = {
        'serial': '1234ABCD',
    }
    user_permissions = ('dcim.view_modulebay', 'dcim.view_moduletype', 'dcim.view_device')

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device = create_test_device('Test Device 1')

        module_types = (
            ModuleType(manufacturer=manufacturer, model='Module Type 1'),
            ModuleType(manufacturer=manufacturer, model='Module Type 2'),
            ModuleType(manufacturer=manufacturer, model='Module Type 3'),
        )
        ModuleType.objects.bulk_create(module_types)

        module_bays = (
            ModuleBay(device=device, name='Module Bay 1'),
            ModuleBay(device=device, name='Module Bay 2'),
            ModuleBay(device=device, name='Module Bay 3'),
            ModuleBay(device=device, name='Module Bay 4'),
            ModuleBay(device=device, name='Module Bay 5'),
            ModuleBay(device=device, name='Module Bay 6'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=device, module_bay=module_bays[0], module_type=module_types[0]),
            Module(device=device, module_bay=module_bays[1], module_type=module_types[1]),
            Module(device=device, module_bay=module_bays[2], module_type=module_types[2]),
        )
        Module.objects.bulk_create(modules)

        cls.create_data = [
            {
                'device': device.pk,
                'module_bay': module_bays[3].pk,
                'module_type': module_types[0].pk,
                'status': ModuleStatusChoices.STATUS_ACTIVE,
                'serial': 'ABC123',
                'asset_tag': 'Foo1',
            },
            {
                'device': device.pk,
                'module_bay': module_bays[4].pk,
                'module_type': module_types[1].pk,
                'status': ModuleStatusChoices.STATUS_ACTIVE,
                'serial': 'DEF456',
                'asset_tag': 'Foo2',
            },
            {
                'device': device.pk,
                'module_bay': module_bays[5].pk,
                'module_type': module_types[2].pk,
                'status': ModuleStatusChoices.STATUS_ACTIVE,
                'serial': 'GHI789',
                'asset_tag': 'Foo3',
            },
        ]


class ConsolePortTest(Mixins.ComponentTraceMixin, APIViewTestCases.APIViewTestCase):
    model = ConsolePort
    brief_fields = ['_occupied', 'cable', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    peer_termination_type = ConsoleServerPort
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        console_ports = (
            ConsolePort(device=device, name='Console Port 1'),
            ConsolePort(device=device, name='Console Port 2'),
            ConsolePort(device=device, name='Console Port 3'),
        )
        ConsolePort.objects.bulk_create(console_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Console Port 4',
                'speed': 9600,
            },
            {
                'device': device.pk,
                'name': 'Console Port 5',
                'speed': 115200,
            },
            {
                'device': device.pk,
                'name': 'Console Port 6',
                'speed': None,
            },
        ]


class ConsoleServerPortTest(Mixins.ComponentTraceMixin, APIViewTestCases.APIViewTestCase):
    model = ConsoleServerPort
    brief_fields = ['_occupied', 'cable', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    peer_termination_type = ConsolePort
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        console_server_ports = (
            ConsoleServerPort(device=device, name='Console Server Port 1'),
            ConsoleServerPort(device=device, name='Console Server Port 2'),
            ConsoleServerPort(device=device, name='Console Server Port 3'),
        )
        ConsoleServerPort.objects.bulk_create(console_server_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Console Server Port 4',
                'speed': 9600,
            },
            {
                'device': device.pk,
                'name': 'Console Server Port 5',
                'speed': 115200,
            },
            {
                'device': device.pk,
                'name': 'Console Server Port 6',
                'speed': None,
            },
        ]


class PowerPortTest(Mixins.ComponentTraceMixin, APIViewTestCases.APIViewTestCase):
    model = PowerPort
    brief_fields = ['_occupied', 'cable', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    peer_termination_type = PowerOutlet
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        power_ports = (
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
            PowerPort(device=device, name='Power Port 3'),
        )
        PowerPort.objects.bulk_create(power_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Power Port 4',
            },
            {
                'device': device.pk,
                'name': 'Power Port 5',
            },
            {
                'device': device.pk,
                'name': 'Power Port 6',
            },
        ]


class PowerOutletTest(Mixins.ComponentTraceMixin, APIViewTestCases.APIViewTestCase):
    model = PowerOutlet
    brief_fields = ['_occupied', 'cable', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    peer_termination_type = PowerPort
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        power_ports = (
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
        )
        PowerPort.objects.bulk_create(power_ports)

        power_outlets = (
            PowerOutlet(device=device, name='Power Outlet 1'),
            PowerOutlet(device=device, name='Power Outlet 2'),
            PowerOutlet(device=device, name='Power Outlet 3'),
        )
        PowerOutlet.objects.bulk_create(power_outlets)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Power Outlet 4',
                'power_port': power_ports[0].pk,
            },
            {
                'device': device.pk,
                'name': 'Power Outlet 5',
                'power_port': power_ports[1].pk,
            },
            {
                'device': device.pk,
                'name': 'Power Outlet 6',
                'power_port': None,
            },
        ]


class InterfaceTest(Mixins.ComponentTraceMixin, APIViewTestCases.APIViewTestCase):
    model = Interface
    brief_fields = ['_occupied', 'cable', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    peer_termination_type = Interface
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        interfaces = (
            Interface(device=device, name='Interface 1', type='1000base-t'),
            Interface(device=device, name='Interface 2', type='1000base-t'),
            Interface(device=device, name='Interface 3', type='1000base-t'),
        )
        Interface.objects.bulk_create(interfaces)

        vdcs = (
            VirtualDeviceContext(name='VDC 1', identifier=1, device=device),
            VirtualDeviceContext(name='VDC 2', identifier=2, device=device)
        )
        VirtualDeviceContext.objects.bulk_create(vdcs)

        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
            VLAN(name='SVLAN 1', vid=1001, qinq_role=VLANQinQRoleChoices.ROLE_SERVICE),
        )
        VLAN.objects.bulk_create(vlans)

        wireless_lans = (
            WirelessLAN(ssid='WLAN1'),
            WirelessLAN(ssid='WLAN2'),
        )
        WirelessLAN.objects.bulk_create(wireless_lans)

        vrfs = (
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
            VRF(name='VRF 3'),
        )
        VRF.objects.bulk_create(vrfs)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Interface 4',
                'type': '1000base-t',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'speed': 1000000,
                'duplex': 'full',
                'vrf': vrfs[0].pk,
                'poe_mode': InterfacePoEModeChoices.MODE_PD,
                'poe_type': InterfacePoETypeChoices.TYPE_1_8023AF,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
            {
                'device': device.pk,
                'name': 'Interface 5',
                'type': '1000base-t',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'bridge': interfaces[0].pk,
                'speed': 100000,
                'duplex': 'half',
                'vrf': vrfs[1].pk,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
            {
                'device': device.pk,
                'vdcs': [vdcs[0].pk],
                'name': 'Interface 6',
                'type': 'virtual',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'parent': interfaces[1].pk,
                'vrf': vrfs[2].pk,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
            {
                'device': device.pk,
                'vdcs': [vdcs[1].pk],
                'name': 'Interface 7',
                'type': InterfaceTypeChoices.TYPE_80211A,
                'mode': InterfaceModeChoices.MODE_Q_IN_Q,
                'tx_power': 10,
                'wireless_lans': [wireless_lans[0].pk, wireless_lans[1].pk],
                'rf_channel': WirelessChannelChoices.CHANNEL_5G_32,
                'qinq_svlan': vlans[3].pk,
            },
            {
                'device': device.pk,
                'vdcs': [vdcs[1].pk],
                'name': 'Interface 8',
                'type': InterfaceTypeChoices.TYPE_80211A,
                'mode': InterfaceModeChoices.MODE_Q_IN_Q,
                'tx_power': 10,
                'wireless_lans': [wireless_lans[0].pk, wireless_lans[1].pk],
                'rf_channel': "",
                'qinq_svlan': vlans[3].pk,
            },
        ]

    def _perform_interface_test_with_invalid_data(self, mode: str = None, invalid_data: dict = {}):
        device = Device.objects.first()
        data = {
            'device': device.pk,
            'name': 'Interface 1',
            'type': InterfaceTypeChoices.TYPE_1GE_FIXED,
        }
        data.update({'mode': mode})
        data.update(invalid_data)

        response = self.client.post(self._get_list_url(), data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        content = json.loads(response.content)
        for key in invalid_data.keys():
            self.assertIn(key, content)
        self.assertIsNone(content.get('data'))

    def test_bulk_delete_child_interfaces(self):
        interface1 = Interface.objects.get(name='Interface 1')
        device = interface1.device
        self.add_permissions('dcim.delete_interface')

        # Create a child interface
        child = Interface.objects.create(
            device=device,
            name='Interface 1A',
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            parent=interface1
        )
        self.assertEqual(device.interfaces.count(), 4)

        # Attempt to delete only the parent interface
        url = self._get_detail_url(interface1)
        with disable_logging():
            self.client.delete(url, **self.header)
        self.assertEqual(device.interfaces.count(), 4)  # Parent was not deleted

        # Attempt to bulk delete parent & child together
        data = [
            {"id": interface1.pk},
            {"id": child.pk},
        ]
        self.client.delete(self._get_list_url(), data, format='json', **self.header)
        self.assertEqual(device.interfaces.count(), 2)  # Child & parent were both deleted

    def test_create_child_interfaces_mode_invalid_data(self):
        """
        POST data to test interface mode check and invalid tagged/untagged VLANS.
        """
        self.add_permissions('dcim.add_interface')

        vlans = VLAN.objects.all()[0:3]

        # Routed mode, untagged, tagged and qinq service vlan
        invalid_data = {
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [vlans[1].pk, vlans[2].pk],
            'qinq_svlan': vlans[2].pk
        }
        self._perform_interface_test_with_invalid_data(None, invalid_data)

        # Routed mode, untagged and tagged vlan
        invalid_data = {
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [vlans[1].pk, vlans[2].pk],
        }
        self._perform_interface_test_with_invalid_data(None, invalid_data)

        # Routed mode, untagged vlan
        invalid_data = {
            'untagged_vlan': vlans[0].pk,
        }
        self._perform_interface_test_with_invalid_data(None, invalid_data)

        invalid_data = {
            'tagged_vlans': [vlans[1].pk, vlans[2].pk],
        }
        # Routed mode, qinq service vlan
        self._perform_interface_test_with_invalid_data(None, invalid_data)
        # Access mode, tagged vlans
        self._perform_interface_test_with_invalid_data(InterfaceModeChoices.MODE_ACCESS, invalid_data)
        # All tagged mode, tagged vlans
        self._perform_interface_test_with_invalid_data(InterfaceModeChoices.MODE_TAGGED_ALL, invalid_data)

        invalid_data = {
            'qinq_svlan': vlans[0].pk,
        }
        # Routed mode, qinq service vlan
        self._perform_interface_test_with_invalid_data(None, invalid_data)
        # Access mode, qinq service vlan
        self._perform_interface_test_with_invalid_data(InterfaceModeChoices.MODE_ACCESS, invalid_data)
        # Tagged mode, qinq service vlan
        self._perform_interface_test_with_invalid_data(InterfaceModeChoices.MODE_TAGGED, invalid_data)
        # Tagged-all mode, qinq service vlan
        self._perform_interface_test_with_invalid_data(InterfaceModeChoices.MODE_TAGGED_ALL, invalid_data)


class FrontPortTest(APIViewTestCases.APIViewTestCase):
    model = FrontPort
    brief_fields = ['_occupied', 'cable', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    peer_termination_type = Interface
    user_permissions = ('dcim.view_device', 'dcim.view_rearport')

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        rear_ports = (
            RearPort(device=device, name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 3', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 4', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 5', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 6', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPort.objects.bulk_create(rear_ports)

        front_ports = (
            FrontPort(device=device, name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[0]),
            FrontPort(device=device, name='Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[1]),
            FrontPort(device=device, name='Front Port 3', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[2]),
        )
        FrontPort.objects.bulk_create(front_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Front Port 4',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_ports[3].pk,
                'rear_port_position': 1,
            },
            {
                'device': device.pk,
                'name': 'Front Port 5',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_ports[4].pk,
                'rear_port_position': 1,
            },
            {
                'device': device.pk,
                'name': 'Front Port 6',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_ports[5].pk,
                'rear_port_position': 1,
            },
        ]

    @tag('regression')  # Issue #18991
    def test_front_port_paths(self):
        device = Device.objects.first()
        rear_port = RearPort.objects.create(
            device=device, name='Rear Port 10', type=PortTypeChoices.TYPE_8P8C
        )
        interface1 = Interface.objects.create(device=device, name='Interface 1')
        front_port = FrontPort.objects.create(
            device=device,
            name='Rear Port 10',
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rear_port,
        )
        Cable.objects.create(a_terminations=[interface1], b_terminations=[front_port])

        self.add_permissions(f'dcim.view_{self.model._meta.model_name}')
        url = reverse(f'dcim-api:{self.model._meta.model_name}-paths', kwargs={'pk': front_port.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)


class RearPortTest(APIViewTestCases.APIViewTestCase):
    model = RearPort
    brief_fields = ['_occupied', 'cable', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    peer_termination_type = Interface
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        rear_ports = (
            RearPort(device=device, name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 3', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPort.objects.bulk_create(rear_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Rear Port 4',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'device': device.pk,
                'name': 'Rear Port 5',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'device': device.pk,
                'name': 'Rear Port 6',
                'type': PortTypeChoices.TYPE_8P8C,
            },
        ]

    @tag('regression')  # Issue #18991
    def test_rear_port_paths(self):
        device = Device.objects.first()
        interface1 = Interface.objects.create(device=device, name='Interface 1')
        rear_port = RearPort.objects.create(
            device=device,
            name='Rear Port 10',
            type=PortTypeChoices.TYPE_8P8C,
        )
        Cable.objects.create(a_terminations=[interface1], b_terminations=[rear_port])

        self.add_permissions(f'dcim.view_{self.model._meta.model_name}')
        url = reverse(f'dcim-api:{self.model._meta.model_name}-paths', kwargs={'pk': rear_port.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)


class ModuleBayTest(APIViewTestCases.APIViewTestCase):
    model = ModuleBay
    brief_fields = ['description', 'display', 'id', 'installed_module', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')

        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        device = Device.objects.create(device_type=device_type, role=role, name='Device 1', site=site)

        module_bays = (
            ModuleBay(device=device, name='Device Bay 1'),
            ModuleBay(device=device, name='Device Bay 2'),
            ModuleBay(device=device, name='Device Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Device Bay 4',
            },
            {
                'device': device.pk,
                'name': 'Device Bay 5',
            },
            {
                'device': device.pk,
                'name': 'Device Bay 6',
            },
        ]


class DeviceBayTest(APIViewTestCases.APIViewTestCase):
    model = DeviceBay
    brief_fields = ['description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_device', )

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')

        device_types = (
            DeviceType(
                manufacturer=manufacturer,
                model='Device Type 1',
                slug='device-type-1',
                subdevice_role=SubdeviceRoleChoices.ROLE_PARENT
            ),
            DeviceType(
                manufacturer=manufacturer,
                model='Device Type 2',
                slug='device-type-2',
                subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
            ),
        )
        DeviceType.objects.bulk_create(device_types)

        devices = (
            Device(device_type=device_types[0], role=role, name='Device 1', site=site),
            Device(device_type=device_types[1], role=role, name='Device 2', site=site),
            Device(device_type=device_types[1], role=role, name='Device 3', site=site),
            Device(device_type=device_types[1], role=role, name='Device 4', site=site),
        )
        Device.objects.bulk_create(devices)

        device_bays = (
            DeviceBay(device=devices[0], name='Device Bay 1'),
            DeviceBay(device=devices[0], name='Device Bay 2'),
            DeviceBay(device=devices[0], name='Device Bay 3'),
        )
        DeviceBay.objects.bulk_create(device_bays)

        cls.create_data = [
            {
                'device': devices[0].pk,
                'name': 'Device Bay 4',
                'installed_device': devices[1].pk,
            },
            {
                'device': devices[0].pk,
                'name': 'Device Bay 5',
                'installed_device': devices[2].pk,
            },
            {
                'device': devices[0].pk,
                'name': 'Device Bay 6',
                'installed_device': devices[3].pk,
            },
        ]


class InventoryItemTest(APIViewTestCases.APIViewTestCase):
    model = InventoryItem
    brief_fields = ['_depth', 'description', 'device', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }
    user_permissions = ('dcim.view_device', 'dcim.view_manufacturer')

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, role=role, name='Device 1', site=site)

        roles = (
            InventoryItemRole(name='Inventory Item Role 1', slug='inventory-item-role-1'),
            InventoryItemRole(name='Inventory Item Role 2', slug='inventory-item-role-2'),
        )
        InventoryItemRole.objects.bulk_create(roles)

        interfaces = (
            Interface(device=device, name='Interface 1'),
            Interface(device=device, name='Interface 2'),
            Interface(device=device, name='Interface 3'),
        )
        Interface.objects.bulk_create(interfaces)

        InventoryItem.objects.create(
            device=device, name='Inventory Item 1', role=roles[0], manufacturer=manufacturer, component=interfaces[0]
        )
        InventoryItem.objects.create(
            device=device, name='Inventory Item 2', role=roles[0], manufacturer=manufacturer, component=interfaces[1]
        )
        InventoryItem.objects.create(
            device=device, name='Inventory Item 3', role=roles[0], manufacturer=manufacturer, component=interfaces[2]
        )

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Inventory Item 4',
                'role': roles[1].pk,
                'manufacturer': manufacturer.pk,
                'component_type': 'dcim.interface',
                'component_id': interfaces[0].pk,
            },
            {
                'device': device.pk,
                'name': 'Inventory Item 5',
                'role': roles[1].pk,
                'manufacturer': manufacturer.pk,
                'component_type': 'dcim.interface',
                'component_id': interfaces[1].pk,
            },
            {
                'device': device.pk,
                'name': 'Inventory Item 6',
                'role': roles[1].pk,
                'manufacturer': manufacturer.pk,
                'component_type': 'dcim.interface',
                'component_id': interfaces[2].pk,
            },
        ]


class InventoryItemRoleTest(APIViewTestCases.APIViewTestCase):
    model = InventoryItemRole
    brief_fields = ['description', 'display', 'id', 'inventoryitem_count', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Inventory Item Role 4',
            'slug': 'inventory-item-role-4',
            'color': 'ffff00',
        },
        {
            'name': 'Inventory Item Role 5',
            'slug': 'inventory-item-role-5',
            'color': 'ffff00',
        },
        {
            'name': 'Inventory Item Role 6',
            'slug': 'inventory-item-role-6',
            'color': 'ffff00',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        roles = (
            InventoryItemRole(name='Inventory Item Role 1', slug='inventory-item-role-1', color='ff0000'),
            InventoryItemRole(name='Inventory Item Role 2', slug='inventory-item-role-2', color='00ff00'),
            InventoryItemRole(name='Inventory Item Role 3', slug='inventory-item-role-3', color='0000ff'),
        )
        InventoryItemRole.objects.bulk_create(roles)


class CableTest(APIViewTestCases.APIViewTestCase):
    model = Cable
    brief_fields = ['description', 'display', 'id', 'label', 'url']
    bulk_update_data = {
        'length': 100,
        'length_unit': 'm',
    }

    # TODO: Allow updating cable terminations
    test_update_object = None

    def model_to_dict(self, *args, **kwargs):
        data = super().model_to_dict(*args, **kwargs)

        # Serialize termination objects
        if 'a_terminations' in data:
            data['a_terminations'] = GenericObjectSerializer(data['a_terminations'], many=True).data
        if 'b_terminations' in data:
            data['b_terminations'] = GenericObjectSerializer(data['b_terminations'], many=True).data

        return data

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')

        devices = (
            Device(device_type=devicetype, role=role, name='Device 1', site=site),
            Device(device_type=devicetype, role=role, name='Device 2', site=site),
        )
        Device.objects.bulk_create(devices)

        interfaces = []
        for device in devices:
            for i in range(0, 10):
                interfaces.append(Interface(device=device, type=InterfaceTypeChoices.TYPE_1GE_FIXED, name=f'eth{i}'))
        Interface.objects.bulk_create(interfaces)

        cables = (
            Cable(a_terminations=[interfaces[0]], b_terminations=[interfaces[10]], label='Cable 1'),
            Cable(a_terminations=[interfaces[1]], b_terminations=[interfaces[11]], label='Cable 2'),
            Cable(a_terminations=[interfaces[2]], b_terminations=[interfaces[12]], label='Cable 3'),
        )
        for cable in cables:
            cable.save()

        cls.create_data = [
            {
                'a_terminations': [{
                    'object_type': 'dcim.interface',
                    'object_id': interfaces[4].pk,
                }],
                'b_terminations': [{
                    'object_type': 'dcim.interface',
                    'object_id': interfaces[14].pk,
                }],
                'label': 'Cable 4',
            },
            {
                'a_terminations': [{
                    'object_type': 'dcim.interface',
                    'object_id': interfaces[5].pk,
                }],
                'b_terminations': [{
                    'object_type': 'dcim.interface',
                    'object_id': interfaces[15].pk,
                }],
                'label': 'Cable 5',
            },
            {
                'a_terminations': [{
                    'object_type': 'dcim.interface',
                    'object_id': interfaces[6].pk,
                }],
                'b_terminations': [{
                    'object_type': 'dcim.interface',
                    'object_id': interfaces[16].pk,
                }],
                'label': 'Cable 6',
            },
        ]


class ConnectedDeviceTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')
        devices = (
            Device(device_type=devicetype, role=role, name='TestDevice1', site=site),
            Device(device_type=devicetype, role=role, name='TestDevice2', site=site),
        )
        Device.objects.bulk_create(devices)
        interfaces = (
            Interface(device=devices[0], name='eth0'),
            Interface(device=devices[1], name='eth0'),
            Interface(device=devices[0], name='eth1'),  # Not connected
        )
        Interface.objects.bulk_create(interfaces)

        cable = Cable(a_terminations=[interfaces[0]], b_terminations=[interfaces[1]])
        cable.save()

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_get_connected_device(self):
        url = reverse('dcim-api:connected-device-list')

        url_params = '?peer_device=TestDevice1&peer_interface=eth0'
        response = self.client.get(url + url_params, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'TestDevice2')

        url_params = '?peer_device=TestDevice1&peer_interface=eth1'
        response = self.client.get(url + url_params, **self.header)
        self.assertHttpStatus(response, status.HTTP_404_NOT_FOUND)


class VirtualChassisTest(APIViewTestCases.APIViewTestCase):
    model = VirtualChassis
    brief_fields = ['description', 'display', 'id', 'master', 'member_count', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Test Site', slug='test-site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type', slug='device-type')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role', color='ff0000')

        devices = (
            Device(name='Device 1', device_type=devicetype, role=role, site=site),
            Device(name='Device 2', device_type=devicetype, role=role, site=site),
            Device(name='Device 3', device_type=devicetype, role=role, site=site),
            Device(name='Device 4', device_type=devicetype, role=role, site=site),
            Device(name='Device 5', device_type=devicetype, role=role, site=site),
            Device(name='Device 6', device_type=devicetype, role=role, site=site),
            Device(name='Device 7', device_type=devicetype, role=role, site=site),
            Device(name='Device 8', device_type=devicetype, role=role, site=site),
            Device(name='Device 9', device_type=devicetype, role=role, site=site),
            Device(name='Device 10', device_type=devicetype, role=role, site=site),
            Device(name='Device 11', device_type=devicetype, role=role, site=site),
            Device(name='Device 12', device_type=devicetype, role=role, site=site),
        )
        Device.objects.bulk_create(devices)

        # Create 12 interfaces per device
        interfaces = []
        for i, device in enumerate(devices):
            for j in range(0, 13):
                interfaces.append(
                    # Interface name starts with parent device's position in VC; e.g. 1/1, 1/2, 1/3...
                    Interface(device=device, name=f'{i % 3 + 1}/{j}', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
                )
        Interface.objects.bulk_create(interfaces)

        # Create three VirtualChassis with three members each
        virtual_chassis = (
            VirtualChassis(name='Virtual Chassis 1', master=devices[0], domain='domain-1'),
            VirtualChassis(name='Virtual Chassis 2', master=devices[3], domain='domain-2'),
            VirtualChassis(name='Virtual Chassis 3', master=devices[6], domain='domain-3'),
        )
        VirtualChassis.objects.bulk_create(virtual_chassis)
        Device.objects.filter(pk=devices[0].pk).update(virtual_chassis=virtual_chassis[0], vc_position=1)
        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=virtual_chassis[0], vc_position=2)
        Device.objects.filter(pk=devices[2].pk).update(virtual_chassis=virtual_chassis[0], vc_position=3)
        Device.objects.filter(pk=devices[3].pk).update(virtual_chassis=virtual_chassis[1], vc_position=1)
        Device.objects.filter(pk=devices[4].pk).update(virtual_chassis=virtual_chassis[1], vc_position=2)
        Device.objects.filter(pk=devices[5].pk).update(virtual_chassis=virtual_chassis[1], vc_position=3)
        Device.objects.filter(pk=devices[6].pk).update(virtual_chassis=virtual_chassis[2], vc_position=1)
        Device.objects.filter(pk=devices[7].pk).update(virtual_chassis=virtual_chassis[2], vc_position=2)
        Device.objects.filter(pk=devices[8].pk).update(virtual_chassis=virtual_chassis[2], vc_position=3)

        cls.update_data = {
            'name': 'Virtual Chassis X',
            'domain': 'domain-x',
            'master': devices[1].pk,
        }

        cls.create_data = [
            {
                'name': 'Virtual Chassis 4',
                'domain': 'domain-4',
            },
            {
                'name': 'Virtual Chassis 5',
                'domain': 'domain-5',
            },
            {
                'name': 'Virtual Chassis 6',
                'domain': 'domain-6',
            },
        ]

        cls.bulk_update_data = {
            'domain': 'newdomain',
            'master': None
        }


class PowerPanelTest(APIViewTestCases.APIViewTestCase):
    model = PowerPanel
    brief_fields = ['description', 'display', 'id', 'name', 'powerfeed_count', 'url']
    user_permissions = ('dcim.view_site', )

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site.objects.create(name='Site 1', slug='site-1'),
            Site.objects.create(name='Site 2', slug='site-2'),
        )

        locations = (
            Location.objects.create(name='Location 1', slug='location-1', site=sites[0]),
            Location.objects.create(name='Location 2', slug='location-2', site=sites[0]),
            Location.objects.create(name='Location 3', slug='location-3', site=sites[0]),
            Location.objects.create(name='Location 4', slug='location-3', site=sites[1]),
        )

        power_panels = (
            PowerPanel(site=sites[0], location=locations[0], name='Power Panel 1'),
            PowerPanel(site=sites[0], location=locations[1], name='Power Panel 2'),
            PowerPanel(site=sites[0], location=locations[2], name='Power Panel 3'),
        )
        PowerPanel.objects.bulk_create(power_panels)

        cls.create_data = [
            {
                'name': 'Power Panel 4',
                'site': sites[0].pk,
                'location': locations[0].pk,
            },
            {
                'name': 'Power Panel 5',
                'site': sites[0].pk,
                'location': locations[1].pk,
            },
            {
                'name': 'Power Panel 6',
                'site': sites[0].pk,
                'location': locations[2].pk,
            },
        ]

        cls.bulk_update_data = {
            'site': sites[1].pk,
            'location': locations[3].pk
        }


class PowerFeedTest(APIViewTestCases.APIViewTestCase):
    model = PowerFeed
    brief_fields = ['_occupied', 'cable', 'description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'status': 'planned',
    }
    user_permissions = ('dcim.view_powerpanel', )

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        location = Location.objects.create(site=site, name='Location 1', slug='location-1')
        rackrole = RackRole.objects.create(name='Rack Role 1', slug='rack-role-1', color='ff0000')

        racks = (
            Rack(site=site, location=location, role=rackrole, name='Rack 1'),
            Rack(site=site, location=location, role=rackrole, name='Rack 2'),
            Rack(site=site, location=location, role=rackrole, name='Rack 3'),
            Rack(site=site, location=location, role=rackrole, name='Rack 4'),
        )
        Rack.objects.bulk_create(racks)

        power_panels = (
            PowerPanel(site=site, location=location, name='Power Panel 1'),
            PowerPanel(site=site, location=location, name='Power Panel 2'),
        )
        PowerPanel.objects.bulk_create(power_panels)

        PRIMARY = PowerFeedTypeChoices.TYPE_PRIMARY
        REDUNDANT = PowerFeedTypeChoices.TYPE_REDUNDANT
        power_feeds = (
            PowerFeed(power_panel=power_panels[0], rack=racks[0], name='Power Feed 1A', type=PRIMARY),
            PowerFeed(power_panel=power_panels[1], rack=racks[0], name='Power Feed 1B', type=REDUNDANT),
            PowerFeed(power_panel=power_panels[0], rack=racks[1], name='Power Feed 2A', type=PRIMARY),
            PowerFeed(power_panel=power_panels[1], rack=racks[1], name='Power Feed 2B', type=REDUNDANT),
            PowerFeed(power_panel=power_panels[0], rack=racks[2], name='Power Feed 3A', type=PRIMARY),
            PowerFeed(power_panel=power_panels[1], rack=racks[2], name='Power Feed 3B', type=REDUNDANT),
        )
        PowerFeed.objects.bulk_create(power_feeds)

        cls.create_data = [
            {
                'name': 'Power Feed 4A',
                'power_panel': power_panels[0].pk,
                'rack': racks[3].pk,
                'type': PRIMARY,
            },
            {
                'name': 'Power Feed 4B',
                'power_panel': power_panels[1].pk,
                'rack': racks[3].pk,
                'type': REDUNDANT,
            },
        ]


class VirtualDeviceContextTest(APIViewTestCases.APIViewTestCase):
    model = VirtualDeviceContext
    brief_fields = ['description', 'device', 'display', 'id', 'identifier', 'name', 'url']
    bulk_update_data = {
        'status': 'planned',
    }

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Test Site', slug='test-site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type', slug='device-type')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role', color='ff0000')

        devices = (
            Device(name='Device 1', device_type=devicetype, role=role, site=site),
            Device(name='Device 2', device_type=devicetype, role=role, site=site),
            Device(name='Device 3', device_type=devicetype, role=role, site=site),
        )
        Device.objects.bulk_create(devices)

        vdcs = (
            VirtualDeviceContext(device=devices[1], name='VDC 1', identifier=1, status='active'),
            VirtualDeviceContext(device=devices[1], name='VDC 2', identifier=2, status='active'),
            VirtualDeviceContext(device=devices[2], name='VDC 1', identifier=1, status='active'),
            VirtualDeviceContext(device=devices[2], name='VDC 2', identifier=2, status='active'),
            VirtualDeviceContext(device=devices[2], name='VDC 3', identifier=3, status='active'),
            VirtualDeviceContext(device=devices[2], name='VDC 4', identifier=4, status='active'),
            VirtualDeviceContext(device=devices[2], name='VDC 5', identifier=5, status='active'),
        )
        VirtualDeviceContext.objects.bulk_create(vdcs)

        cls.create_data = [
            {
                'device': devices[0].pk,
                'status': 'active',
                'name': 'VDC 1',
                'identifier': 1,
            },
            {
                'device': devices[0].pk,
                'status': 'active',
                'name': 'VDC 2',
                'identifier': 2,
            },
            {
                'device': devices[1].pk,
                'status': 'active',
                'name': 'VDC 3',
                # Omit identifier to test uniqueness constraint
            },
        ]


class MACAddressTest(APIViewTestCases.APIViewTestCase):
    model = MACAddress
    brief_fields = ['description', 'display', 'id', 'mac_address', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        device = create_test_device(name='Device 1')
        interfaces = (
            Interface(device=device, name='Interface 1', type='1000base-t'),
            Interface(device=device, name='Interface 2', type='1000base-t'),
            Interface(device=device, name='Interface 3', type='1000base-t'),
            Interface(device=device, name='Interface 4', type='1000base-t'),
            Interface(device=device, name='Interface 5', type='1000base-t'),
        )
        Interface.objects.bulk_create(interfaces)

        mac_addresses = (
            MACAddress(mac_address='00:00:00:00:00:01', assigned_object=interfaces[0]),
            MACAddress(mac_address='00:00:00:00:00:02', assigned_object=interfaces[1]),
            MACAddress(mac_address='00:00:00:00:00:03', assigned_object=interfaces[2]),
        )
        MACAddress.objects.bulk_create(mac_addresses)

        cls.create_data = [
            {
                'mac_address': '00:00:00:00:00:04',
                'assigned_object_type': 'dcim.interface',
                'assigned_object_id': interfaces[3].pk,
            },
            {
                'mac_address': '00:00:00:00:00:05',
                'assigned_object_type': 'dcim.interface',
                'assigned_object_id': interfaces[4].pk,
            },
            {
                'mac_address': '00:00:00:00:00:06',
            },
        ]
