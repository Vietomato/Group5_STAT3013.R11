# INMET Weather Data Preparation and EDA

## Objective

Prepare external weather data for the Olist project
and examine descriptive relationships with late
delivery.

The prediction point follows the project's
purchase-time setting. Weather observed around
carrier handoff and customer delivery is retained
separately for retrospective EDA.

## Data Sources

Weather observations were obtained from INMET's
historical automatic-station archives for 2016,
2017 and 2018.

The archives contain:

- 2016: 529 station files.
- 2017: 563 station files.
- 2018: 596 station files.

There are 1,688 station-year files and 597 distinct
station codes across the three years. The archives
contain 14,276,088 hourly records.

The files use semicolon delimiters, decimal commas
and Latin-1 encoding. The missing-value code -9999
was converted to missing values.

Original archives and the official research dataset
were preserved.

Sources:

- https://portal.inmet.gov.br/dadoshistoricos
- https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Quality Review

The hourly audit detected no invalid timestamps,
duplicate station-file timestamps, timestamps outside
the expected annual calendar grid, unparsed numeric
measurements or nonfinite measurements.

Recorded rows and valid measurements were evaluated
separately. A recorded hourly row may still contain
missing weather values.

Some station files begin during the year. Calendar
hours without records therefore do not automatically
indicate equipment failure.

Extreme observations were inspected with nearby
hourly records. Values were not automatically removed
because they were large or unusual.

One gust observation of 78.7 m/s at station A101,
AM, on 4 October 2018 was retained with a review flag.
The corresponding station-day gust statistic was
temporarily excluded from the conservative state
candidate. Other weather variables were retained.

For that state-day, the mean station gust statistic
changed from 11.164 to 5.969 m/s. Thirteen of the
25 inventory stations remained usable, giving 52%
coverage.

This exclusion does not establish that the original
observation was incorrect.

Daily checks detected no violations of the evaluated
temperature relationships, humidity bounds,
non-negative rainfall and wind values, or finite-value
requirements.

## Daily and State-Level Aggregation

Daily windows are defined in UTC using observations
after day-start and up to day-end.

Hourly precipitation represents the preceding hour.
The midnight report of the following date is therefore
included in the preceding UTC rainfall day.

Each station-day feature requires 24 nonmissing
source values. Partial rainfall sums are stored
separately from complete daily totals.

The station-day table contains 616,649 rows.
Of these, 481,532 have complete daily rainfall.

Complete rainfall-day percentages are:

- 2016: 77.57%.
- 2017: 77.00%.
- 2018: 79.57%.

State-level candidates require at least two usable
stations and 50% of the annual station inventory.
Coverage is evaluated separately for each feature.

The state-day table contains 29,592 rows covering
27 federative units over 2016–2018.

The coverage denominator is the annual archive
inventory. It may include stations that began
operating later in the year. Operational prediction
would require an inventory available at the
prediction time.

The final rainfall day, 31 December 2018, lacks the
next midnight observation because the 2019 archive
was not included. This date is after the observed
order period used in this project.

## Weather Variables

Seven weather statistics are included:

- Daily rainfall total.
- Mean air temperature.
- Maximum air temperature from hourly maxima.
- Minimum air temperature from hourly minima.
- Mean relative humidity.
- Mean reported wind-speed samples.
- Maximum reported wind gust.

State values are means across usable stations.
Consequently, the temperature-extreme and gust
candidates represent means of station-level extremes,
rather than absolute extremes across the state.

Other INMET channels remain in the source archives
but are not included in the current joined candidates.

## Order-Level Matching

All 99,441 research orders were retained.

There are 98,666 orders with seller links.
The remaining 775 orders have missing delivery labels.

All 96,470 labeled orders have seller links.
Seller counts reconstructed from the source tables
match the research dataset.

There are 1,278 orders with multiple sellers and
510 orders with sellers in multiple states.

