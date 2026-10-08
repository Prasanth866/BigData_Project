# Problem #3: Semantic Knowledge Base (RDF / RDFS) - Museum Management

## Overview
This directory contains the semantic modeling, ontology design, RDF/RDFS graph representations, SPARQL queries, and execution scripts for the **Museum Management Semantic Knowledge Base**.

---

## Directory Structure

```text
problem3_rdf_museum/
├── ontology/
│   ├── museum.ttl           # W3C Turtle RDF representation (human-friendly)
│   ├── museum.rdf           # W3C RDF/XML standard interchange representation
│   └── museum.nt            # W3C N-Triples canonical representation
├── queries/
│   ├── q1_artworks_info.rq          # SPARQL query for artworks, artists, galleries & periods
│   ├── q2_artists_subclass_check.rq # SPARQL query for RDFS subClassOf reasoning
│   └── q3_labels_comments.rq        # SPARQL query retrieving metadata labels & comments
├── validate_and_query.py    # Python validator and SPARQL engine execution script
├── run.sh                   # Runner script
├── SOLUTION_REPORT.md       # Comprehensive academic/technical report answering Questions 1-7
└── README.md
```

---

## Solutions to the 7 Specified Questions

Detailed answers and mathematical/ontological justifications are available in [SOLUTION_REPORT.md](file:///Users/prasanth/Desktop/Projects/BigData/problem3_rdf_museum/SOLUTION_REPORT.md).

### Summary:
1. **Classes**: `mus:Person`, `mus:Artist`, `mus:Artwork`, `mus:Gallery`, `mus:ArtPeriod`
2. **Subclass Relationships**: `mus:Artist rdfs:subClassOf mus:Person .`
3. **Properties**: `mus:createdBy`, `mus:displayedIn`, `mus:belongsToPeriod`, `mus:creates`
4. **Domain & Range**:
   - `mus:createdBy`: Domain = `mus:Artwork`, Range = `mus:Artist`
   - `mus:displayedIn`: Domain = `mus:Artwork`, Range = `mus:Gallery`
   - `mus:belongsToPeriod`: Domain = `mus:Artwork`, Range = `mus:ArtPeriod`
   - `mus:creates`: Domain = `mus:Artist`, Range = `mus:Artwork`
5. **Individuals**:
   - Artists: `mus:Leonardo`, `mus:VanGogh`
   - Artworks: `mus:MonaLisa`, `mus:StarryNight`
   - Galleries: `mus:Gallery1`, `mus:Gallery2`
   - Art Periods: `mus:Renaissance`, `mus:PostImpressionism`
6. **RDF/RDFS Triples**: Serialized in Turtle (`museum.ttl`), RDF/XML (`museum.rdf`), and N-Triples (`museum.nt`).
7. **Labels & Comments**: Explicit `rdfs:label` and `rdfs:comment` annotations attached to all schema entities and instances.

---

## Execution

Run the validation and query pipeline:
```bash
./run.sh
```
Or directly:
```bash
python3 validate_and_query.py
```
