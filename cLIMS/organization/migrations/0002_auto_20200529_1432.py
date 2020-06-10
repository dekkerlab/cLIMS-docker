# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2020-05-29 18:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        ('wetLab', '0001_initial'),
        ('dryLab', '0002_auto_20200529_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='experimentset',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='setDoc', to='wetLab.Document'),
        ),
        migrations.AddField(
            model_name='experimentset',
            name='experimentSet_exp',
            field=models.ManyToManyField(related_name='setExp', to='organization.Experiment'),
        ),
        migrations.AddField(
            model_name='experimentset',
            name='experimentSet_type',
            field=models.ForeignKey(help_text='The categorization of the set of experiments.', on_delete=django.db.models.deletion.CASCADE, related_name='setChoice', to='organization.Choice'),
        ),
        migrations.AddField(
            model_name='experimentset',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expSetProject', to='organization.Project'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='antibody',
            field=models.ForeignKey(blank=True, help_text='For Cut&Run experiments reference to a antibody object', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expAntibody', to='wetLab.Antibody'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='authentication_docs',
            field=models.ManyToManyField(blank=True, help_text='Attach any authentication document for your biosample here. e.g. Fragment Analyzer document, Gel images.', related_name='expAddProto', to='wetLab.Protocol'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='contributing_labs',
            field=models.ManyToManyField(blank=True, help_text='Contributing labs for this experiment.', to='organization.ContributingLabs'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='document',
            field=models.ForeignKey(blank=True, help_text='Documents that provide additional information (not data file).', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wetLab.Document'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='experiment_biosample',
            field=models.ForeignKey(help_text='Starting biological material.', on_delete=django.db.models.deletion.CASCADE, related_name='expBio', to='wetLab.Biosample'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='experiment_enzyme',
            field=models.ForeignKey(blank=True, help_text='The enzyme used for digestion of the DNA.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expEnz', to='wetLab.Enzyme'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='imageObjects',
            field=models.ManyToManyField(blank=True, help_text='Any additional image related to this experiment.', related_name='expImg', to='dryLab.ImageObjects'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expProject', to='organization.Project'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='protocol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expPro', to='wetLab.Protocol'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='references',
            field=models.ForeignKey(blank=True, help_text='The publications that provide more information about the object.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='organization.Publication'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='type',
            field=models.ForeignKey(help_text='JsonObjField', on_delete=django.db.models.deletion.CASCADE, related_name='expType', to='organization.JsonObjField'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='variation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expProVar', to='wetLab.Protocol', verbose_name='protocol_variations'),
        ),
        migrations.AddField(
            model_name='award',
            name='award_exp',
            field=models.ManyToManyField(related_name='awardExp', to='organization.Experiment'),
        ),
        migrations.AddField(
            model_name='award',
            name='award_project',
            field=models.ManyToManyField(related_name='awardPro', to='organization.Project'),
        ),
    ]