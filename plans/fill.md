# Filled plots

Design decisions recorded November 14, 2026. Implementation and validation notes
appear below.

## User API

Use one `fill` option on the plotting functions and `plot_gen`.

| Value | Meaning |
| --- | --- |
| `None` | Disable fill, the default |
| A datetime scalar | Fill to this timestamp on a datetime y axis |
| A finite real number | Fill between the curve and this y value |
| `"bottom"` | Fill between the curve and the current viewport bottom |
| A list of these values | Configure each series independently |

```python
plot(ys, fill=0)
plot(ys, fill="bottom")
plot([a, b], fill=[0, None])
plot(ys, fill=10, lines=True, color="blue")
```

A scalar broadcasts to every series. A list must match the series count exactly.
Accept NumPy real scalars. Reject Python and NumPy booleans, nonfinite baselines,
complex numbers, nested lists, and unknown strings with useful errors. Test for
`None` explicitly because zero is a valid baseline.

Fill uses the series color and character set. `lines` continues to control the
explicit connecting stroke. Fill itself connects adjacent valid samples even
when `lines=False`. Existing point markers are still drawn. A single isolated
point has no filled area.

Sparklines always fill to the bottom of the view. Both helpers expose keyword-only
`color`, `y_min`, and `y_max`; fill is configured internally.

## Geometry

For each pair of consecutive valid samples, the curve is a straight segment in
plot coordinates, after datetime conversion and any logarithmic transforms.
A constant baseline closes the area vertically. Crossings of the baseline fill
both sides, with no artificial gap at the crossing. Split at the crossing when
constructing polygons to avoid a self-intersecting quadrilateral.

NaN or infinite coordinates break connectivity. Nonpositive values on log axes
must break connectivity after transformation. Never remove invalid samples and
then connect their surviving neighbors. Gaps can still be covered by another
valid segment or series occupying the same coordinates.

The agreed geometry is the union of each segment's area to the baseline.
Overlapping and retraced regions remain filled. This supports arbitrary sample
order, decreasing x, and repeated x values. Preserve input order.

For a fixed baseline, union intervals always share that baseline, which is why
column extrema suffice. A future second-curve API would require revisiting this
property.

Vertical segments and segments exactly on the baseline have zero geometric area.
Their existing points and optional line stroke remain visible. Positive-area
segments that become narrower than one pixel need the raster coverage rule below.

## Rasterization contract

The current renderer maps coordinates with `(size - 1)` and rounds pixel indices
using NumPy rounding, then flips y. ASCII uses 1x1 pixels per character, block
uses 2x2, and Braille uses 2x4. Fill must use these same transforms.

The agreed coverage rule marks a pixel when its cell has positive-area overlap
with the clipped filled region. Clamp the outermost cell boundaries to the
viewport. This preserves narrow areas in compressed sparkline output. Point
and line coverage remains governed by the existing drawing routines. A filled
edge may therefore differ by a subpixel from a separately rasterized stroke.
Document and test that difference instead of assuming pixel-perfect equality.

A one-pixel axis needs an explicit special case. Treat its sole cell as spanning
that axis's viewport extent. Do not divide by `size - 1` or collapse all geometry
before evaluating whether it has area. This matters especially for ASCII height
one and width-one output.

Implement a small geometry reference first. Review expected pixel matrices for
crossings, edges, thin triangles, and degenerate segments before optimizing.

## Visibility and clipping

Area visibility and stroke visibility are separate predicates. A segment above
the viewport can have visible fill extending to a baseline below it.

| Situation | Fill result |
| --- | --- |
| Segment above view, baseline below view | Full visible height over its x span |
| Segment and baseline both above view | Empty |
| Segment below view, baseline inside view | Bottom edge through baseline |
| Segment and baseline both below view | Empty |
| Both endpoints outside x range on opposite sides | Process the crossing span |
| Whole segment x extent outside view | Empty |

Use floating-point geometry for rejection and clipping before integer conversion.
First clip each segment's x domain to the visible range, preserving its
interpolated y values. Determine area intervals against the original baseline,
then intersect those intervals with the visible y range. Clamping endpoints' y
values before interpolation changes slopes and gives incorrect coverage.

