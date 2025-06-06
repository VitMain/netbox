import tempfile
from pathlib import Path

from django.forms import ValidationError
from django.test import tag, TestCase

from core.models import DataSource, ObjectType
from dcim.models import Device, DeviceRole, DeviceType, Location, Manufacturer, Platform, Region, Site, SiteGroup
from extras.models import ConfigContext, ConfigTemplate, Tag
from tenancy.models import Tenant, TenantGroup
from utilities.exceptions import AbortRequest
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class TagTest(TestCase):

    def test_default_ordering_weight_then_name_is_set(self):
        Tag.objects.create(name='Tag 1', slug='tag-1', weight=3000)
        Tag.objects.create(name='Tag 2', slug='tag-2')  # Default: 1000
        Tag.objects.create(name='Tag 3', slug='tag-3', weight=2000)
        Tag.objects.create(name='Tag 4', slug='tag-4', weight=2000)

        tags = Tag.objects.all()

        self.assertEqual(tags[0].slug, 'tag-2')
        self.assertEqual(tags[1].slug, 'tag-3')
        self.assertEqual(tags[2].slug, 'tag-4')
        self.assertEqual(tags[3].slug, 'tag-1')

    def test_tag_related_manager_ordering_weight_then_name(self):
        tags = [
            Tag.objects.create(name='Tag 1', slug='tag-1', weight=3000),
            Tag.objects.create(name='Tag 2', slug='tag-2'),  # Default: 1000
            Tag.objects.create(name='Tag 3', slug='tag-3', weight=2000),
            Tag.objects.create(name='Tag 4', slug='tag-4', weight=2000),
        ]

        site = Site.objects.create(name='Site 1')
        for _tag in tags:
            site.tags.add(_tag)
        site.save()

        site = Site.objects.first()
        tags = site.tags.all()

        self.assertEqual(tags[0].slug, 'tag-2')
        self.assertEqual(tags[1].slug, 'tag-3')
        self.assertEqual(tags[2].slug, 'tag-4')
        self.assertEqual(tags[3].slug, 'tag-1')

    def test_create_tag_unicode(self):
        tag = Tag(name='Testing Unicode: 台灣')
        tag.save()

        self.assertEqual(tag.slug, 'testing-unicode-台灣')

    def test_object_type_validation(self):
        region = Region.objects.create(name='Region 1', slug='region-1')
        sitegroup = SiteGroup.objects.create(name='Site Group 1', slug='site-group-1')

        # Create a Tag that can only be applied to Regions
        tag = Tag.objects.create(name='Tag 1', slug='tag-1')
        tag.object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'region'))

        # Apply the Tag to a Region
        region.tags.add(tag)
        self.assertIn(tag, region.tags.all())

        # Apply the Tag to a SiteGroup
        with self.assertRaises(AbortRequest):
            sitegroup.tags.add(tag)


