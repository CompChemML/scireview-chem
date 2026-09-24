# Scientific gap analysis

## Surviving gap

**Whether Na2NbOF5 transport predictions converge with trajectory length and cell size across multiple O/F disorder realizations, and whether collective charge transport differs from tracer/Nernst–Einstein transport across temperature.**

This combines the supported gaps without claiming that prior AIMD ignored disorder or that MLMD must reconcile calculation and experiment.

## Candidate assessments

### Gap A — Trajectory-length convergence of Na diffusion

**Status:** SUPPORTED  
**Evidence:** Primary study used 20/30 ps according to supplied notes; no exact-material convergence study located  
**Closest competing paper:** R06/R07  
**Why distinct:** Na2NbOF5 convergence remains material-specific  
**Remaining uncertainty:** Primary PDF needed to confirm all runs and block-analysis details

### Gap B — Finite-size effects and larger cells

**Status:** PARTIALLY SUPPORTED  
**Evidence:** No cell-size convergence study located; prior work did use disorder-representing supercells  
**Closest competing paper:** R07/R08  
**Why distinct:** Question is convergence, not whether disorder was ignored  
**Remaining uncertainty:** Exact original cell sizes and replicas require full text

### Gap C — Sensitivity to O/F disorder realizations

**Status:** PARTIALLY SUPPORTED  
**Evidence:** Disorder was represented, but systematic ensemble sampling was not located  
**Closest competing paper:** R07  
**Why distinct:** Multiple Na2NbOF5 O/F configurations are system-specific  
**Remaining uncertainty:** Full paper may contain more configuration sampling than accessible metadata shows

### Gap D — Collective/correlated hopping and Nernst-Einstein limits

**Status:** SUPPORTED  
**Evidence:** No exact-material Haven/collective study located; contextual Na MLIP study demonstrates relevance  
**Closest competing paper:** R06  
**Why distinct:** Applies correlation analysis to Na2NbOF5 rather than importing conclusions  
**Remaining uncertainty:** Explicit treatment in primary paper must be confirmed from supplied PDF

### Gap E — Temperature-dependent diffusion and activation energy

**Status:** SUPPORTED  
**Evidence:** Accessible exact-material AIMD evidence centers on 300 K; no long-trajectory temperature series located  
**Closest competing paper:** R06/R07  
**Why distinct:** Long MLMD can estimate a material-specific Arrhenius regime  
**Remaining uncertainty:** Confirm whether supplementary information contains additional temperatures

### Gap F — Defect/vacancy effects

**Status:** NOT SUPPORTED  
**Evidence:** Prior screening addressed vacancy energetics and defect chemistry is not yet scoped well enough for a primary novelty claim  
**Closest competing paper:** R03/R04  
**Why distinct:** Could become a secondary sensitivity study only after defect states are justified  
**Remaining uncertainty:** Relevant intrinsic/extrinsic defect concentrations are unknown

## Claims to avoid

- “Previous AIMD ignored disorder.” It did not.
- “MLMD will explain the calculation–experiment discrepancy.” The reported experimental sample is not an intrinsic bulk benchmark.
- “The work is novel because Na2NbOF5 is new.” Prior screening and AIMD already exist.
- “No one is working on this.” Public search cannot resolve unpublished work.

## Sources
- [Morkhova et al. (2026), A new sodium-ion conductor Na2NbOF5](https://doi.org/10.1016/j.jpcs.2026.113889)
- [Hierarchical screening of ICSD ... mixed polyanionic oxohalides](https://doi.org/10.1007/s10008-025-06205-4)
- [He, Chen & Lai, Na diffusion with MLIPs](https://doi.org/10.2139/ssrn.4431516)
- [Miyagawa et al., MLMD ion migration](https://arxiv.org/abs/2401.11244)
- [Aghoghovbia et al., Probing MLIPs on ion transport](https://doi.org/10.1002/aidi.70143)
- [ML-assisted discovery of sodium superionic conductors](https://doi.org/10.1039/D5MH01176K)
