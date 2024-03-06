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

# Review with PhylogicNDTReviewer

## What is PhylogicNDT^1 used for?
The PhylogicNDT suite of tools models phylogenetic and evolutionary trajectories, clonal dynamics, and subclonal relationships within multiple samples of a single cancer patient to allow for a better understanding of the cancer's progression over time. PhylogicNDT can be used to determine the clonality of different potential driver mutations, track the growth rate of clones over time (when tumor abundance information is known), and even come up with the relative timing of different events across a cohort. All these findings are useful for better understanding the progression of cancer subtypes and their response to treatment.

## Why is review important?
The PhylogicNDT Clustering and BuildTree process can easily be corrupted by artifactual mutations. Sometimes, this manifests itself as mutations appearing far from their supposed cluster. More often, however, artifactual clusters arise, often small, sometimes filled with a high ratio of indels and synonymous mutations, and nearly always breaking the phylogenetic tree. Ideally, many artifact mutations can be filtered out before running Phylogic (through the use of a good PoN, various other filtering steps in the characterization pipeline, and manual variant review); however, some will persist due to a high volume of mutations or hard to call artifacts. Additionally, it is possible to have a true mutation with an aberrant CCF distribution, due to various reasons, which can shift the clustering results erroneously.

The goal of the PhylogicNDT manual review process is not to correctly cluster every mutation (this is in fact what the algorithm should be doing) but to eliminate artifact clusters and investigate odd-looking clustering results. Poor clustering can be used as orthogonal evidence of a mutation artifact, or at least of an erroneous process that must be understood, explained, and corrected. After review and re-running of the method, the goal is to have clean clustering results and a biologically-feasible phylogenetic tree.

