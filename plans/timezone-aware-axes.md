# Timezone-aware axes: research and implementation plan

Status: implemented with TDD. Research and implementation date: 2026-11-16.

## Implementation record

The implementation followed the no-options contract below. Shared normalization
now covers native datetime sequences, pandas and Polars, both axes, scalar
bounds/gridlines/fill baselines, histogram axes and repeated plot updates.
Aware ticks use local calendar rules and include offsets during repeated hours;
naive labels retain their existing behavior.

Tests were written and run before implementation: the initial 43 cases all
failed. Further red/green iterations covered automatic padding at midnight,
one-label fallbacks, fill baselines, dateutil timezone caching, pinned bounds
when awareness changes, and histogram timezone preservation. The final feature
suite has 64 passing cases and one optional pytz test skipped in this environment
(pytz is installed by pandas on the supported Python 3.10 environment).

Final `make test` (2026-11-20): **336 passed, 28 skipped**, with format, lint, type and example
checks also passing. A seeded sweep exercises seconds through years on both
axis directions. The manual gallery in `scripts/timezone_axis_visual_control.py`
was inspected at widths 30, 60 and 100, including vertical axes.

Implementation details discovered through visual checks:

- Automatic padding is clamped at local date boundaries so a midnight-starting
  single-day plot does not acquire an unnecessary previous-day date context.
- Labels use the shared renderer's centering based on their final text length;
  aware tick selection rejects sets that exceed the available width rather than
  shifting individual labels away from their ticks.
- A narrow aware axis may retain one complete label instead of none.
- `tzdata` is a runtime dependency for systems without an IANA database.

Review follow-up: library-specific timezone tests live in their acceptance test
files; core normalization and tick-label tests use native datetime inputs. A
regression test verifies that offset-bearing labels retain ordinary centering.

Local median label-search timings over 15 calls (milliseconds, not full plots):

| Range | Naive cold | Aware cold | Aware panning |
|---|---:|---:|---:|
| 12 hours | 0.71 | 4.01 | 2.61 |
| 31 days | 1.10 | 2.08 | 2.01 |
| 365 days | 1.13 | 3.54 | 2.63 |

Cold measurements cleared label/conversion caches; panning shifted each range
by 37 seconds. Exact cache hits were below 0.001 ms. These are local observations,
not cross-platform performance guarantees. Datetime resolution remains seconds.

## Recommendation

Use the PR's central idea: normalize instants to UTC-based coordinates, generate
round ticks in the axis timezone, and format those ticks locally. Generalize
input handling and improve label selection before accepting this as a complete
solution. Do not require callers to provide UTC input.

Keep the current layout. Readability means useful coverage, locally round tick
times, sufficient date information, and unambiguous repeated-hour labels within
the available character budget. Unequal tick spacing around clock changes is
acceptable; changing the elapsed-time spacing of observations is not.

## Decisions from the interview

- Agreed API: **no explicit timezone options**. Infer timezone from
  aware input on either axis. Callers can convert aware input before plotting
  when they want a different display timezone.
- Naive input retains its supplied calendar/clock readings, as today. This is
  an abstract wall-clock axis, not an implicit conversion from the computer's
  timezone. It cannot distinguish repeated autumn readings.
- Differing aware input timezones use the first series' timezone
  and produce a warning. Normalize each aware sample using its own timezone.
- Repeated autumn-hour labels must include distinct numeric UTC offsets, even
  if fewer ticks fit.
- Preserve the existing axis layout, with self-contained labels and no extra
  date/timezone context line.
- Reject a mixture of aware and naive values on the same axis rather than
  guessing their relationship.

The earlier explicit-option design has been superseded by this simpler contract.
Never infer the computer's local timezone. Missing values do not count as naive
values. Different axes may independently be aware, naive or numeric.

## What the issue and PR establish