Skip a segment when its filled bounding region cannot overlap the viewport.
A bounding-box intersection is only a candidate test, not proof of coverage.
Handle fully covered columns directly. No allocation or loop bound should depend
on the distance to an off-screen endpoint or baseline. Guard interpolation
against overflow with very large finite inputs.

The actual line code currently generates candidates before final viewport
rejection. Numba counts and allocates samples using projected segment lengths.
The NumPy fallback allocates batch arrays using the largest sample count in that
batch. Large off-screen segments can therefore be expensive already. Earlier
claims that the line renderer already skips all that work were too broad.

For filled plots with `lines=True`, optimizing fill alone leaves this line cost.
Any stroke-clipping change needs an independent equivalence check against the
existing line rasterizer. Restarting sampling at a clipped endpoint can change
rounding and pixel placement. Preserve its original sampling phase or explicitly
review and test the changed stroke behavior.

## Bounds, scales, and state

Explicit numeric baselines participate in automatic y bounds for enabled
series with at least one positive-area segment. Apply existing padding afterward.
User-specified and interactively pinned bounds take precedence independently.
An isolated point or all-invalid series should not expand bounds solely because
of a fill setting. Preserve the current empty-data behavior.

Resolve `"bottom"` from the current y minimum at render time, after bounds are
established. It does not contribute to autoscaling. It follows pan, zoom, and
reset, even when those operations do not rebuild options.

On logarithmic y axes, numeric baselines must be positive. Transform them once
from original data units. Preserve the original option in `plot_gen` so repeated
updates cannot apply logarithms repeatedly. On log x axes, use transformed x
coordinates for interpolation, matching existing lines.

Datetime y axes accept datetime baselines and finite numeric Unix timestamps
in seconds, matching existing axis-bound conversion. Use `floatify` and its
`datetime64[s]` convention. Reject NaT before conversion because NumPy can turn
it into a finite sentinel. Per-series lists accept the same baseline values.
Validate persisted baselines against the current axis type on data updates.

Persist `fill` across data-only updates. Explicit `fill=None` clears it. Snapshot
mutable per-series lists using the existing defensive-copy path. Revalidate list
length if the number of series changes. Resize and Rich width constraints require
recomputing coverage for the final pixel dimensions.

## Integration and performance

`param_initializer.py` normalizes per-series settings and baseline units.
`Options.fill` belongs in alphabetical order. `layer_factory.render_points`
passes each series' fill setting into pixel rendering. Add fill before that
series' existing points and optional lines. Series remain processed in order.

Preserve existing encoding semantics. Later series own overlapping pixels. For
block and Braille, the character encoder chooses the highest series index in a
cell and suppresses other series' subpixels in that cell. Consequently a small
foreground shape can hide background fill across part of a character. Same-color
fill does not remove this existing limitation. ASCII uses series characters.
Filled cells cover gridlines under the current layer assembly order.

Keep the disabled-fill execution path free of fill buffers and extra geometry
passes. For enabled fill, stream segments in batches and reduce coverage into
viewport-sized column bounds, then paint each covered interval once per series.
Carry segment connectivity correctly across batch boundaries. Complexity targets
are linear input scanning plus visible segment-column work and viewport painting.
Repeated wide segments can still cost O(N * width); do not claim an unconditional
O(N + width * height) algorithm.

Numba parallel workers must not race on shared minima and maxima. Use disjoint
column ownership or bounded worker-local reductions, selected through benchmarks.
Identical final pixel writes do not make extrema updates race-safe. The existing
`fastmath=True` setting also needs review around finite checks and intersections.
NumPy and Numba must implement the same coverage and invalid-value rules.

## Validation and implementation sequence

1. Confirm remaining bounds and state details against the agreed geometry,
   coverage, and datetime baseline rules.
2. Implement a simple bounded reference and hand-checked pixel fixtures.
3. Integrate normalization, bounds, streaming, helper APIs, and character encoding.
4. Implement optimized NumPy and Numba paths and compare against the reference.
5. Run benchmarks and `make test` before considering the feature complete.

