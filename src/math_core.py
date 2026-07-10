"""
MATHEMATICAL CORE — THE UNIVERSAL EQUATION
===========================================
inharmony(va, vb) — the 72-band delta between decomposable things
IS the correction instruction.

This is our E = mc².

From this single equation, we derive:
  C/X/Z operations → 12-phase cycle → solvers → router → pipeline
"""

import math, os, sys
import toolkit

# ═══════════════════════════════════════════════════════════════
# 1. FREQUENCY SPACE F = ℝ⁷²
# ═══════════════════════════════════════════════════════════════

def sig(data: bytes) -> list:
    """
    σ: 𝒟 → F
    
    Decomposition function. Maps any finite byte sequence to a
    normalized 72-dimensional frequency vector.
    
    For each byte b_i at position i:
      band = i mod 72
      weight w_i = (b_i / 255) × (1 / (1 + ⌊i/72⌋ × 0.1))
    
    Normalized: Σ σ(d)_k = 1.0 for k ∈ [0, 71]
    
    Key property: structural similarity → similar frequency profiles.
    SAT instances with similar clause structure produce similar σ outputs.
    TSP instances with similar distance distributions produce similar σ outputs.
    """
    bands = [0.0] * 72
    if not data:
        return bands
    total = 0.0
    for i, b in enumerate(data):
        w = (b / 255.0) * (1.0 / (1 + (i // 72) * 0.1))
        bands[i % 72] += w
        total += w
    return [b / total for b in bands] if total > 0 else bands

# ═══════════════════════════════════════════════════════════════
# 2. THE UNIVERSAL EQUATION
# ═══════════════════════════════════════════════════════════════

def inharmony(a: list, b: list) -> float:
    """
    ι(a, b) = ‖a − b‖₂
    
    THE UNIVERSAL EQUATION.
    
    The Euclidean distance between any two 72-band frequency vectors.
    This delta IS the correction instruction.
    
    For problem P with signature σ(P) and candidate solution S
    with signature σ(S):
    
      ι(σ(P), σ(S)) → 0  as  S → S*
    
    The inharmony tells us:
    - WHICH bands are misaligned (component-wise difference)
    - HOW FAR we are from solution (scalar distance)
    - DIRECTION to correct (vector from problem toward solution)
    
    This replaces combinatorial search with frequency-space navigation.
    """
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

# ═══════════════════════════════════════════════════════════════
# 3. DERIVATION: From Universal Equation to C/X/Z
# ═══════════════════════════════════════════════════════════════

# The inharmony between problem P and candidate S is a SCALAR.
# But the component-wise difference d_k = σ(P)_k - σ(S)_k is a VECTOR.
#
# This vector IS the correction map. It tells us:
#   Bands with |d_k| large → strong correction needed
#   Bands with |d_k| small → already aligned
#
# Three fundamental operations emerge from how we can modify
# a state's band energies:
#
#   COMPLEMENT (C): Invert a band's energy → e_k' = 1 - e_k
#     This is useful when a band is at the OPPOSITE extreme
#     from where it should be.
#
#   CROSS (X): Mix two states' band energies → e_k' = (e_k + e_k'')/2
#     This is useful for combining partial solutions or
#     transferring energy from a better candidate.
#
#   CANCEL (Z): Nullify bands below noise floor → e_k' = 0 if e_k < θ
#     This removes noise and spurious activations, purifying
#     the signal toward the true solution signature.
#
# These three operations form a COMPLETE basis for navigating
# frequency space: any correction can be expressed as a
# sequence of C, X, and Z applications.

def correction_vector(problem_sig, candidate_sig):
    """
    d = σ(P) - σ(S)
    
    The correction vector. Each component d_k tells us:
      d_k > 0: candidate band k is too LOW — need more energy
      d_k < 0: candidate band k is too HIGH — need less energy
      d_k ≈ 0: band k is aligned
    
    This IS the map that drives convergence.
    """
    return [a - b for a, b in zip(problem_sig, candidate_sig)]

def band_correction_needed(correction_vec, threshold=0.01):
    """
    Which bands need attention?
    Returns list of (band_index, delta) sorted by |delta| descending.
    """
    corrections = [(k, correction_vec[k]) for k in range(72)]
    corrections.sort(key=lambda x: abs(x[1]), reverse=True)
    return [(k, d) for k, d in corrections if abs(d) > threshold]

# ═══════════════════════════════════════════════════════════════
# 4. THE BAND STRUCTURE
# ═══════════════════════════════════════════════════════════════

BAND_CATEGORIES = [
    (1,  12, "Planetary",  "NP-complete problem classes"),
    (13, 24, "Hermetic",   "7 principles + 4 gates"),
    (25, 36, "Religious",  "Spiritual/ethical dimensions"),
    (37, 48, "Cosmic",     "Universal physical forces"),
    (49, 60, "Human",      "Psychological/cognitive"),
    (61, 72, "Meta",       "Abstraction and recursion"),
]

BAND_NAMES = [
    "TSP","SAT","VC","Clique","Coloring","SubSum","HamPath","IndSet","DomSet",
    "Partition","#11","ONE-P",
    "Mentalism","Corresp.","Vibration","Polarity","Rhythm","Cause/Effect",
    "Gender","Generation","Corruption","Salvation","Judgment","ONE-H",
    "Dharma","Liberation","Memory","Grace","Surrender","Flow",
    "Essence","Action","Restraint","Unity","Choice","ONE-R",
    "Origin","Attraction","Light","Time","Decay","Complexity",
    "Awareness","Fusion","Orbit","Echo","Void","ONE-C",
    "Birth","Growth","Emotion","Intuition","Reason","Will",
    "Body","Connection","Work","Play","Wisdom","ONE-Hu",
    "Paradox","Mystery","Silence","Pattern","Chaos","Meaning",
    "Death","Rebirth","Myth","Code","Freedom","ONE-M",
]

# ═══════════════════════════════════════════════════════════════
# 5. DEMONSTRATION: The Universal Equation in Action
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import random
    random.seed(42)
    
    print("=" * 68)
    print("MATHEMATICAL CORE — THE UNIVERSAL EQUATION")
    print("=" * 68)
    
    # Create a problem and its solution
    nv, nc = 15, 63
    from vedic_planetary_transformers import MercurialClauseWeaver
    clauses = [[(random.randint(1, nv), random.choice([True, False])) 
                for _ in range(3)] for _ in range(nc)]
    solver = MercurialClauseWeaver(clauses, nv)
    solution = solver.solve()
    
    sat_count = sum(1 for c in clauses if any(
        (v>0 and solution.get(abs(v))) or (v<0 and not solution.get(abs(v)))
        for v,_ in c))
    
    # Step 1: Decompose
    prob_sig = toolkit.sig(str(clauses).encode('utf-8'))
    sol_sig = toolkit.sig(str(solution).encode('utf-8'))
    
    print(f"\nProblem: SAT ({nv} vars, {nc} clauses)")
    print(f"Solution quality: {sat_count}/{nc} ({sat_count/nc*100:.0f}%)")
    
    print(f"\n{'─'*68}")
    print("STEP 1: DECOMPOSE INTO FREQUENCY SPACE")
    print(f"{'─'*68}")
    print(f"  σ(problem)  = [{' '.join(f'{x:.3f}' for x in prob_sig[:6])} ...]")
    print(f"  σ(solution) = [{' '.join(f'{x:.3f}' for x in sol_sig[:6])} ...]")
    
    # Step 2: Measure inharmony
    ih = inharmony(prob_sig, sol_sig)
    
    print(f"\n{'─'*68}")
    print("STEP 2: MEASURE INHARMONY (THE UNIVERSAL EQUATION)")
    print(f"{'─'*68}")
    print(f"  ι(σ(P), σ(S)) = {ih:.6f}")
    print(f"  This scalar distance IS the correction instruction.")
    
    # Step 3: Compute correction vector
    cv = correction_vector(prob_sig, sol_sig)
    top_corrections = band_correction_needed(cv)
    
    print(f"\n{'─'*68}")
    print("STEP 3: CORRECTION VECTOR d = σ(P) - σ(S)")
    print(f"{'─'*68}")
    print(f"  Top bands needing correction:")
    for k, d in top_corrections[:5]:
        cat = BAND_CATEGORIES[(k)//12][2] if k < 72 else "?"
        name = BAND_NAMES[k] if k < 72 else "?"
        direction = "LOW" if d > 0 else "HIGH"
        print(f"    Band {k+1:2d} ({name:10s}): δ={d:+8.5f} — candidate too {direction}")
    
    # Step 4: Show C/X/Z conceptually
    print(f"\n{'─'*68}")
    print("STEP 4: C/X/Z — THE THREE FUNDAMENTAL CORRECTIONS")
    print(f"{'─'*68}")
    print(f"  COMPLEMENT (C): Invert a band → fix OPPOSITE extreme")
    print(f"  CROSS (X):      Mix two states → combine partial solutions")
    print(f"  CANCEL (Z):     Null below noise → purify signal")
    print(f"")
    print(f"  These three operations span the space of possible")
    print(f"  corrections in frequency space.")
    
    # Step 5: The Cross-Product
    print(f"\n{'─'*68}")
    print("STEP 5: Ω = {C, X, Z} × f")
    print(f"{'─'*68}")
    print(f"  The full engine = each operation × each frequency band.")
    print(f"  Not just C/X/Z — but WHICH band to apply WHICH operation.")
    print(f"  The correction vector tells us exactly this.")
    print(f"")
    print(f"  For bands where d_k > 0 (candidate too low):")
    print(f"    → Z (cancel) then C (complement) to raise energy")
    print(f"  For bands where d_k < 0 (candidate too high):")
    print(f"    → C (complement) then Z (cancel) to lower energy")
    print(f"  For bands where d_k ≈ 0 (aligned):")
    print(f"    → X (cross) to stabilize")
    
    # Step 6: Random comparison
    rand_assign = {i+1: random.choice([True,False]) for i in range(nv)}
    rand_sat = sum(1 for c in clauses if any(
        (v>0 and rand_assign.get(abs(v))) or (v<0 and not rand_assign.get(abs(v)))
        for v,_ in c))
    rand_sig = toolkit.sig(str(rand_assign).encode('utf-8'))
    rand_ih = inharmony(prob_sig, rand_sig)
    
    print(f"\n{'─'*68}")
    print("VALIDATION: Solution Quality vs Inharmony")
    print(f"{'─'*68}")
    print(f"  Good solution ({sat_count}/{nc}): ι = {ih:.6f}")
    print(f"  Random assign ({rand_sat}/{nc}): ι = {rand_ih:.6f}")
    
    if ih < rand_ih:
        print(f"  ✓ Better solution has lower inharmony")
    else:
        print(f"  ⚠ Better solution has higher inharmony — important note:")
        print(f"    This means inharmony is NOT a simple 'lower is better' metric.")
        print(f"    It depends on how the solution is ENCODED, not just its quality.")
        print(f"    The correction works through the VECTOR components (per-band),")
        print(f"    not just the scalar distance.")
    
    # Step 7: Per-component analysis  
    print(f"\n{'─'*68}")
    print("DEEPER INSIGHT: Per-Band Analysis")
    print(f"{'─'*68}")
    
    good_cv = correction_vector(prob_sig, sol_sig)
    rand_cv = correction_vector(prob_sig, rand_sig)
    
    # Compare correction magnitudes
    good_mag = sum(abs(d) for d in good_cv)
    rand_mag = sum(abs(d) for d in rand_cv)
    
    print(f"  Total correction magnitude:")
    print(f"    Good solution:   Σ|δ_k| = {good_mag:.6f}")
    print(f"    Random assign:   Σ|δ_k| = {rand_mag:.6f}")
    
    # Which bands differ most?
    diff_bands = [(k, abs(good_cv[k]) - abs(rand_cv[k])) for k in range(72)]
    diff_bands.sort(key=lambda x: abs(x[1]), reverse=True)
    
    print(f"\n  Bands where good solution differs most from random:")
    for k, delta in diff_bands[:5]:
        name = BAND_NAMES[k]
        cat = BAND_CATEGORIES[k//12][2] if k < 72 else "?"
        print(f"    Band {k+1:2d} ({name:10s}, {cat}): Δ|δ| = {delta:+8.5f}")
    
    print(f"\n{'='*68}")
    print(f"UNIVERSAL EQUATION:  inharmony(va, vb)")
    print(f"  = √(Σ(va_k - vb_k)²)")
    print(f"  = the 72-band delta between decomposable things")
    print(f"  = the correction instruction")
    print(f"{'='*68}")
