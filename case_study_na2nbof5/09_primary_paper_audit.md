# Na2NbOF5 primary-paper audit

## Audit status

**PROVISIONAL — full paper not supplied in the workspace.** Publisher metadata and search snippets were accessible; the numerical simulation details below are explicitly from the user's paper notes. They must be checked line-by-line against the provided PDF before this audit can be called complete.

## FACT FROM ACCESSIBLE PAPER RECORD

- Title: *A new sodium-ion conductor Na2NbOF5: Ab initio calculations and electrochemical testing*.
- DOI: 10.1016/j.jpcs.2026.113889; Journal of Physics and Chemistry of Solids 218, 113889 (2026).
- The work follows hierarchical ICSD screening using geometrical/topological analysis, bond-valence site-energy ideas, kinetic Monte Carlo and quantum-chemical calculations.
- Accessible summaries identify two-dimensional Na migration and barriers below 0.5 eV.

## FACT FROM USER-PROVIDED FULL-PAPER NOTES — REQUIRES PDF VERIFICATION

- AIMD length: 20 or 30 ps; timestep: 1 fs; ensemble: NVT; thermostat: Nosé–Hoover; temperature: 300 K.
- DFT: PBE; plane-wave cutoff: 600 eV.
- Disorder: supercells were prepared to represent structural O/F disorder.
- Reported D: approximately 7.1 × 10^-8 cm² s^-1.
- Reported conductivity: approximately 6.6 × 10^-3 S cm^-1.
- Experimental sample: about 12.3% NaF; measured conductivity approximately 1.03 × 10^-6 S cm^-1.
- The experimental number was not presented as intrinsic bulk conductivity because the sample was unsintered, contacts were poor, grain boundaries contributed and NaF was present.

## ITEMS NOT VERIFIED WITHOUT FULL TEXT

- Exact reason for material selection in the final paper versus the prior screening study.
- Exact migration-path labels and numerical barrier for each path.
- Exact cell sizes, O/F occupation construction and number of configurations.
- MSD fitting window, dimensional prefactor, uncertainty/block averaging and derivation of D.
- Exact Nernst–Einstein equation, carrier concentration and charge used for conductivity.
- Whether distinct/self and collective conductivity, Haven ratio or an explicit correlation factor were calculated.
- Authors' stated future work.

## OUR INTERPRETATION

Twenty-to-thirty-picosecond trajectories can be too short to demonstrate diffusive-regime convergence, especially in disordered solids. That motivates a convergence study; it does not invalidate the paper. Multiple disorder realizations may reveal variance not visible in a single representation, but the paper must not be described as ignoring disorder. The experimental discrepancy is not a clean MLMD validation target because the sample limitations confound intrinsic transport.

## Sources
- [Morkhova et al. (2026), A new sodium-ion conductor Na2NbOF5](https://doi.org/10.1016/j.jpcs.2026.113889)
- [Morkhova et al., SSRN preprint record](https://doi.org/10.2139/ssrn.6481875)
- [Hierarchical screening of ICSD ... mixed polyanionic oxohalides](https://doi.org/10.1007/s10008-025-06205-4)