Tests must cover zero baselines and rejected booleans; per-series broadcasting;
negative and mixed-sign data; increasing, decreasing, repeated, and reversing x;
vertical and zero-area segments; isolated points; invalid data and batch-boundary
gaps; all clipping cases above; exact viewport edges; one-pixel axes; all character
sets; overlapping series; automatic and pinned bounds; log transforms; repeated
renders; resize; option clearing; and concurrent input snapshots.

Use independent expected geometry and deterministic randomized reference parity.
Test optimized implementations with Numba available and unavailable, following
`tests/unit/test_numpy_fallback.py`. Ensure tiny and extreme coordinate values do
not cause allocation growth, overflow, or false connections.

Benchmark warm and cold JIT separately. Compare unfilled baseline performance and
filled plots across small inputs through millions of samples, dense and sparse
series, steep and nearly horizontal segments, mostly off-screen inputs, repeated
wide segments, multiple series, and sparkline dimensions. Measure peak memory as
well as elapsed time. Reuse the workloads in `scripts/scaling_benchmark.py` where
appropriate. Record measured results before setting numerical regression limits.

## Prior art

Matplotlib exposes `fill_between(x, y1, y2=0)`, optional masks and steps, and
intersection interpolation for conditional regions. Its implementation builds
polygons per contiguous valid region and includes both boundaries in data bounds.
[API](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.fill_between.html),
[implementation inspected](https://raw.githubusercontent.com/matplotlib/matplotlib/v3.10.8/lib/matplotlib/collections.py)

Bokeh exposes `varea` and `harea` with two boundaries. Its documented NaN gap
behavior for patches should not be assumed for every version of `varea`. The 3.8
implementation inspected follows one boundary forward and the other backward.
The latest `varea` source could not be verified during research.
[Area guide](https://docs.bokeh.org/en/latest/docs/user_guide/basic/areas.html),
[implementation inspected](https://raw.githubusercontent.com/bokeh/bokeh/branch-3.8/bokehjs/src/lib/models/glyphs/varea.ts)

## Implementation and measured results

The implementation uses a batched NumPy fill pass and an optional serial Numba
kernel. Serial extrema reduction avoids shared-write races. Both backends are
checked against independent polygon clipping in the tests. NumPy skips columns
outside each batch's x extent. Fill memory scales with batch size and viewport
size. Filled strokes use a bounded sampler that retains the original major-axis
sampling grid for ordinary multi-pixel dimensions. One-pixel axes clip in data
space before coordinate collapse. Unfilled strokes keep the existing sampler.

Regression tests also identified missing-data issues. Datetime NaT now converts
to NaN. An all-invalid series is ignored when finding bounds alongside valid
series. Nonempty all-invalid data raises an error; empty input preserves the
existing empty-plot behavior. Filled plots treat
infinite coordinates as gaps. Point rasterization rejects out-of-range rounded
coordinates before integer conversion and clips collapsed axes in data space.

Local warm timings below are medians of three runs, measured at the pixel-renderer
entry point on November 14, 2026. They exclude input creation, option validation,
character encoding, and terminal output. The ordinary viewport is 120x68 pixels;
the sparkline viewport is 10x4. Input uses a fixed random seed. The committed
renderer was read into a temporary module for the unfilled comparison.

| Workload | NumPy | Numba |
| --- | --- | --- |
| One million points, committed renderer | 10.1 ms | 10.6 ms |
| One million points, current unfilled renderer | 10.7 ms | 11.1 ms |
| One million points with fill | 41.7 ms | 42.4 ms |
| One million points with sparkline fill | 37.5 ms | 32.9 ms |
| 10,000 segments repeatedly crossing the viewport with fill | 19.7 ms | 7.0 ms |
| Off-screen filled stroke spanning x = +/-1e100 | 2.4 ms | 0.1 ms |

For the million-point fill, tracemalloc recorded approximately 1.66 MiB of peak
additional allocation with NumPy and 0.67 MiB with Numba. The off-screen filled
stroke used about 0.18 MiB in both cases. These are traced allocations after
warm-up, excluding input arrays and process/JIT memory, rather than total RSS.
First-call accelerated fill in the final benchmark took 148 ms including cached
JIT loading; this is not a measurement of fresh compilation. Tests exercise both
installed and absent Numba environments. Timing differences of fractions of a
millisecond should be interpreted with normal run-to-run noise.


## Edge-case audit, November 15, 2026

The final review added deterministic coverage where the original random tests
were insufficient. The following map lists representative tests; parameterized
geometry tests execute against both NumPy and Numba when installed.

| Contract | Coverage |
| --- | --- |
| Baseline types, zero, broadcasting, disabled series, invalid lengths | `test_invalid_fill`, `test_fill_scalar_broadcast`, `test_per_series_fill_snapshot_and_length` |
| Crossings, reversed/repeated x, vertical and zero-area geometry | `test_triangle_and_reversal`, `test_isolated_points_and_zero_area`, `test_clipping_and_cell_edges_against_reference` |
| Missing samples and batch-boundary gaps | `test_nonfinite_samples_break_connections`, `test_gap_at_batch_boundary`, `test_datetime_nat_breaks_fill` |
| Off-screen boundaries and exact cell edges | `test_offscreen_boundary`, `test_clipping_and_cell_edges_against_reference` |
| Narrow areas and collapsed dimensions | `test_tiny_area_survives`, `test_single_cell_does_not_show_wholly_offscreen_geometry` |
| Extreme geometry and bounded line sampling | `test_extreme_offscreen_coordinates`, `test_extreme_diagonal_preserves_visible_slope` |
| Large x offsets, including timestamp-sized values | `test_fill_is_invariant_under_x_translation` |
| Stroke consistency | `test_filled_line_stroke_matches_existing_sampling` |
| Autoscaling, pinned bounds, clearing and data updates | `test_fill_expands_bounds_and_can_be_cleared`, `test_single_point_does_not_expand_bounds`, `test_pinned_y_bounds_survive_filled_data_updates` |
| Pan, zoom, reset and resize | `test_bottom_fill_tracks_pan_zoom_and_reset`, `test_resize_fill_and_restore` |
| Log transforms and nonpositive data | `test_log_baseline_transformed_once`, `test_log_x_fill_uses_transformed_segments`, `test_nonpositive_log_samples_break_fill` |
| Datetime baselines, NaT rejection, axis type changes and recovery | `test_datetime_and_numeric_baselines_match`, `test_datetime_nat_baseline_rejected_on_datetime_axis`, `test_datetime_fill_revalidated_on_axis_type_change` |
| Empty input and all-invalid series | `test_empty_fill_preserves_empty_plot_behavior`, `test_fill_without_valid_data_raises`, `test_invalid_series_does_not_affect_another_filled_series` |
| Character sets, overlap ownership and gridlines | `test_fill_is_independent_of_lines`, `test_per_series_fill_uses_existing_character_and_overlap_order`, `test_foreground_point_keeps_existing_character_color_priority`, `test_fill_covers_gridlines` |
| Mutable option snapshots and concurrent rendering | `test_per_series_fill_snapshot_and_length`, `test_set_data_is_thread_safe_under_render` (now also parameterized with fill) |

Three defects were reproduced with failing regression tests and corrected.

- Extreme diagonals could lose their visible slope through cancellation. A rare
  high-precision clipping path now handles endpoints over a trillion times the
  viewport coordinate scale before ordinary interpolation. It uses standard-library
  Decimal with precision covering float64's exponent range. Such extreme inputs
  cost more per segment; normal geometry stays on the vectorized/compiled paths.
- Scaling every segment by absolute x magnitude perturbed exact cell boundaries
  for timestamp-sized offsets. Scaling is now reserved for huge coordinates
  where subtraction could overflow.
- A failed streaming recomputation cleared its dirty flag and partially updated
  state. Validation now completes before committing new series, options, and
  pinned-bound state, and errors remain reproducible until corrected.

The earlier timing table predates these review fixes. Random geometry checks and
hand-checked fixtures provide complementary coverage, not an exhaustive proof of
all floating-point inputs. Cold JIT compilation and whole-process peak RSS remain
unmeasured; the existing figures report warm timing and traced temporary memory.
