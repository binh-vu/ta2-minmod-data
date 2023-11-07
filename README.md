# MinMod Knowledge Graph

This repository contains the datasets used to create the mineral site knowledge graph. The knowledge graph integrates heterogeneous data sources including scholarly articles, geolocation databases, and structured tables to provide a rich, queryable graph of mineral site information.

## Repository Structure

- `/data`: This directory contains all the raw data used to build the MinMod knowledge graph.
- `/deployment`: This directory holds the final `.ttl` file that is deployed on our online SPARQL endpoint.
- `README.md`: Provides an overview and guidance on how to use the repository.

## Schema

The data in this knowledge graph adhere to this [schema](https://github.com/DARPA-CRITICALMAAS/schemas/blob/main/ta2/README.md).

## Deployment

The final Turtle file (`final.ttl`) is deployed and can be queried at our online SPARQL endpoint: [SPARQL Endpoint](https://minmod.isi.edu/sparql). You can also explore the data via our [Mineral Data Browser](https://minmod.isi.edu/).