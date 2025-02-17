from typing import Callable
from typing import List
from typing import Optional
from typing import Sequence

from optuna._experimental import experimental
from optuna.study import Study
from optuna.trial import FrozenTrial
from optuna.visualization._pareto_front import _get_pareto_front_info
from optuna.visualization._pareto_front import _ParetoFrontInfo
from optuna.visualization.matplotlib._matplotlib_imports import _imports


if _imports.is_successful():
    from optuna.visualization.matplotlib._matplotlib_imports import Axes
    from optuna.visualization.matplotlib._matplotlib_imports import plt


@experimental("2.8.0")
def plot_pareto_front(
    study: Study,
    *,
    target_names: Optional[List[str]] = None,
    include_dominated_trials: bool = True,
    axis_order: Optional[List[int]] = None,
    targets: Optional[Callable[[FrozenTrial], Sequence[float]]] = None,
) -> "Axes":
    """Plot the Pareto front of a study.

    .. seealso::
        Please refer to :func:`optuna.visualization.plot_pareto_front` for an example.

    Example:

        The following code snippet shows how to plot the Pareto front of a study.

        .. plot::

            import optuna


            def objective(trial):
                x = trial.suggest_float("x", 0, 5)
                y = trial.suggest_float("y", 0, 3)

                v0 = 4 * x ** 2 + 4 * y ** 2
                v1 = (x - 5) ** 2 + (y - 5) ** 2
                return v0, v1


            study = optuna.create_study(directions=["minimize", "minimize"])
            study.optimize(objective, n_trials=50)

            optuna.visualization.matplotlib.plot_pareto_front(study)

    Args:
        study:
            A :class:`~optuna.study.Study` object whose trials are plotted for their objective
            values.
        target_names:
            Objective name list used as the axis titles. If :obj:`None` is specified,
            "Objective {objective_index}" is used instead.
        include_dominated_trials:
            A flag to include all dominated trial's objective values.
        axis_order:
            A list of indices indicating the axis order. If :obj:`None` is specified,
            default order is used.

            .. warning::
                Deprecated in v3.0.0. This feature will be removed in the future. The removal of
                this feature is currently scheduled for v5.0.0, but this schedule is subject to
                change. See https://github.com/optuna/optuna/releases/tag/v3.0.0.
        targets:
            A function that returns a tuple of target values to display.
            The argument to this function is :class:`~optuna.trial.FrozenTrial`.

            .. note::
                Added in v3.0.0 as an experimental feature. The interface may change in newer
                versions without prior notice.
                See https://github.com/optuna/optuna/releases/tag/v3.0.0.

    Returns:
        A :class:`matplotlib.axes.Axes` object.

    Raises:
        :exc:`ValueError`:
            If ``targets`` is :obj:`None` when your objective studies have more than 3 objectives.
        :exc:`ValueError`:
            If ``targets`` returns something other than sequence.
        :exc:`ValueError`:
            If the number of target values to display isn't 2 or 3.
        :exc:`ValueError`:
            If ``targets`` is specified for empty studies and ``target_names`` is :obj:`None`.
        :exc:`ValueError`:
            If using both ``targets`` and ``axis_order``.
    """

    _imports.check()

    info = _get_pareto_front_info(
        study, target_names, include_dominated_trials, axis_order, None, targets
    )

    if info.n_targets == 2:
        return _get_pareto_front_2d(info)
    elif info.n_targets == 3:
        return _get_pareto_front_3d(info)
    else:
        raise ValueError(
            "`plot_pareto_front` function only supports 2 or 3 targets."
            " you used {} targets now.".format(info.n_targets)
        )


def _get_pareto_front_2d(info: _ParetoFrontInfo) -> "Axes":
    # Set up the graph style.
    plt.style.use("ggplot")  # Use ggplot style sheet for similar outputs to plotly.
    _, ax = plt.subplots()
    ax.set_title("Pareto-front Plot")
    cmap = plt.get_cmap("tab10")  # Use tab10 colormap for similar outputs to plotly.

    ax.set_xlabel(info.target_names[info.axis_order[0]])
    ax.set_ylabel(info.target_names[info.axis_order[1]])

    if info.non_best_trials_with_values is not None and len(info.non_best_trials_with_values) > 0:
        ax.scatter(
            x=[values[info.axis_order[0]] for _, values in info.non_best_trials_with_values],
            y=[values[info.axis_order[1]] for _, values in info.non_best_trials_with_values],
            color=cmap(0),
            label="Trial",
        )
    if info.best_trials_with_values is not None and len(info.best_trials_with_values) > 0:
        ax.scatter(
            x=[values[info.axis_order[0]] for _, values in info.best_trials_with_values],
            y=[values[info.axis_order[1]] for _, values in info.best_trials_with_values],
            color=cmap(3),
            label="Best Trial",
        )

    if info.non_best_trials_with_values is not None and ax.has_data():
        ax.legend()

    return ax


def _get_pareto_front_3d(info: _ParetoFrontInfo) -> "Axes":
    # Set up the graph style.
    plt.style.use("ggplot")  # Use ggplot style sheet for similar outputs to plotly.
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.set_title("Pareto-front Plot")
    cmap = plt.get_cmap("tab10")  # Use tab10 colormap for similar outputs to plotly.

    ax.set_xlabel(info.target_names[info.axis_order[0]])
    ax.set_ylabel(info.target_names[info.axis_order[1]])
    ax.set_zlabel(info.target_names[info.axis_order[2]])

    if info.non_best_trials_with_values is not None and len(info.non_best_trials_with_values) > 0:
        ax.scatter(
            xs=[values[info.axis_order[0]] for _, values in info.non_best_trials_with_values],
            ys=[values[info.axis_order[1]] for _, values in info.non_best_trials_with_values],
            zs=[values[info.axis_order[2]] for _, values in info.non_best_trials_with_values],
            color=cmap(0),
            label="Trial",
        )

    if info.best_trials_with_values is not None and len(info.best_trials_with_values):
        ax.scatter(
            xs=[values[info.axis_order[0]] for _, values in info.best_trials_with_values],
            ys=[values[info.axis_order[1]] for _, values in info.best_trials_with_values],
            zs=[values[info.axis_order[2]] for _, values in info.best_trials_with_values],
            color=cmap(3),
            label="Best Trial",
        )

    if info.non_best_trials_with_values is not None and ax.has_data():
        ax.legend()

    return ax
