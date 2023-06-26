# Project Plan

## Summary

<!-- Describe your data science project in max. 5 sentences. -->

This projects aims to analyzes the correlation between planted trees and speed limits in Berlin. The goal is to see if there is a correlation between the two and if so, how strong it is.

## Rationale

<!-- Outline the impact of the analysis, e.g. which pains it solves. -->

The analysis could influence city planners to incorporate more trees into city design to make it more attractive for citizens, while also reducing the speed of cars and making cities more walkable and safe.

## Datasources

<!-- Describe each datasources you plan to use in a section. Use the prefic "DatasourceX" where X is the id of the datasource. -->

### Datasource 1: Baumbestand Berlin - Straßenbäume - Sachdaten zur Karte - [WFS]

- Metadata URL: https://mobilithek.info/offers/-5687470862699743129
- Data URL: https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_wfs_baumbestand
- Data Type: WFS_SRVC

Planted trees in Berlin.

### Datasource 1: Tempolimits - [WFS]

- Metadata URL: https://mobilithek.info/offers/-8613064499673471355
- Data URL: https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_vms_tempolimits_spatial
- Data Type: WFS_SRVC

Speed limits in Berlin.

## Work Packages

<!-- List of work packages ordered sequentially, each pointing to an issue with more details. -->

1. [Automated data pipeline](https://github.com/motschel123/2023-amse/issues/1)
2. [Automated Tests](https://github.com/motschel123/2023-amse/issues/2)
3. [Continuous Integration](https://github.com/motschel123/2023-amse/issues/3)
4. [Data Visualisation](https://github.com/motschel123/2023-amse/issues/5)
5. [Deployment](https://github.com/motschel123/2023-amse/issues/4)