class ConfigContextTest(TestCase):
    """
    These test cases deal with the weighting, ordering, and deep merge logic of config context data.

    It also ensures the various config context querysets are consistent.
    """
    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        region = Region.objects.create(name='Region')
        sitegroup = SiteGroup.objects.create(name='Site Group')
        site = Site.objects.create(name='Site 1', slug='site-1', region=region, group=sitegroup)
        location = Location.objects.create(name='Location 1', slug='location-1', site=site)
        Platform.objects.create(name='Platform')
        tenantgroup = TenantGroup.objects.create(name='Tenant Group')
        Tenant.objects.create(name='Tenant', group=tenantgroup)
        Tag.objects.create(name='Tag', slug='tag')
        Tag.objects.create(name='Tag2', slug='tag2')

        Device.objects.create(
            name='Device 1',
            device_type=devicetype,
            role=role,
            site=site,
            location=location
        )

    def test_higher_weight_wins(self):
        device = Device.objects.first()
        context1 = ConfigContext(
            name="context 1",
            weight=101,
            data={
                "a": 123,
                "b": 456,
                "c": 777
            }
        )
        context2 = ConfigContext(
            name="context 2",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 789
            }
        )
        ConfigContext.objects.bulk_create([context1, context2])

        expected_data = {
            "a": 123,
            "b": 456,
            "c": 777
        }
        self.assertEqual(device.get_config_context(), expected_data)

    def test_name_ordering_after_weight(self):
        device = Device.objects.first()
        context1 = ConfigContext(
            name="context 1",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 777
            }
        )
        context2 = ConfigContext(
            name="context 2",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 789
            }
        )
        ConfigContext.objects.bulk_create([context1, context2])

        expected_data = {
            "a": 123,
            "b": 456,
            "c": 789
        }
        self.assertEqual(device.get_config_context(), expected_data)

    def test_annotation_same_as_get_for_object(self):
        """
        This test incorporates features from all of the above tests cases to ensure
        the annotate_config_context_data() and get_for_object() queryset methods are the same.
        """
        device = Device.objects.first()
        context1 = ConfigContext(
            name="context 1",
            weight=101,
            data={
                "a": 123,
                "b": 456,
                "c": 777
            }
        )
        context2 = ConfigContext(
            name="context 2",
            weight=100,
            data={
                "a": 123,
                "b": 456,
                "c": 789
            }
        )
        context3 = ConfigContext(
            name="context 3",
            weight=99,
            data={
                "d": 1
            }
        )
        context4 = ConfigContext(
            name="context 4",
            weight=99,
            data={
                "d": 2
            }
        )
        ConfigContext.objects.bulk_create([context1, context2, context3, context4])

        annotated_queryset = Device.objects.filter(name=device.name).annotate_config_context_data()
        self.assertEqual(device.get_config_context(), annotated_queryset[0].get_config_context())

    def test_annotation_same_as_get_for_object_device_relations(self):
        region = Region.objects.first()
        sitegroup = SiteGroup.objects.first()
        site = Site.objects.first()
        location = Location.objects.first()
        platform = Platform.objects.first()
        tenantgroup = TenantGroup.objects.first()
        tenant = Tenant.objects.first()
        tag = Tag.objects.first()

        region_context = ConfigContext.objects.create(
            name="region",
            weight=100,
            data={
                "region": 1
            }
        )
        region_context.regions.add(region)

        sitegroup_context = ConfigContext.objects.create(
            name="sitegroup",
            weight=100,
            data={
                "sitegroup": 1
            }
        )
        sitegroup_context.site_groups.add(sitegroup)

        site_context = ConfigContext.objects.create(
            name="site",
            weight=100,
            data={
                "site": 1
            }
        )
        site_context.sites.add(site)

        location_context = ConfigContext.objects.create(
            name="location",
            weight=100,
            data={
                "location": 1
            }
        )
        location_context.locations.add(location)

        platform_context = ConfigContext.objects.create(
            name="platform",
            weight=100,
            data={
                "platform": 1
            }
        )
        platform_context.platforms.add(platform)

        tenant_group_context = ConfigContext.objects.create(
            name="tenant group",
            weight=100,
            data={
                "tenant_group": 1
            }
        )
        tenant_group_context.tenant_groups.add(tenantgroup)

        tenant_context = ConfigContext.objects.create(
            name="tenant",
            weight=100,
            data={
                "tenant": 1
            }
        )
        tenant_context.tenants.add(tenant)

        tag_context = ConfigContext.objects.create(
            name="tag",
            weight=100,
            data={
                "tag": 1
            }
        )
        tag_context.tags.add(tag)

        device = Device.objects.create(
            name="Device 2",
            site=site,
            location=location,
            tenant=tenant,
            platform=platform,
            role=DeviceRole.objects.first(),
            device_type=DeviceType.objects.first()
        )
        device.tags.add(tag)

        annotated_queryset = Device.objects.filter(name=device.name).annotate_config_context_data()
        self.assertEqual(device.get_config_context(), annotated_queryset[0].get_config_context())

    def test_annotation_same_as_get_for_object_virtualmachine_relations(self):
        region = Region.objects.first()
        sitegroup = SiteGroup.objects.first()
        site = Site.objects.first()
        platform = Platform.objects.first()
        tenantgroup = TenantGroup.objects.first()
        tenant = Tenant.objects.first()
        tag = Tag.objects.first()
        cluster_type = ClusterType.objects.create(name="Cluster Type")
        cluster_group = ClusterGroup.objects.create(name="Cluster Group")
        cluster = Cluster.objects.create(
            name="Cluster",
            group=cluster_group,
            type=cluster_type,
            scope=site,
        )

        region_context = ConfigContext.objects.create(
            name="region",
            weight=100,
            data={"region": 1}
        )
        region_context.regions.add(region)

        sitegroup_context = ConfigContext.objects.create(
            name="sitegroup",
            weight=100,
            data={"sitegroup": 1}
        )
        sitegroup_context.site_groups.add(sitegroup)

        site_context = ConfigContext.objects.create(
            name="site",
            weight=100,
            data={"site": 1}
        )
        site_context.sites.add(site)

        platform_context = ConfigContext.objects.create(
            name="platform",
            weight=100,
            data={"platform": 1}
        )
        platform_context.platforms.add(platform)

        tenant_group_context = ConfigContext.objects.create(
            name="tenant group",
            weight=100,
            data={"tenant_group": 1}
        )
        tenant_group_context.tenant_groups.add(tenantgroup)

        tenant_context = ConfigContext.objects.create(
            name="tenant",
            weight=100,
            data={"tenant": 1}
        )
        tenant_context.tenants.add(tenant)

        tag_context = ConfigContext.objects.create(
            name="tag",
            weight=100,
            data={"tag": 1}
        )
        tag_context.tags.add(tag)

        cluster_type_context = ConfigContext.objects.create(
            name="cluster type",
            weight=100,
            data={"cluster_type": 1}
        )
        cluster_type_context.cluster_types.add(cluster_type)

        cluster_group_context = ConfigContext.objects.create(
            name="cluster group",
            weight=100,
            data={"cluster_group": 1}
        )
        cluster_group_context.cluster_groups.add(cluster_group)

        cluster_context = ConfigContext.objects.create(
            name="cluster",
            weight=100,
            data={"cluster": 1}
        )
        cluster_context.clusters.add(cluster)

        virtual_machine = VirtualMachine.objects.create(
            name="VM 1",
            cluster=cluster,
            tenant=tenant,
            platform=platform,
            role=DeviceRole.objects.first()
        )
        virtual_machine.tags.add(tag)

        annotated_queryset = VirtualMachine.objects.filter(name=virtual_machine.name).annotate_config_context_data()
        self.assertEqual(virtual_machine.get_config_context(), annotated_queryset[0].get_config_context())

    def test_virtualmachine_site_context(self):
        """
        Check that config context associated with a site applies to a VM whether the VM is assigned
        directly to that site or via its cluster.
        """
        site = Site.objects.first()
        cluster_type = ClusterType.objects.create(name="Cluster Type")
        cluster = Cluster.objects.create(name="Cluster", type=cluster_type, scope=site)
        vm_role = DeviceRole.objects.first()

        # Create a ConfigContext associated with the site
        context = ConfigContext.objects.create(
            name="context1",
            weight=100,
            data={"foo": True}
        )
        context.sites.add(site)

        # Create one VM assigned directly to the site, and one assigned via the cluster
        vm1 = VirtualMachine.objects.create(name="VM 1", site=site, role=vm_role)
        vm2 = VirtualMachine.objects.create(name="VM 2", cluster=cluster, role=vm_role)

        # Check that their individually-rendered config contexts are identical
        self.assertEqual(
            vm1.get_config_context(),
            vm2.get_config_context()
        )

        # Check that their annotated config contexts are identical
        vms = VirtualMachine.objects.filter(pk__in=(vm1.pk, vm2.pk)).annotate_config_context_data()
        self.assertEqual(
            vms[0].get_config_context(),
            vms[1].get_config_context()
        )

    def test_multiple_tags_return_distinct_objects(self):
        """
        Tagged items use a generic relationship, which results in duplicate rows being returned when queried.
        This is combated by appending distinct() to the config context querysets. This test creates a config
        context assigned to two tags and ensures objects related by those same two tags result in only a single
        config context record being returned.

        See https://github.com/netbox-community/netbox/issues/5314
        """
        site = Site.objects.first()
        platform = Platform.objects.first()
        tenant = Tenant.objects.first()
        tags = Tag.objects.all()

        tag_context = ConfigContext.objects.create(
            name="tag",
            weight=100,
            data={
                "tag": 1
            }
        )
        tag_context.tags.set(tags)

        device = Device.objects.create(
            name="Device 3",
            site=site,
            tenant=tenant,
            platform=platform,
            role=DeviceRole.objects.first(),
            device_type=DeviceType.objects.first()
        )
        device.tags.set(tags)

        annotated_queryset = Device.objects.filter(name=device.name).annotate_config_context_data()
        self.assertEqual(ConfigContext.objects.get_for_object(device).count(), 1)
        self.assertEqual(device.get_config_context(), annotated_queryset[0].get_config_context())

    def test_multiple_tags_return_distinct_objects_with_seperate_config_contexts(self):
        """
        Tagged items use a generic relationship, which results in duplicate rows being returned when queried.
        This is combatted by by appending distinct() to the config context querysets. This test creates a config
        context assigned to two tags and ensures objects related by those same two tags result in only a single
        config context record being returned.

        This test case is seperate from the above in that it deals with multiple config context objects in play.

        See https://github.com/netbox-community/netbox/issues/5387
        """
        site = Site.objects.first()
        platform = Platform.objects.first()
        tenant = Tenant.objects.first()
        tag1, tag2 = list(Tag.objects.all())

        tag_context_1 = ConfigContext.objects.create(
            name="tag-1",
            weight=100,
            data={
                "tag": 1
            }
        )
        tag_context_1.tags.add(tag1)

        tag_context_2 = ConfigContext.objects.create(
            name="tag-2",
            weight=100,
            data={
                "tag": 1
            }
        )
        tag_context_2.tags.add(tag2)

        device = Device.objects.create(
            name="Device 3",
            site=site,
            tenant=tenant,
            platform=platform,
            role=DeviceRole.objects.first(),
            device_type=DeviceType.objects.first()
        )
        device.tags.set([tag1, tag2])

        annotated_queryset = Device.objects.filter(name=device.name).annotate_config_context_data()
        self.assertEqual(ConfigContext.objects.get_for_object(device).count(), 2)
        self.assertEqual(device.get_config_context(), annotated_queryset[0].get_config_context())

    def test_valid_local_context_data(self):
        device = Device.objects.first()
        device.local_context_data = None
        device.clean()

        device.local_context_data = {"foo": "bar"}
        device.clean()

    def test_invalid_local_context_data(self):
        device = Device.objects.first()

        device.local_context_data = ""
        with self.assertRaises(ValidationError):
            device.clean()

        device.local_context_data = 0
        with self.assertRaises(ValidationError):
            device.clean()

        device.local_context_data = False
        with self.assertRaises(ValidationError):
            device.clean()

        device.local_context_data = 'foo'
        with self.assertRaises(ValidationError):
            device.clean()


