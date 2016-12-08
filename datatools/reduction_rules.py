import numpy as np


def reduction1(C):
    # returns: F - features that must be in the solution
    #          P - pairs which can be removed from the sub-problem
    # if this pair is covered by only one feature - mark it for removal
    candidate_pairs = (C.sum(axis=1) == 1)
    # the features to keep will be any that differ for the candidate pairs
    F = np.flatnonzero(C[candidate_pairs].sum(axis=0))
    # get all pairs covered by these features
    P = np.flatnonzero(C[:, F].sum(axis=1))
    return F, P


def reduction2(C):
    # returns: F - features that must be in the solution
    #          P - pairs which can be removed from the sub-problem
    # First find how many pairs each feature covers
    num_covered = C.sum(axis=0)
    # If we iterate in order we can save some time doing double comparisons
    order = np.argsort(num_covered)
    redundant_features = set()
    for i, f1 in enumerate(order[:-1]):
        for f2 in order[i+1:]:
            # if examples covered by f1 are a subset of those covered by f2
            # then f1 is a redundant feature since f2 covers all its pairs
            if np.array_equal(C[:, f1], C[:, f1] * C[:, f2]):
                redundant_features.add(f1)
                break
    return sorted(list(redundant_features))


def reduction3(C):
    # returns: F - features that must be in the solution
    #          P - pairs which can be removed from the sub-problem
    # First find how features each pair is covered by
    num_covered = C.sum(axis=1)
    # If we iterate in order we can save some time doing double comparisons
    order = np.argsort(num_covered)[::-1]
    redundant_pairs = set()
    for i, p1 in enumerate(order[:-1]):
        for p2 in order[i+1:]:
            # if features covering p2 are a subset of those covering p1 then
            # p1 is redundant since any feature that covers p2 will cover p1
            if np.array_equal(C[p2, :], C[p1, :] * C[p2, :]):
                redundant_pairs.add(p1)
                break
    return sorted(list(redundant_pairs))


def apply(C, apply1=True, apply2=True, apply3=True):
    finished = False
    Np, Nf = C.shape
    Pmask = np.full(Np, True, dtype=bool)
    Fmask = np.full(Nf, True, dtype=bool)
    C_ = C
    F = []
    while(not finished):
        finished = True
        if apply1:
            # print('checking 1')
            f, p = reduction1(C_)
            if len(f):
                # print('applying 1')
                finished = False
                # get actual indices
                f = np.flatnonzero(Fmask)[f]
                p = np.flatnonzero(Pmask)[p]
                # update masks
                Pmask[p] = False
                Fmask[f] = False
                # record required features
                F.extend(f)
                C_ = C[Pmask, :][:, Fmask]
        if apply2:
            # print('checking 2')
            f = reduction2(C_)
            if len(f):
                # print('applying 2')
                finished = False
                # get actual indices
                f = np.flatnonzero(Fmask)[f]
                Fmask[f] = False
                C_ = C[Pmask, :][:, Fmask]
        if apply3:
            # print('checking 3')
            p = reduction3(C_)
            if len(p):
                # print('applying 3')
                finished = False
                # get actual indices
                p = np.flatnonzero(Pmask)[p]
                Pmask[p] = False
                C_ = C[Pmask, :][:, Fmask]
        print({i for i, p in enumerate(Pmask) if p})
    return F, Fmask, Pmask
