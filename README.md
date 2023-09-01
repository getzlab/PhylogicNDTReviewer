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