class ConfigTemplateTest(TestCase):
    """
    TODO: These test cases deal with the weighting, ordering, and deep merge logic of config context data.
    """
    MAIN_TEMPLATE = """
    {%- include 'base.j2' %}
    """.strip()
    BASE_TEMPLATE = """
    Hi
    """.strip()

    @classmethod
    def _create_template_file(cls, templates_dir, file_name, content):
        template_file_name = file_name
        if not template_file_name.endswith('j2'):
            template_file_name += '.j2'
        temp_file_path = templates_dir / template_file_name

        with open(temp_file_path, 'w') as f:
            f.write(content)

    @classmethod
    def setUpTestData(cls):
        temp_dir = tempfile.TemporaryDirectory()
        templates_dir = Path(temp_dir.name) / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)

        cls._create_template_file(templates_dir, 'base.j2', cls.BASE_TEMPLATE)
        cls._create_template_file(templates_dir, 'main.j2', cls.MAIN_TEMPLATE)

        data_source = DataSource(
            name="Test DataSource",
            type="local",
            source_url=str(templates_dir),
        )
        data_source.save()
        data_source.sync()

        base_config_template = ConfigTemplate(
            name="BaseTemplate",
            data_file=data_source.datafiles.filter(path__endswith='base.j2').first()
        )
        base_config_template.clean()
        base_config_template.save()
        cls.base_config_template = base_config_template

        main_config_template = ConfigTemplate(
            name="MainTemplate",
            data_file=data_source.datafiles.filter(path__endswith='main.j2').first()
        )
        main_config_template.clean()
        main_config_template.save()
        cls.main_config_template = main_config_template

    @tag('regression')
    def test_config_template_with_data_source(self):
        self.assertEqual(self.BASE_TEMPLATE, self.base_config_template.render({}))

    @tag('regression')
    def test_config_template_with_data_source_nested_templates(self):
        self.assertEqual(self.BASE_TEMPLATE, self.main_config_template.render({}))
