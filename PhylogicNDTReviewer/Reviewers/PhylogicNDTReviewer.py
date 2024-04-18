"""
Standard reviewer for PhylogicNDT (Leshchiner 2018) results. Displays a mutation table that can be filtered and sorted, PhylogicNDT CCF trajectories and candidate clonal trees, general metrics per PhylogicNDT clusters, and copy number plots with currently selected mutations displayed.
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from dash.dependencies import Output
from dash import html, dash_table, dcc
import re

from AnnoMate.Data import DataAnnotation
from AnnoMate.ReviewDataApp import ReviewDataApp, AppComponent
from AnnoMate.ReviewerTemplate import ReviewerTemplate
from AnnoMate.DataTypes.PatientSampleData import PatientSampleData
from AnnoMate.AnnotationDisplayComponent import NumberAnnotationDisplay, TextAreaAnnotationDisplay, RadioitemAnnotationDisplay, TextAnnotationDisplay

from AnnoMate.AppComponents.PhylogicNDTComponents import gen_ccf_pmf_component, gen_phylogicNDT_app_component, gen_cluster_metrics_component
from AnnoMate.AppComponents.MutationTableComponent import gen_mutation_table_app_component
from AnnoMate.AppComponents.CNVPlotComponent import gen_cnv_plot_app_component


class PhylogicNDTReviewer(ReviewerTemplate):
    """Class to facilitate reviewing PhylogicNDT results in a consistent and efficient manner.

    Notes
    -----
    - Display CCF plot (pull code from Patient Reviewer)
    - Display mutations (pull code from Patient Reviewer)
    - Display trees (pull code from Patient Reviewer?)
        - Work on weighted tree viz
    - Display CN plots (pull code from old PhylogicNDT review code, with updated library use)**
         - Display mutations on CN plots
         - Allow filtering using mutations table
    - Metrics for coding vs. non_coding, silent vs. non_syn (coding), indels vs. SNPs summarized for each cluster**
        - Could output some statistics as well -> highlight sig differences from null
    - Integrated (link to run bash script) variant reviewer
    - View CCF pmf distributions for individual mutations**

    - Annotate:
        - Variants (add to variant_review file)
        - Cluster annotations (add to cluster blocklist? Only for final analysis though - better to block mutations)
            - Can also just annotate with notes
        - Notes generally
        - Select correct tree (save tree child-parent relationship, but how to associate clusters if you re-run?)
    """

    def gen_data(self,
                 description: str,
                 participant_df: pd.DataFrame,
                 sample_df: pd.DataFrame,
                 annot_df: pd.DataFrame = None,
                 annot_col_config_dict: Dict = None,
                 history_df: pd.DataFrame = None,
                 index: List = None,
                 ) -> PatientSampleData:
        """

        Parameters
        ----------
        description
            Describe the review session. This is useful if you copy the history of this object to a new review data
            object
        participant_df
            dataframe containing participant data. this will be the primary dataframe
        sample_df
            dataframe containing sample data
        annot_df
            Dataframe with previous/prefilled annotations
        annot_col_config_dict
            Dictionary specifying active annotation columns and validation configurations
        history_df
            Dataframe with previous/prefilled history

        Returns
        -------
        PatientSampleData
            A `Data` object for PhylogicNDT review and annotation history

        """
        if index is None:
            index = participant_df.index.tolist()

        # todo get number of tree options for tree validation; don't think this is possible now

        # create review data object
        rd = PatientSampleData(index=index, description=description,
                               participant_df=participant_df, sample_df=sample_df,
                               annot_df=annot_df, annot_col_config_dict=annot_col_config_dict, history_df=history_df)
        return rd

    def set_default_review_data_annotations(self):
        self.add_review_data_annotation('cluster_annotation', DataAnnotation('string', validate_input=cluster_ann_validation))
        self.add_review_data_annotation('To-Do', DataAnnotation('string'))
        self.add_review_data_annotation('Urgency', DataAnnotation('string',
                                                                  options=['Important (broken tree)', 'Minor',
                                                                           'No changes needed']))
        self.add_review_data_annotation('selected_tree_idx', DataAnnotation('int'))  # options=range(1, tree_num+1) how to access this?
        self.add_review_data_annotation('selected_tree', DataAnnotation('string'))
        self.add_review_data_annotation('notes', DataAnnotation('string'))
        # 'variant_blocklist': ReviewDataAnnotation(),  # needs to go in separate reviewer

    def set_default_review_data_annotations_app_display(self):
        self.add_annotation_display_component('cluster_annotation', TextAnnotationDisplay())
        self.add_annotation_display_component('To-Do', TextAnnotationDisplay())
        self.add_annotation_display_component('Urgency', RadioitemAnnotationDisplay())
        self.add_annotation_display_component('selected_tree_idx', NumberAnnotationDisplay())
        self.add_annotation_display_component('selected_tree', TextAnnotationDisplay())
        self.add_annotation_display_component('notes', TextAreaAnnotationDisplay())

    def gen_review_app(
        self, 
        custom_colors=None, 
        drivers_fn=None,
        default_maf_sample_cols=[
            't_ref_count',
            't_alt_count',
            'n_ref_count',
            'n_alt_count',
        ],
        maf_hugo_col='Hugo_Symbol',
        maf_chromosome_col='Chromosome',
        maf_start_pos_col='Start_position',
        maf_end_pos_col='End_position',
        maf_protein_change_col='Protein_change',
        maf_variant_class_col='Variant_Classification',
        maf_cluster_col='Cluster_Assignment',
        maf_sample_id_col='Sample_ID',
        maf_participant_id_col='Patient_ID',
        maf_variant_type_col='Variant_Type'
    ) -> ReviewDataApp:  #todo change empty list to None
        """Generates a ReviewDataApp object

        Parameters
        ----------
        custom_colors
            List of custom colors (for what?)
        drivers_fn
            Path and filename for driver genes; should be single column with no header
        default_maf_sample_cols
            List of default columns to be displayed on the sample side of the mutation table 
        maf_hugo_col
            Name of the hugo symbol column in the maf file 
        maf_chromosome_col
            Name of the chromosome column in the maf file 
        maf_start_pos_col
            Name of the start position column in the maf file 
        maf_end_pos_col
            Name of the end position column in the maf file 
        maf_protein_change_col
            Name of the protein change column in the maf file 
        maf_variant_class_col
            Name of the variant classification column in the maf file 
        maf_cluster_col
            Name of the cluster assignment column in the maf file 
        maf_sample_id_col
            Name of the sample id column in the maf file 
        maf_participant_id_col
            Name of the participant id column in the maf file 
        maf_variant_type_col
            Name of the variant type column in the maf file 

        Returns
        -------
        ReviewDataApp
        """
        app = ReviewDataApp()

        app.add_component(AppComponent('Cluster Annotations',
                                       html.Div([html.P('To annotate cluster artifacts, use commas to separate '
                                                        'annotations and semicolons to separate the clusters '
                                                        '(eg: 3-F,S;4-CL,SI;5-O)'),
                                                 html.P('Use only the following annotations:'),
                                                 dcc.Markdown(nice_print_ann(ANN_DICT))])))
        app.add_component(
            gen_phylogicNDT_app_component(), 
            drivers_fn=drivers_fn,
            maf_participant_id_col=maf_participant_id_col,
            maf_hugo_col=maf_hugo_col,
            maf_chromosome_col=maf_chromosome_col,
            maf_start_pos_col=maf_start_pos_col,
            maf_cluster_col=maf_cluster_col
        )
        app.add_component(
            gen_cluster_metrics_component(),
            maf_variant_type_col=maf_variant_type_col,
            maf_variant_class_col=maf_variant_class_col,
            maf_cluster_col=maf_cluster_col
        )
        app.add_component(
            gen_mutation_table_app_component(), 
            custom_colors=custom_colors,
            default_maf_sample_cols=default_maf_sample_cols, 
            maf_hugo_col=maf_hugo_col, 
            maf_chromosome_col=maf_chromosome_col, 
            maf_start_pos_col=maf_start_pos_col, 
            maf_end_pos_col=maf_end_pos_col, 
            maf_protein_change_col=maf_protein_change_col, 
            maf_variant_class_col=maf_variant_class_col, 
            maf_cluster_col=maf_cluster_col, 
            maf_sample_id_col=maf_sample_id_col
        )

        def get_sample_data_table(data: PatientSampleData, idx):
            """Clinical and sample data callback function"""
            sample_df = data.sample_df[data.sample_df['participant_id'] == idx].sort_values('collection_date_dfd')
            columns = ['sample_id', 'wxs_purity', 'wxs_ploidy', 'collection_date_dfd']

            return [
                sample_df.reset_index()[columns].to_dict('records'),
                [{"name": i, "id": i} for i in columns]
            ]
        app.add_component(AppComponent('Sample Data',
                                       dash_table.DataTable(id='sample-datatable'),
                                       callback_output=[Output('sample-datatable', 'data'),
                                                        Output('sample-datatable', 'columns')],
                                       new_data_callback=get_sample_data_table))

        app.add_component(
            gen_cnv_plot_app_component(),
            maf_sample_id_col=maf_sample_id_col,
            maf_start_pos_col=maf_start_pos_col,
            maf_chromosome_col=maf_chromosome_col, 
            maf_cluster_col=maf_cluster_col,
            maf_hugo_col=maf_hugo_col,
            maf_variant_class_col=maf_variant_class_col,
            maf_protein_change_col=maf_protein_change_col
        )
        app.add_component(
            gen_ccf_pmf_component(),
            maf_sample_id_col=maf_sample_id_col,
            maf_cluster_col=maf_cluster_col,
            maf_hugo_col=maf_hugo_col,
            maf_chromosome_col=maf_chromosome_col,
            maf_start_pos_col=maf_start_pos_col,
        )

        return app

    def set_default_autofill(self):
        pass


ANN_DICT = {'F': 'Flat cluster (and consistently in middle)',
            'S': 'Small cluster (few mutations compared to other clusters)',
            'W': 'very Wide confidence interval (especially given number of mutations)',
            'ID': 'high InDel/snv ratio',
            'SN': 'high Synonymous/Non-synonymous ratio',
            'NC': 'high Non-Coding/coding ratio (only applies to wes)',
            'G': 'mutations cluster on particular Genomic locations',
            'C': 'probable Clonal/truncal mutations',
            'BM': 'mutations have BiModal ccf pmf and are clustered incorrectly',
            'T': 'breaks phylogenetic Tree',
            'P': 'Purity related',
            'CN': 'Copy Number related',
            'OS': "OverSplitting (smaller cluster shouldn't have been split from other cluster)",
            'O': 'Other (explain in notes)'}


def nice_print_ann(ann_dict):
    each_line = [' - '.join([k, v]) for k, v in ann_dict.items()]
    full_text = '- ' + '\n- '.join(each_line)
    return re.sub(r'[A-Z]+', r'**\g<0>**', full_text)


def cluster_ann_validation(x):
    try:
        cluster_dict = {val.strip().split('-')[0]: [i.strip() for i in val.strip().split('-')[1].split(',')] for val in x.split(';')}
    except IndexError:
        print('Annotation not formatted correctly.')
        return False
    else:
        all_annotations = [item for sublist in cluster_dict.values() for item in sublist]
        return np.array([ann in ANN_DICT.keys() for ann in all_annotations]).all()

