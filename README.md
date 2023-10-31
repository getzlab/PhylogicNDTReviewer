# PhylogicNDTReviewer

Suite of reviewers for reviewing [PhylogicNDT](https://github.com/broadinstitute/PhylogicNDT) results.

Demo: coming soon!

# Install

## Activate or Set up Conda Environment

This is **_highly_** recommended to manage different dependencies required by different reviewers.

See [Set up Conda Environment](https://github.com/getzlab/JupyterReviewer/blob/master/README.md#set-up-conda-environment) for details on how to download conda and configure an environment.
    
## Install PhylogicNDTReviewer

Clone 
```
git clone git@github.com:getzlab/PhylogicNDTReviewer.git

# or in an existing repo
git submodule add git@github.com:getzlab/PhylogicNDTReviewer.git
```

Install
```
cd PhylogicNDTReviewer
conda activate <your_env>
pip install -e .
```

# Basic usage

See `example_notebooks` for basic examples and demos of the PhylogicNDT reviewers.

See `PhylogicNDTReviewer/Reviewers` to see available pre-built reviewer options.

See `PhylogicNDTReviewer/DataTypes` to see pre-built data configurations for PhylogicNDT review.

## Inputs

- *participant_df* - tsv file with participant data/filepaths, with columns (at minimum): 
  - participant_id
  - maf_fn (PhylogicNDT mut_ccfs files for each participant)
  - cluster_ccfs_fn (PhylogicNDT cluster_ccfs files for each participant)
  - build_tree_posterior_fn (PhylogicNDT build_tree_posterior files for each participant)

- *sample_df* - tsv file with sample data and filepaths, with columns (at minimum): 
  - sample_id
  - cnv_seg_fn (copy number seg files for each participant)
  - participant_id
  - collection_date_dfd (collection date, typically counted in days since diagnosis)
  - wxs_ploidy (sample ploidies)
  - wxs_purity (sample purities)

## Output Annotations
- cluster_annotation: annotating artifactual clusters with specific labels
- To-Do: text field to track specific to-dos
- Urgency: how much review/modification is still needed
- selected_tree_idx: index (typically 1-indexed) of the chosen tree, if any
- selected_tree: edge relationships of tree; currently needs to be input manually but can be made automatic
- notes: general text field for other notes

# Review with PhylogicNDTReviewer

## Why is this type of review important 
The PhylogicNDT suite of tools (Leshchiner et. al) models phylogenetic and evolutionary trajectories, clonal dynamics, and subclonal relationships within multiple samples of a single cancer patient to allow for a better understanding of the cancer's progression over time. This is a tool that is run further downstream in the analysis process, meaning that if errors were made or overlooked in upstream tools, they will propagate to PhylogicNDT, causing results to be inaccurate. Because of this, PhylogicNDT Clustering and BuildTree results must be closely reviewed, checking for any such errors. It is important that PhylogicNDT results are clear and correct in order to make meaningful analyses of the data. 

## How is this review conducted 

### Pre-reviewer use: Pipelines and tools run before PhylogicNDT results can be reviewed
As PhylogicNDT is one of the last steps in the analysis process, there are a few upstream tools to be run and reviews to be made before PhylogicNDT can be run and reviewed. 
1. Run the WES Characterization Pipeline: This pipeline runs many different tools, one of which is ABSOLUTE. ABSOLUTE suggests purities and ploidies for each sample, which are necessary for running PhylogicNDT. 
2. Review purities: It is important that the purities are reviewed before running PhylogicNDT. This can be done manually or by using the PurityReviewer, another pre-made AnnoMate Reviewer. 
3. Run Pre-Phylogic workflows: These workflows include make_forcecall_intervalls, forcecall_snps_indels, and abs_seg_forcecall.
4. Mark non-coding mutations in a blacklist.
5. Review remaining mutations: These can be reviewed using cga_itools or MutationReviewer to examine the mutations in IGV and added to the blacklist if necessary. 
6. Run PhylogicNDT using the blacklist created in previous steps. 

PhylogicNDT initially outputs an HTML report containing various graphs and plots, some of which are included in the PhylogicNDTReviewer. This report should always be looked at before the PhylogicNDTReviewer is used. Since the main goal of this reviewer is to determine where possible errors in the PhylogicNDT results may be coming from, it will likely only be used when you’ve looked at the HTML report and seen something that doesn’t look right. 

### Using the reviewer: How to use the reviewer, what to look for, tips and tricks
Once you have all the information you need to review the clustering results, you can run the PhylogicNDTReviewer following the instructions in the above Install and Basic Usage sections to launch the PhylogicNDTReviewer dashboard. Since at this stage you have already looked at the HTML report, you likely have an idea of what might be wrong with the results / where to first look for issues. If you think inappropriate purity may have been called, you can look at the copy number plot and purity. If you think the issue may have to do with mutations, you can look at the mutation table. In addition, it could also be helpful to pull up the MutationReviewer, another pre-made AnnoMate Reviewer, in parallel to look at the mutations in IGV. The Mutation Types by Cluster and CCF pmf plots are also helpful in seeing any immediate red flags if there are an overwhelming number of a certain mutation type or an odd distribution of mutations in a specific cluster. Any findings here can be marked in the annotations section. 

## Next steps after review: Now that review has been conducted, what is done with the information found 
Typically if there are issues found and annotated for a given participant, they will be addressed immediately after the review of that patient (rather than annotating all patients and then going back). The next steps after each participant depend on what issues were found. If the copy number profile looks really wrong, next steps would include backtracking in the pipeline and seeing if there were any mistakes in purity or other ABSOLUTE results / annotations. You also may want to look further into the data itself for any possible artifacts. Once you think you have solved the issue, you will then run PhylogicNDT again and re-review, iterating until the PhylogicNDT report looks accurate. Once this is the case, you can move onto the next participant until all participants have been reviewed. At this point, your clean PhylogicNDT results can be used as a tool to find trends that might explain something about the development of a certain type of cancer or its resistance to treatment.  


# Custom and advanced usage

See `PhylogicNDTReviewer/AppComponents` for pre-built components and their customizable parameters, and additional utility functions. 

For customizing annotations, adding new components, and other features, see [Intro_to_Reviewers.ipynb](https://github.com/getzlab/JupyterReviewer/blob/master/example_notebooks/Intro_to_Reviewers.ipynb).

For creating your own prebuilt reviewer, see [Developer_Jupyter_Reviewer_Tutorial.ipynb](https://github.com/getzlab/JupyterReviewer/blob/master/example_notebooks/Developer_Jupyter_Reviewer_Tutorial.ipynb).

# Pro Tips
The clustering in PhylogicNDT can be very fickle, especially in WES samples, and is affected a lot by noisy CN segmentation and artifact mutations. In turn, any artifact clusters will invalidate the build tree attempts, giving solutions that are not biologically feasible. 
- Don't worry too much about choosing the correct tree until the clusters look plausible. 
- Learn to recognize when an artifact cluster arises due to artifact mutations (typically low CCF or low coverage) vs. when mutations are real but have skewed CCF distributions (clonal mutations with wide CCF dist, noisy CN segment, subclonal CN changes, etc.).
- Clustering can be re-run with artifact mutations "blacklisted" and troublesome mutations "graylisted" (treated as an InDel during clustering and assigned after)
- If you really need a clean tree, you can run BuildTree with certain clusters blacklisted, but this is not recommended.

# Future Development
- It would be advantageous to connect this reviewer with the MutationReviewer (passing a list of mutations directly to review with IGV)
- Add buttons to automatically re-run PhylogicNDT with annotated mutations/clusters removed

# References
Phylogic: Ignaty Leshchiner, Dimitri Livitz, Justin F. Gainor, Daniel Rosebrock, Oliver Spiro, Aina Martinez, Edmund Mroz, Jessica J. Lin, Chip Stewart, Jaegil Kim, Liudmila Elagina, Mari Mino-Kenudson, Marguerite Rooney, Sai-Hong Ignatius Ou, Catherine J. Wu, James W. Rocco, Jeffrey A. Engelman, Alice T. Shaw, Gad Getz
bioRxiv 508127; doi: https://doi.org/10.1101/508127