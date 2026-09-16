"""Pareto-based selection operators used by the formal AEEA implementation.

All objectives are minimized.  Selection never sums objectives and therefore
does not mix cost components with different numerical ranges.
"""

from __future__ import annotations

from math import isfinite, isinf
from typing import Sequence


def pareto_rank_and_crowding(multi_obj_values: Sequence[Sequence[float]]):
    """Return NSGA-II nondomination ranks and normalized crowding distances."""
    try:
        values = [tuple(float(value) for value in row) for row in multi_obj_values]
    except (TypeError, ValueError) as exc:
        raise ValueError("multi_obj_values must be a numeric two-dimensional array") from exc
    if not values or not values[0]:
        raise ValueError("multi_obj_values must be a non-empty two-dimensional array")
    if any(len(row) != len(values[0]) for row in values):
        raise ValueError("all objective vectors must have the same length")
    if not all(isfinite(value) for row in values for value in row):
        raise ValueError("multi_obj_values must contain only finite values")

    size = len(values)
    dominates_set = [[] for _ in range(size)]
    dominated_count = [0] * size
    ranks = [-1] * size

    for p in range(size):
        for q in range(p + 1, size):
            p_dominates_q = all(
                p_value <= q_value
                for p_value, q_value in zip(values[p], values[q])
            ) and any(
                p_value < q_value
                for p_value, q_value in zip(values[p], values[q])
            )
            q_dominates_p = all(
                q_value <= p_value
                for p_value, q_value in zip(values[p], values[q])
            ) and any(
                q_value < p_value
                for p_value, q_value in zip(values[p], values[q])
            )
            if p_dominates_q:
                dominates_set[p].append(q)
                dominated_count[q] += 1
            elif q_dominates_p:
                dominates_set[q].append(p)
                dominated_count[p] += 1

    fronts = [[index for index, count in enumerate(dominated_count) if count == 0]]
    rank = 0
    while rank < len(fronts) and fronts[rank]:
        next_front = []
        for p in fronts[rank]:
            ranks[p] = rank
            for q in dominates_set[p]:
                dominated_count[q] -= 1
                if dominated_count[q] == 0:
                    next_front.append(q)
        if next_front:
            fronts.append(next_front)
        rank += 1

    crowding = [0.0] * size
    for front in fronts:
        if len(front) <= 2:
            for index in front:
                crowding[index] = float("inf")
            continue

        for objective in range(len(values[0])):
            ordered = sorted(front, key=lambda index: (values[index][objective], index))
            crowding[ordered[0]] = float("inf")
            crowding[ordered[-1]] = float("inf")
            span = values[ordered[-1]][objective] - values[ordered[0]][objective]
            if span == 0:
                continue
            for position in range(1, len(ordered) - 1):
                index = ordered[position]
                if not isinf(crowding[index]):
                    crowding[index] += (
                        values[ordered[position + 1]][objective]
                        - values[ordered[position - 1]][objective]
                    ) / span

    return ranks, crowding


def pareto_select_by_count(population, multi_obj_values, count):
    """Select by lower nondomination rank and then larger crowding distance."""
    if len(population) != len(multi_obj_values):
        raise ValueError("population and multi_obj_values must have the same length")
    if not population or count <= 0:
        return [], [], []

    ranks, crowding = pareto_rank_and_crowding(multi_obj_values)
    ordered_indices = sorted(
        range(len(population)),
        key=lambda index: (ranks[index], -crowding[index], index),
    )
    selected_indices = ordered_indices[: min(count, len(population))]
    selected_population = [population[index] for index in selected_indices]
    selected_values = [list(multi_obj_values[index]) for index in selected_indices]
    return selected_population, selected_indices, selected_values


def pareto_select_elites(population, multi_obj_values, elite_ratio):
    """Select the fixed-size elite set used for cross-generation memory."""
    elite_count = min(len(population), max(2, round(len(population) * elite_ratio)))
    return pareto_select_by_count(population, multi_obj_values, elite_count)


def pareto_select_prompt_context(elite_individuals, elite_values):
    """Select half of the current elites as the LLM prompt context."""
    context_count = max(1, len(elite_individuals) // 2)
    selected, _, selected_values = pareto_select_by_count(
        elite_individuals, elite_values, context_count
    )
    return selected, selected_values


def cap_agent_candidates(candidates, objective_values, target_count):
    """Pareto-trim excess valid Agent candidates to the requested count."""
    if len(candidates) != len(objective_values):
        raise ValueError("candidates and objective_values must have the same length")
    if len(candidates) <= target_count:
        return list(candidates), list(objective_values)
    selected, _, selected_values = pareto_select_by_count(
        candidates, objective_values, target_count
    )
    return selected, selected_values
