# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import pkg_resources

import qiime2


def _get_data_from_tests(path):
    return pkg_resources.resource_filename('q2_fmt.tests',
                                           os.path.join('data', path))


def alpha_md_factory():
    return qiime2.Metadata.load(
        _get_data_from_tests('sample_metadata_alpha_div.tsv'))


def beta_md_factory():
    return qiime2.Metadata.load(
        _get_data_from_tests('sample_metadata_donors.tsv'))


def alpha_div_factory():
    return qiime2.Artifact.import_data(
        'SampleData[AlphaDiversity]', _get_data_from_tests('alpha_div.tsv'))


def beta_div_factory():
    return qiime2.Artifact.import_data(
        'DistanceMatrix', _get_data_from_tests('dist_matrix_donors.tsv'))


def faithpd_md_factory():
    return qiime2.Metadata.load(
        _get_data_from_tests('metadata-faithpd.tsv')
    )


def faithpd_div_factory():
    return qiime2.Artifact.import_data(
        'SampleData[AlphaDiversity]', _get_data_from_tests('faithpd.tsv')
    )


def peds_feature_table_factory():
    return qiime2.Artifact.import_data(
        'FeatureTable[Frequency]', _get_data_from_tests('feature-table.biom')
    )


def peds_md_factory():
    return qiime2.Metadata.load(
        _get_data_from_tests('md-peds-usage.txt')
    )


def peds_dist_factory():
    return qiime2.Artifact.import_data(
        "GroupDist[Ordered, Matched] % Properties('peds')",
        _get_data_from_tests('peds_dist')
    )


def group_timepoints_alpha_independent(use):
    alpha = use.init_artifact('alpha', alpha_div_factory)
    metadata = use.init_metadata('metadata', alpha_md_factory)

    timepoints, references = use.action(
        use.UsageAction('fmt', 'group_timepoints'),
        use.UsageInputs(
            diversity_measure=alpha,
            distance_to='donor',
            metadata=metadata,
            time_column='days_post_transplant',
            reference_column='relevant_donor',
            subject_column=False
        ),
        use.UsageOutputNames(
            timepoint_dists='timepoint_dists',
            reference_dists='reference_dists'
        )
    )

    timepoints.assert_output_type('GroupDist[Ordered, Independent]')
    references.assert_output_type('GroupDist[Unordered, Independent]')


def group_timepoints_beta(use):
    beta = use.init_artifact('beta', beta_div_factory)
    metadata = use.init_metadata('metadata', beta_md_factory)

    timepoints, references = use.action(
        use.UsageAction('fmt', 'group_timepoints'),
        use.UsageInputs(
            diversity_measure=beta,
            metadata=metadata,
            distance_to='donor',
            time_column='days_post_transplant',
            reference_column='relevant_donor',
            subject_column='subject',
        ),
        use.UsageOutputNames(
            timepoint_dists='timepoint_dists',
            reference_dists='reference_dists'
        )
    )

    timepoints.assert_output_type('GroupDist[Ordered, Matched]')
    references.assert_output_type('GroupDist[Unordered, Independent]')


# Engraftment example using faith PD, baseline0 comparison
def engraftment_baseline(use):
    md = use.init_metadata('md', faithpd_md_factory)
    div_measure = use.init_artifact('div_measure', faithpd_div_factory)

    stats_table, raincloud = use.action(
        use.UsageAction('fmt', 'engraftment'),
        use.UsageInputs(
            diversity_measure=div_measure,
            metadata=md,
            distance_to='donor',
            compare='baseline',
            time_column='week',
            reference_column='InitialDonorSampleID',
            subject_column='SubjectID',
            where='SampleType="stool"',
            filter_missing_references=True,
            against_group='0',
            p_val_approx='asymptotic',
        ),
        use.UsageOutputNames(
            stats='stats',
            raincloud_plot='raincloud_plot'
        )
    )

    stats_table.assert_output_type('StatsTable[Pairwise]')
    raincloud.assert_output_type('Visualization')


def peds_method(use):
    md = use.init_metadata('md', peds_md_factory)
    peds_table = use.init_artifact('peds_table', peds_feature_table_factory)

    peds_group_dists, = use.action(
        use.UsageAction('fmt', 'sample_peds'),
        use.UsageInputs(
            table=peds_table,
            metadata=md,
            time_column='time_point',
            reference_column='Donor',
            subject_column='SubjectID'
        ),
        use.UsageOutputNames(
            peds_dists='peds_dist'
        )

    )

    peds_group_dists.assert_output_type("GroupDist[Ordered, Matched] %"
                                        " Properties('peds')")


def feature_peds_method(use):
    md = use.init_metadata('md', peds_md_factory)
    peds_table = use.init_artifact('peds_table', peds_feature_table_factory)

    peds_group_dists, = use.action(
        use.UsageAction('fmt', 'feature_peds'),
        use.UsageInputs(
            table=peds_table,
            metadata=md,
            time_column='time_point',
            reference_column='Donor',
            subject_column='SubjectID'
        ),
        use.UsageOutputNames(
            peds_dists='peds_dist'
        )

    )

    peds_group_dists.assert_output_type("GroupDist[Ordered, Matched] %"
                                        " Properties('peds')")


# PEDS pipeline
def peds_pipeline_sample(use):
    md = use.init_metadata('md', peds_md_factory)
    peds_table = use.init_artifact('peds_table', peds_feature_table_factory)

    peds_heatmap, = use.action(
        use.UsageAction('fmt', 'peds'),
        use.UsageInputs(
            table=peds_table,
            metadata=md,
            peds_metric='sample',
            time_column='time_point',
            reference_column='Donor',
            subject_column='SubjectID'
        ),
        use.UsageOutputNames(
            visualization='heatmap',

        )
    )

    peds_heatmap.assert_output_type('Visualization')


# Heatmap pipeline
def peds_heatmap(use):
    peds_dist = use.init_artifact('peds_dist', peds_dist_factory)

    peds_heatmap, = use.action(
        use.UsageAction('fmt', 'peds_heatmap'),
        use.UsageInputs(
            data=peds_dist,
        ),
        use.UsageOutputNames(
            visualization='heatmap',

        )
    )

    peds_heatmap.assert_output_type('Visualization')
