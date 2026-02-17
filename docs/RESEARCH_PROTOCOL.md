# Research Protocol: Adaptive Learning via Cognitive Load Estimation

## 1. Research Questions

1. **RQ1**: Can cognitive load be reliably estimated from interaction telemetry and privacy-safe webcam features during CS problem-solving?
2. **RQ2**: Which behavioral and visual signals are the strongest predictors of self-reported mental effort?
3. **RQ3**: Does load-aware adaptive instruction improve learning outcomes compared to static instruction?

## 2. Study Design

**Design**: Between-subjects randomized controlled trial using the built-in A/B testing framework.

**Variants**:
| Group | Description | N (target) |
|-------|-------------|------------|
| Control | Static problem ordering, no load-based adaptation | 30 |
| Heuristic | Heuristic-based load estimation with adaptive sequencing | 30 |
| ML Model | ML-based load estimation with adaptive sequencing | 30 |

**Assignment**: Deterministic hash-based assignment (SHA-256 of session ID mod 100) ensures reproducibility and balanced groups.

## 3. Participants

**Eligibility**:
- Undergraduate CS students (CS1/CS2 level)
- Comfortable with basic JavaScript
- 18+ years of age

**Recruitment**:
- In-class announcements with instructor permission
- Voluntary participation with informed consent
- No compensation required (can offer extra credit if approved)

**Target sample**: N = 90 (30 per group), accounting for ~15% attrition.

## 4. Procedure

1. Participant visits the web application and creates an account
2. System displays informed consent form explaining:
   - What data is collected (interaction telemetry, optional webcam features)
   - That no raw video is stored — only numeric aggregates
   - Right to withdraw at any time
3. Participant completes a **pre-test** (5 problems, fixed order, no adaptation)
4. System assigns participant to experimental condition via A/B engine
5. Participant completes the **learning phase** (15–20 adaptive problems, ~30 minutes)
   - Periodic effort self-reports (1–7 Likert scale) prompted every 3 minutes
   - Optional webcam consent toggle available throughout
6. Participant completes a **post-test** (5 problems, fixed order, no adaptation)
7. Participant completes a brief exit survey (SUS usability scale, qualitative feedback)

## 5. Measures

### Independent Variable
- **Condition**: Control vs. Heuristic vs. ML Model

### Dependent Variables
- **Learning gain**: Post-test score minus pre-test score
- **Time-to-correct**: Mean time from problem presentation to correct submission
- **Completion rate**: Proportion of problems solved correctly
- **Hint usage**: Number of hints requested
- **Dropout rate**: Proportion of participants who quit before completing all problems

### Cognitive Load Indicators (Collected, Not Manipulated)
- Self-reported effort (1–7 Likert, Paas & Van Merriënboer, 1994)
- Estimated load score from the model (0–1)
- Individual features: compile errors, pause duration, gaze dispersion, blink rate, head motion

## 6. Data Collection

All data is collected automatically by the system:

| Signal | Source | Frequency | Storage |
|--------|--------|-----------|---------|
| Keystrokes | Telemetry.ts | Batched every 1.5s | events table |
| Code submissions | Problems router | On submit | submissions table |
| Compile/runtime errors | Sequencer | On submit | events table |
| Hint requests | HintPanel | On click | events table |
| Face presence | FaceMeshProcessor | Every 2s | webcam_features table |
| Gaze metrics | FaceMeshProcessor | Every 2s | webcam_features table |
| Blink rate | FaceMeshProcessor | Every 2s | webcam_features table |
| Head motion | FaceMeshProcessor | Every 2s | webcam_features table |
| Effort rating | User input | Every 3 min | effort_labels table |

## 7. Analysis Plan

### Primary Analysis
- **One-way ANOVA** (or Kruskal-Wallis if non-normal) comparing learning gain across 3 conditions
- **Post-hoc pairwise comparisons** with Bonferroni correction
- **Effect size**: Cohen's d for pairwise comparisons, eta-squared for ANOVA

### Secondary Analyses
- **Pearson correlation matrix** between each feature and self-reported effort
- **Multiple regression** predicting effort from telemetry + webcam features
- **Model accuracy**: MAE, RMSE, Pearson r of ML model vs. self-reported effort (cross-validated)
- **Time-series analysis**: Load trajectories over session duration by condition

### Exploratory
- Feature importance rankings from the trained gradient boosting model
- Interaction effects between webcam consent and load estimation accuracy
- Qualitative analysis of exit survey responses

## 8. IRB Considerations

- **Data minimization**: No raw video stored. Webcam processing occurs entirely in-browser.
- **Consent**: Explicit opt-in for both telemetry and webcam features. Participants can disable webcam at any time without losing access to the tutor.
- **Anonymization**: Session IDs are random UUIDs. Email addresses stored for authentication only.
- **Data retention**: All data deleted 12 months after study completion.
- **Risk**: Minimal — standard educational software interaction. No deception.

## 9. Limitations

- Self-reported effort is subjective and may not perfectly capture cognitive load
- Webcam features are noisy and depend on lighting/hardware conditions
- Single-session study may not capture long-term learning effects
- JavaScript-only problem domain limits generalizability

## 10. References

- Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*, 12(2), 257–285.
- Paas, F., & Van Merriënboer, J. J. G. (1994). Variability of worked examples and transfer of geometrical problem-solving skills. *Journal of Educational Psychology*, 86(1), 122–133.
- Kalyuga, S. (2011). Cognitive load theory: How many types of load does it really need? *Educational Psychology Review*, 23(1), 1–19.
- Andrzejak, R., et al. (2021). Detecting cognitive load using physiological sensors. *Computers in Human Behavior*, 123, 106864.