[Issue #53](https://github.com/olavolav/uniplot/issues/53) correctly identifies
both the unwanted UTC labels and the distortion caused by removing timezone
information before plotting: spring gaps and overlapping autumn observations.

Reviewed the live PR head
[`2a3afe1`](https://github.com/olavolav/uniplot/pull/54/commits/2a3afe1abbee7702ba66b35a4da3a478a1ce2f32),
which has four commits and supports **both axes**. The cached PR description
still described the older, x-only version; that is not the reviewed revision.

Useful parts of the implementation:

- UTC-based data coordinates and local calendar tick candidates.
- Local-to-UTC round-trip validation: nonexistent candidates disappear, and
  repeated candidates can produce two distinct instants.
- Collision checking after local formatting.
- Conversion caching and a fast pandas normalization path.

Gaps in the current head, confirmed by source inspection and isolated execution:

1. Inference/normalization recognizes pandas `.tz` / `.dt.tz`, not timezone-aware
   Python datetime sequences. Equivalent input representations behave differently.
2. Multiple series silently select the first detected timezone; there is no
   warning policy. The absence of an explicit option matches the latest design.
3. Repeated-hour labels remain identical. Offset information has been removed
   before string formatting.
4. Date shortening considers only the selected ticks. A range crossing midnight
   can select ticks exclusively on the second day and then remove all dates.
5. Aware explicit bounds and gridlines still use the separate `floatify` path;
   general input normalization must cover these too.
6. The fallback from failed `ZoneInfo` conversion returns the original timezone.
   That is not sufficient for pytz objects, whose localization semantics differ.
7. The PR predates current missing-value handling and label-margin changes.
   Adapt its ideas to the current code; do not replace current files wholesale.

These are reasons to rework the proposal, not evidence that its core algorithm
is wrong. Its locally aligned daytime labels are already good.

## Reproduced label behavior

Ran the exact PR snapshot outside the checkout using the existing development
environment. These are actual selected tick texts, not proposed output:

| Local range / input | Width | Tick texts |
|---|---:|---|
| Amsterdam, Nov 2, 09:00–21:00 | 60 | `09:00 12:00 15:00 18:00 21:00` |
| Kathmandu, Nov 2, 09:00–21:00 | 60 | `09:00 12:00 15:00 18:00 21:00` |
| Amsterdam, Nov 2 22:00–Nov 3 04:00 | 60 | `00:00 03:00` |
| Amsterdam, Nov 2 09:00–Nov 4 09:00 | 60 | `2026-11-03 2026-11-04` |
| Amsterdam autumn transition, 00:00–03:00, four elapsed hours | 60 | `00:00 01:00 02:00 02:00 03:00` |
| Amsterdam spring transition, 00:00–10:00, nine elapsed hours | 60 | `00:00 03:00 06:00 09:00` |
| Tokyo 09:00–18:00, pandas DatetimeIndex | 60 | `09:00 12:00 15:00 18:00` |
| Same instants, Python aware datetime list | 60 | `00:00 03:00 06:00 09:00`, with warnings |

The midnight case illustrates the user's concern even without a DST transition.
The multi-day case is sparse rather than incorrect. A redesigned formatter must
be assessed with actual terminal output, not only conversion assertions.

## Comparison with other libraries

| Aspect | Matplotlib | Bokeh | Implication for uniplot |
|---|---|---|---|
| Coordinates | Numeric days since an epoch | Numeric milliseconds since Unix epoch | Keep numeric instants separate from local labels |
| Timezone selection | Date converter infers tzinfo; locators and formatters accept a timezone | Standard datetime formatter has no axis timezone property | Matplotlib is the closer timezone architecture |
| Tick generation | Calendar locators and sensible interval multiples | Composite datetime ticker; calendar day generation uses UTC operations | Localize tick selection as well as tick strings |
| Compact labels | ConciseDateFormatter removes redundancy and uses shared context | Boundary scaling, optional context, suppression of repeated text | Consider date boundaries and the complete visible range |

Matplotlib's DateConverter takes timezone information from the first usable
value and passes it to both locator and formatter. Its timezone-aware machinery
is not a guarantee of ideal DST labels; uniplot still needs explicit collision
and repeated-hour tests. Sources: [date API](https://matplotlib.org/stable/api/dates_api.html),
[converter source inspected at v3.10.7](https://github.com/matplotlib/matplotlib/blob/v3.10.7/lib/matplotlib/dates.py),
[concise formatting examples](https://matplotlib.org/stable/gallery/ticks/date_concise_formatter.html).

Bokeh's built-in formatter supports different formats by scale and richer
context, but does not expose a timezone-selection property. Its day ticker uses
UTC calendar operations. Merely adding a custom local formatter would therefore
not establish local midnight ticks. Sources: [time-series units](https://docs.bokeh.org/en/latest/docs/user_guide/topics/timeseries.html),
[formatter API](https://docs.bokeh.org/en/latest/docs/reference/models/formatters/DatetimeTickFormatter/index.html),
[day ticker source, 3.10.0](https://github.com/bokeh/bokeh/blob/3.10.0/bokehjs/src/lib/models/tickers/days_ticker.ts),
[formatter source, 3.10.0](https://github.com/bokeh/bokeh/blob/3.10.0/bokehjs/src/lib/models/formatters/datetime_tick_formatter.ts).

Borrow the separation of coordinates, tick location and formatting. Do not copy
Matplotlib's extra context area or Bokeh's repeated-label suppression: those
conflict with the requested layout and repeated-hour policy.

## Implementation sequence

### 1. Define and centralize normalization

Introduce a small axis-independent datetime normalization module/helper. Keep
`MultiSeries` responsible for series organization, not timezone arithmetic.
Retain numeric seconds and missing-value behavior; subsecond support is a
separate change.

Support native datetime sequences, NumPy datetime arrays, pandas Index/Series,
and timezone metadata from Polars, which is already a supported integration.
Keep pandas and Polars optional; use vectorized adapters where available.
Normalize IANA timezone names, standard-library fixed offsets and known pytz
zones deliberately. Do not treat equal current offsets as equal timezone rules.
Use the first nonempty series' first valid timezone when inference encounters
different zones, including heterogeneous aware datetime lists; warn on conflicts.

Resolve the axis's awareness mode and display timezone once per plot/update. Preserve
awareness metadata until normalization is complete. Ignore missing values for
timezone selection and issue each warning once per axis per render, not once
per observation or tick candidate.

Unify scalar conversion for explicit bounds and existing datetime gridlines with
the same policy: aware datetime bounds on an aware axis, naive datetime bounds
on a naive axis; numeric bounds retain their existing coordinate meaning. Reject
awareness mismatches rather than assigning a timezone. In interactive
updates, resolve new input metadata without converting already-normalized pinned
bounds a second time.

### 2. Resolve local times correctly

Aware input supplies an offset and therefore a definite UTC instant. Naive
input is not localized at all. Do not add DST interpretation to naive-only data.
For aware input, preserve the supplied fold/offset choice; validate invalid
named-zone wall times by round trip rather than silently correcting them.

Local calendar tick generation still needs DST handling: a candidate can map to
zero, one or two UTC instants. Use both fold choices and a UTC round trip.
Nonexistent ticks are omitted; repeated-hour candidates can include both
instants, ordered in UTC. This logic does not guess the meaning of naive input.

Use `zoneinfo` for IANA rules. Decide packaging explicitly: `zoneinfo` needs
system timezone data or the `tzdata` package. A small `tzdata` dependency is the
recommended portable solution if IANA names must work on all supported systems.
Do not silently fall back to a fixed offset when rules are unavailable.
[Python zoneinfo documentation](https://docs.python.org/3/library/zoneinfo.html)
describes both fold handling and this deployment requirement.

### 3. Generate locally round candidates

Extend the shared `datetime_labels` path, used for both directions. Generate
seconds/minutes/hours and calendar days/months/years in local time, then map to
UTC coordinates, sort, deduplicate and crop there. Preserve local midnight and
month/year boundaries across offset changes.

Use the PR's fold-aware conversion as a starting point. Verify the candidate
envelope around a rollback, including a viewport entirely inside the repeated
hour. Cover half-hour transitions and non-hour offsets; do not hard-code a
one-hour DST adjustment. Permit uneven physical tick spacing.

Retain the existing search/scoring structure initially. Add a bounded fallback
to fewer useful labels if normal candidates do not fit. Avoid an unnecessary
general replacement of the label-search algorithm.

### 4. Select format and tick density together

Pass the complete local view interval and each tick's offset into formatting;
do not flatten everything to naive NumPy datetimes before deciding strings.

- Within a single local day, retain short time labels where sufficient.
- Across midnight, retain date information even if selected ticks all fall on
  one day. Start with compact, locale-neutral `MM-DD HH:MM` within a year and
  include the year when the visible range requires it; keep each label
  self-contained rather than relying on a new context line.
- For day/month/year ticks, preserve existing compact calendar formats where
  sufficient. Candidate formatting should not invent precision absent in input.
- Distinguish ambiguous local-hour labels with numeric offsets, e.g.
  `02:00+02:00` and `02:00+01:00`. Detect ambiguity from timezone rules, not
  merely duplicate text among retained ticks, so thinning cannot hide it.
- Measure final strings, including date and offset, before accepting a candidate.
  Re-score density and coverage after formatting. Prefer fewer informative ticks
  to overlap or ambiguous text. Keep explicit bounds and line-length caps intact.

Prototype the midnight and autumn cases first and inspect them at widths 30,
60 and 100, plus short vertical axes. Exact format choices can be adjusted from
these renderings without another public option.

### 5. Verify and document

Test properties as well as a small curated set of rendered outputs:

- Same instant in different supported input representations gets the same
  coordinate. Both axes use the same normalization and labeling semantics.
- Inference, mismatched-zone warnings and mixed naive/aware
  inputs have deterministic, documented behavior.
- UTC positions remain ordered through both DST transitions. Nonexistent ticks
  are absent; retained repeated-hour ticks carry distinct offsets.
- Midnight coverage, month/year changes, fractional offsets, a half-hour DST
  zone, fixed offsets, missing values and empty series.
- Explicit datetime bounds, gridlines, interactive updates, hard width caps,
  and numeric/naive regressions.
- Seeded range/width sweeps check no overlap, valid tick placement and usable
  labels when space permits. A visual gallery checks quality beyond invariants.

Benchmark cold calls and panning as well as cache hits on 12-hour, month and
year ranges. Preserve the vectorized naive path and use bounded timezone-aware
caches. The PR reports a 12-hour slowdown; measure locally before setting a
performance budget rather than adopting that report as a verified target.

Document examples for native datetime, pandas, both axes, conversion of aware
input before plotting, mixed-zone warnings and the limitations of naive input.
Run `make test`
before completion. Version-control operations remain entirely with the user.

## Verification performed for this research

- Current checkout: `make test` passed, including formatting, lint, typing,
  visual examples and unit tests: **272 passed, 27 skipped**.
- Exact PR snapshot: pytest suite **206 passed, 2 skipped** under the existing
  development environment. This is not a full PR `make test` or a CI matrix.
- Separate probes reproduced the label cases above. Existing checkout code was
  not replaced or modified to execute the PR. No version-control mutation was
  performed.
