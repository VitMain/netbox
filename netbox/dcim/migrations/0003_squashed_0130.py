from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0002_squashed'),
        ('virtualization', '0001_squashed_0022'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0001_squashed'),
        ('tenancy', '0001_squashed_0012'),
        ('extras', '0002_squashed_0059'),
    ]

    replaces = [
        ('dcim', '0003_auto_20160628_1721'),
        ('dcim', '0004_auto_20160701_2049'),
        ('dcim', '0005_auto_20160706_1722'),
        ('dcim', '0006_add_device_primary_ip4_ip6'),
        ('dcim', '0007_device_copy_primary_ip'),
        ('dcim', '0008_device_remove_primary_ip'),
        ('dcim', '0009_site_32bit_asn_support'),
        ('dcim', '0010_devicebay_installed_device_set_null'),
        ('dcim', '0011_devicetype_part_number'),
        ('dcim', '0012_site_rack_device_add_tenant'),
        ('dcim', '0013_add_interface_form_factors'),
        ('dcim', '0014_rack_add_type_width'),
        ('dcim', '0015_rack_add_u_height_validator'),
        ('dcim', '0016_module_add_manufacturer'),
        ('dcim', '0017_rack_add_role'),
        ('dcim', '0018_device_add_asset_tag'),
        ('dcim', '0019_new_iface_form_factors'),
        ('dcim', '0020_rack_desc_units'),
        ('dcim', '0021_add_ff_flexstack'),
        ('dcim', '0022_color_names_to_rgb'),
        ('dcim', '0023_devicetype_comments'),
        ('dcim', '0024_site_add_contact_fields'),
        ('dcim', '0025_devicetype_add_interface_ordering'),
        ('dcim', '0026_add_rack_reservations'),
        ('dcim', '0027_device_add_site'),
        ('dcim', '0028_device_copy_rack_to_site'),
        ('dcim', '0029_allow_rackless_devices'),
        ('dcim', '0030_interface_add_lag'),
        ('dcim', '0031_regions'),
        ('dcim', '0032_device_increase_name_length'),
        ('dcim', '0033_rackreservation_rack_editable'),
        ('dcim', '0034_rename_module_to_inventoryitem'),
        ('dcim', '0035_device_expand_status_choices'),
        ('dcim', '0036_add_ff_juniper_vcp'),
        ('dcim', '0037_unicode_literals'),
        ('dcim', '0038_wireless_interfaces'),
        ('dcim', '0039_interface_add_enabled_mtu'),
        ('dcim', '0040_inventoryitem_add_asset_tag_description'),
        ('dcim', '0041_napalm_integration'),
        ('dcim', '0042_interface_ff_10ge_cx4'),
        ('dcim', '0043_device_component_name_lengths'),
        ('dcim', '0044_virtualization'),
        ('dcim', '0045_devicerole_vm_role'),
        ('dcim', '0046_rack_lengthen_facility_id'),
        ('dcim', '0047_more_100ge_form_factors'),
        ('dcim', '0048_rack_serial'),
        ('dcim', '0049_rackreservation_change_user'),
        ('dcim', '0050_interface_vlan_tagging'),
        ('dcim', '0051_rackreservation_tenant'),
        ('dcim', '0052_virtual_chassis'),
        ('dcim', '0053_platform_manufacturer'),
        ('dcim', '0054_site_status_timezone_description'),
        ('dcim', '0055_virtualchassis_ordering'),
        ('dcim', '0056_django2'),
        ('dcim', '0057_tags'),
        ('dcim', '0058_relax_rack_naming_constraints'),
        ('dcim', '0059_site_latitude_longitude'),
        ('dcim', '0060_change_logging'),
        ('dcim', '0061_platform_napalm_args'),
        ('dcim', '0062_interface_mtu'),
        ('dcim', '0063_device_local_context_data'),
        ('dcim', '0064_remove_platform_rpc_client'),
        ('dcim', '0065_front_rear_ports'),
        ('dcim', '0066_cables'),
        ('dcim', '0067_device_type_remove_qualifiers'),
        ('dcim', '0068_rack_new_fields'),
        ('dcim', '0069_deprecate_nullablecharfield'),
        ('dcim', '0070_custom_tag_models'),
        ('dcim', '0071_device_components_add_description'),
        ('dcim', '0072_powerfeeds'),
        ('dcim', '0073_interface_form_factor_to_type'),
        ('dcim', '0074_increase_field_length_platform_name_slug'),
        ('dcim', '0075_cable_devices'),
        ('dcim', '0076_console_port_types'),
        ('dcim', '0077_power_types'),
        ('dcim', '0078_3569_site_fields'),
        ('dcim', '0079_3569_rack_fields'),
        ('dcim', '0080_3569_devicetype_fields'),
        ('dcim', '0081_3569_device_fields'),
        ('dcim', '0082_3569_interface_fields'),
        ('dcim', '0082_3569_port_fields'),
        ('dcim', '0083_3569_cable_fields'),
        ('dcim', '0084_3569_powerfeed_fields'),
        ('dcim', '0085_3569_poweroutlet_fields'),
        ('dcim', '0086_device_name_nonunique'),
        ('dcim', '0087_role_descriptions'),
        ('dcim', '0088_powerfeed_available_power'),
        ('dcim', '0089_deterministic_ordering'),
        ('dcim', '0090_cable_termination_models'),
        ('dcim', '0091_interface_type_other'),
        ('dcim', '0092_fix_rack_outer_unit'),
        ('dcim', '0093_device_component_ordering'),
        ('dcim', '0094_device_component_template_ordering'),
        ('dcim', '0095_primary_model_ordering'),
        ('dcim', '0096_interface_ordering'),
        ('dcim', '0097_interfacetemplate_type_other'),
        ('dcim', '0098_devicetype_images'),
        ('dcim', '0099_powerfeed_negative_voltage'),
        ('dcim', '0100_mptt_remove_indexes'),
        ('dcim', '0101_nested_rackgroups'),
        ('dcim', '0102_nested_rackgroups_rebuild'),
        ('dcim', '0103_standardize_description'),
        ('dcim', '0104_correct_infiniband_types'),
        ('dcim', '0105_interface_name_collation'),
        ('dcim', '0106_role_default_color'),
        ('dcim', '0107_component_labels'),
        ('dcim', '0108_add_tags'),
        ('dcim', '0109_interface_remove_vm'),
        ('dcim', '0110_virtualchassis_name'),
        ('dcim', '0111_component_template_description'),
        ('dcim', '0112_standardize_components'),
        ('dcim', '0113_nullbooleanfield_to_booleanfield'),
        ('dcim', '0114_update_jsonfield'),
        ('dcim', '0115_rackreservation_order'),
        ('dcim', '0116_rearport_max_positions'),
        ('dcim', '0117_custom_field_data'),
        ('dcim', '0118_inventoryitem_mptt'),
        ('dcim', '0119_inventoryitem_mptt_rebuild'),
        ('dcim', '0120_cache_cable_peer'),
        ('dcim', '0121_cablepath'),
        ('dcim', '0122_standardize_name_length'),
        ('dcim', '0123_standardize_models'),
        ('dcim', '0124_mark_connected'),
        ('dcim', '0125_console_port_speed'),
        ('dcim', '0126_rename_rackgroup_location'),
        ('dcim', '0127_device_location'),
        ('dcim', '0128_device_location_populate'),
        ('dcim', '0129_interface_parent'),
        ('dcim', '0130_sitegroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='tagged_vlans',
            field=models.ManyToManyField(blank=True, related_name='interfaces_as_tagged', to='ipam.VLAN'),
        ),
        migrations.AddField(
            model_name='interface',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='interface',
            name='untagged_vlan',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='interfaces_as_untagged',
                to='ipam.vlan',
            ),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='device_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'
            ),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='rear_port',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='frontport_templates',
                to='dcim.rearporttemplate',
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='_cable_peer_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='cable',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='device',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.device'
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='rear_port',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='frontports', to='dcim.rearport'
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='manufacturer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name='device_types', to='dcim.manufacturer'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='devicebaytemplate',
            name='device_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'
            ),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='device',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.device'
            ),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='installed_device',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='parent_bay',
                to='dcim.device',
            ),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='device',
            name='cluster',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='devices',
                to='virtualization.cluster',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='device_role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='dcim.devicerole'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='device_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='dcim.devicetype'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='devices',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='platform',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='devices',
                to='dcim.platform',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='primary_ip4',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='primary_ip4_for',
                to='ipam.ipaddress',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='primary_ip6',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='primary_ip6_for',
                to='ipam.ipaddress',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='rack',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='devices',
                to='dcim.rack',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='site',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='dcim.site'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='device',
            name='tenant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='devices',
                to='tenancy.tenant',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='virtual_chassis',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='members',
                to='dcim.virtualchassis',
            ),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='device_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_cable_peer_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_path',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='cable',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='device',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.device'
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='device_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='_cable_peer_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='_path',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='cable',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='device',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.device'
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='cablepath',
            name='destination_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='cablepath',
            name='origin_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype'
            ),
        ),
        migrations.AddField(
            model_name='cable',
            name='_termination_a_device',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device'
            ),
        ),
        migrations.AddField(
            model_name='cable',
            name='_termination_b_device',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device'
            ),
        ),
        migrations.AddField(
            model_name='cable',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='cable',
            name='termination_a_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='cable',
            name='termination_b_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='rearporttemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='rearport',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='rack',
            unique_together={('location', 'facility_id'), ('location', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='powerporttemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='powerport',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='powerpanel',
            unique_together={('site', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='poweroutlettemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='poweroutlet',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='powerfeed',
            unique_together={('power_panel', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together={('site', 'name'), ('site', 'slug')},
        ),
        migrations.AlterUniqueTogether(
            name='inventoryitem',
            unique_together={('device', 'parent', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='interfacetemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='interface',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='frontporttemplate',
            unique_together={('rear_port', 'rear_port_position'), ('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='frontport',
            unique_together={('device', 'name'), ('rear_port', 'rear_port_position')},
        ),
        migrations.AlterUniqueTogether(
            name='devicetype',
            unique_together={('manufacturer', 'model'), ('manufacturer', 'slug')},
        ),
        migrations.AlterUniqueTogether(
            name='devicebaytemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='devicebay',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together={
                ('rack', 'position', 'face'),
                ('virtual_chassis', 'vc_position'),
                ('site', 'tenant', 'name'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='consoleserverporttemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='consoleserverport',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='consoleporttemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='consoleport',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='cablepath',
            unique_together={('origin_type', 'origin_id')},
        ),
        migrations.AlterUniqueTogether(
            name='cable',
            unique_together={('termination_b_type', 'termination_b_id'), ('termination_a_type', 'termination_a_id')},
        ),
    ]