Origin weather is weighted by distinct seller counts
in each state. Sellers are counted once per order,
regardless of their number of item rows.

If any seller-state weather contribution is missing,
the full origin candidate remains missing.
Available seller weights are not renormalized.

Carrier handoff is recorded at order level. Applying
this timestamp to all sellers is an approximation,
rather than evidence that they dispatched together.

## Timezone and Feature Availability

Olist timestamps have no timezone information in the
available files. The source timezone remains
unverified.

Two assumptions are retained separately:

- Source timestamps interpreted as UTC.
- Source timestamps interpreted as America/Sao_Paulo.

These scenarios represent the same orders and must
not be pooled as independent observations.

Thirteen purchase timestamps remain unresolved under
the conservative Sao Paulo localization. These orders
were retained with missing scenario-specific weather.

Among 99,428 purchases comparable under both
assumptions, 14,364 were assigned different previous
UTC weather dates.

Purchase-time candidates use the previous complete
UTC weather day under each assumption.

No selected observation window ends after its assumed
purchase cutoff. However, INMET publication latency
has not been verified. This check therefore does not
establish operational data availability.

Weather from the handoff day and arrival day is marked
for retrospective EDA only.

## Labels and Missing Weather

The original labels were preserved by order ID:

- Not late: 89,936 orders.
- Late: 6,534 orders.
- Missing label: 2,971 orders.

The observed late-delivery rate among labeled orders
is 6.77%. The not-late to late ratio is 13.76.

Approximately 98.73% of labeled orders have all
14 pre-purchase origin and destination features.

Orders with incomplete retrospective weather have
late-delivery rates of 7.76–8.02%, compared with
approximately 6.76% among complete cases.

These descriptive differences support reporting
missingness rather than automatically deleting all
incomplete orders.

## Preliminary Findings

In pooled pre-purchase comparisons, late orders have
higher mean rainfall indices, air temperatures and
humidity. Wind mean differences are comparatively
small. Class interquartile ranges overlap.

For pre-purchase origin rainfall, the (5,10] mm group
has a late-delivery rate of 9.78–9.95%, compared with
4.85–4.88% in the (0,1] mm group.

The relationship is not consistently increasing.
The >10 mm origin group has a lower observed rate
than the (5,10] mm group.

The pooled association is not consistent across
purchase months. Sixteen months have at least
100 orders in both comparison groups under both
timezone assumptions.

In each scenario, the (5,10] mm origin group has a
higher late-delivery rate in eight months and a
lower rate in eight months than the (0,1] mm group.

The composition of purchase months may therefore
contribute to the pooled differences. State,
distance and delivery characteristics still require
examination.

## Research Questions

1. Do late-delivery rates differ between groups of
   pre-purchase origin rainfall?

2. Do late-delivery rates differ between groups of
   pre-purchase destination rainfall?

3. Do pre-purchase temperature, humidity and wind
   statistics differ between delivery labels?

4. How are handoff-day and arrival-day weather indices
   associated with historical delivery outcomes?

5. Do descriptive relationships persist when examining
   purchase month, geography and delivery distance?

For rainfall-group comparisons, the initial null
hypothesis is equality of late-delivery rates.

For mean weather comparisons, the initial null
hypothesis is equality of means between labels.

No hypothesis tests have been performed in this review.

## Limitations and Next Steps

Weather indices describe observed stations within
states. They do not measure conditions at each
customer address, seller address or delivery route.

Station coverage, missingness and station composition
can change across dates and years.

Orders sharing weather exposures may be dependent.
Formal inference must consider this structure and
multiple comparisons.

Arrival-day weather is retrospective. The arrival
date is itself an outcome of the delivery process.

The findings do not establish causality, statistical
significance or additional predictive value.

Before final model inclusion, the group should resolve
or explicitly document the timezone assumption,
review point-in-time data availability, and evaluate
weather additions using an appropriate time-based
validation design.