## Running PhylogicNDT
As PhylogicNDT is one of the last steps in the analysis process, there are a few upstream tools to be run and reviews to be performed before PhylogicNDT can be run. 
1. Get variant, copy number (CN), and purity/ploidy calls for each sample (i.e. by running the [CGA Characterization Pipeline](https://github.com/broadinstitute/CGA_Production_Analysis_Pipeline)).
2. Review purity/ploidy calls manually or using the PurityReviewer.
3. Run [Pre-Phylogic workflows](https://github.com/getzlab/prePhylogic_TOOL), forcecalling union mutations and re-running ABSOLUTE^2.
4. Review mutations using cga_itools or MutationReviewer and add artifacts to blacklist. In some cases (e.g. for Whole Genome Samples or high tumor mutational burden cancer types), reviewing all the mutations is infeasible. If so, it is okay to skip this step, knowing that more clustering artifacts are likely to originate from artifact mutations.
5. Run PhylogicNDT using data generated above.
	- ./PhylogicNDT.py Cluster -i Patient_ID -sif Patient.sif --artifact_blacklist blacklist.txt --run_with_BuildTree

	- .sif file should contain sample ID, maf filename (.RData file from step 3), seg_fn (can be empty), purity (from step 2), and timepoint for each sample

	- See PhylogicNDT documentation for further details and customization

PhylogicNDT initially outputs an HTML report containing various graphs and plots, some of which are included in the PhylogicNDTReviewer. This report can be viewed for individual participants to check for inconsistencies or one can move straight to using the PhylogicNDTReviewer to review the whole cohort.

## Using the reviewer
Once you have all the information you need to review the clustering results, you can run the PhylogicNDTReviewer following the instructions in the above Install and Basic Usage sections to launch the PhylogicNDTReviewer dashboard. For each participant, you should first look at the CCF plot for obvious discrepancies. In general, all clusters should obey the Pigeonhole principle (where the sum of the siblings' CCF must be less than the parent's CCF). Consequently, a child must never have a CCF greater than its parent. If you see two clusters with lines that cross (thus they cannot be parent-child) but that also add up to more than one (in one or more samples), this is also evidence of an artifact. Remember in all cases however, that each CCF estimate has uncertainty, with an error (95% CI) represented by the shaded area.

Suspicious or obviously artifactual clusters should be annotated using the abbreviations found below, along with any notes that will help you determine the cause and remedy for the artifact. As will be discussed later, you often see evidence in terms of non-viable clusters, but the underlying artifacts are typically the mutations input to PhylogicNDT.

- **F** - **F**lat cluster (and consistently in middle)
- **S** - **S**mall cluster (few mutations compared to other clusters)
- **W** - very **W**ide confidence interval (especially given number of mutations)
- **ID** - high **I**n**D**el/snv ratio
- **SN** - high **S**ynonymous/**N**on-synonymous ratio
- **NC** - high **N**on-**C**oding/coding ratio (only applies to wes)
- **G** - mutations cluster on particular **G**enomic locations
- **C** - probable **C**lonal/truncal mutations
- **BM** - mutations have **B**i**M**odal ccf pmf and are clustered incorrectly
- **T** - breaks phylogenetic **T**ree
- **P** - **P**urity related
- **CN** - **C**opy **N**umber related
- **OS** - **O**ver**S**plitting (smaller cluster shouldn't have been split from other cluster)
- **O** - **O**ther (explain in notes)

In some cases, you may want to note issues with specific mutations as well. Of particular interest are:
- Very low clonal mutations 
- Mutations that begin clonal but have a CCF <<1 in later samples due to a deletion
- Mutations with a CCF significantly >0 in cluster with 0 CCF for some sample 

## PhylogicNDTReviewer Annotations
The following is a list of the default annotations included in the PhylogicNDTReviewer. Note that you can add any additional annotations if needed. 

- Cluster annotation: Cluster artifacts found using the categories defined above; format as specified in the Cluster Annotations panel of the dashboard (e.g., 3-F;4-CL,SI)
- To-do: Notes of next steps (e.g., rerunning PhylogicNDT with a different purity) 
- Urgency: Checklist - one of important, minor, or no changes needed
- Selected tree: Which PhylogicNDT tree is correct, if any (from the tree dropdown)
- Notes: Any additional notes 

## Next steps after review
For most applications, the goal of PhylogicNDT is to generate feasible clusters (and their corresponding posterior CCF distribution for each sample) and assign driver mutations to these clusters. Artifacts in PhylogicNDT arise on the level of the clusters and wreak havoc on the generation of the phylogenetic tree. These artifacts do not occur spontaneously, however, but arise due to artifactual mutations (e.g., sequencing or mapping artifacts, irregularities in the CCF distribution from broken assumptions in ABSOLUTE, etc.). Thus, to correct the artifacts on the cluster level, one must understand the cause of the mutation artifacts and correct them

In general, if a mutation in question is not a suspected driver (i.e. does not have biological significance) and does not give rise to an artifact cluster, it can be left alone. These mutations likely have noisy/artifactual CCF distributions, but their assignment to a true cluster actually helps to “smooth” or correct for this noise. (Indeed this is the purpose of PhylogicNDT, to aggregate the signal from many noisy mutation CCF profiles!) Even if the (non-driver) mutation seems to be mis-clustered, it is usually okay to leave it. There are times, however, when many mutations are mis-assigned and cause a new artifactual cluster to appear (evidenced by the above annotations); this is often the result of not just noise but systematic error. In this case, intervention is necessary to avoid incorrect downstream biological analysis. Typical interventions can be found below and should be generally investigated in order.
  
|Evidence|Investigation|Action|
|--|--|--|
|Truncal clone < 1.0 CCF |Check ABSOLUTE solution |Adjust the purity in necessary samples |
|Artifact cluster |Review mutations in IGV (use MutationReviewer) |Blacklist mutation if evidence of artifact |
|Artifact cluster with evidence of CN abnormalities* |Investigate CN profiles for individual samples |Correct for CN issues if possible; otherwise graylist mutations |
|Oversplitting or wide clusters | |Re-run Phylogic with smaller prior on number of clusters |
|Unexplained artifacts |Ensure upstream tools are working correctly (especially CN pipeline and mutation filters) | |
*Common CN abnormalities include a deletion in a later sample causing a clonal or high-CCF cluster to drop to zero. Or subclonal deletions causing bimodal CCF distributions for mutations and mis-clustering.

If after all this investigation and correction, there are still artifact clusters, you can blacklist all the offending mutations that are non-coding or synonymous and graylist all other mutations. As a true last resort (when you only need a correct tree result), you can rerun BuildTree with that cluster blacklisted, but this will essentially “ignore” any mutations assigned to that cluster in further analyses.

Review can be done on a single participant or more likely, if reviewing a whole cohort, issues can be grouped across many participants and dealt with sequentially. PhylogicNDT review is an iterative process, often requiring a few cycles of review and re-running the pipeline to come to a stable, clean output. Once the clustering results look suitable and the correct tree is selected, the PhylogicNDT data is ready for downstream analysis.

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
1. Leshchiner, I. et al. Comprehensive analysis of tumour initiation, spatial and temporal progression under multiple lines of treatment. Preprint at bioRxiv https://doi.org/10.1101/508127 (2019).
2. Carter, S. L. et al. Absolute quantification of somatic DNA alterations in human cancer. Nat. Biotechnol. 30, 413–21 (2012). doi: 10.1038/nbt.2203.