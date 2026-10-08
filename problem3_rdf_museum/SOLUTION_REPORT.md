# Problem #3: Semantic Knowledge Base (RDF / RDFS) - Museum Management

## Executive Summary & Formal Solution Report

This report provides the formal semantic modeling and knowledge representation for the **Museum Management Knowledge Base** according to W3C RDF and RDF Schema (RDFS) standards.

---

## 1. Identification of Suitable Classes
Based on the domain requirements ("information about artworks, artists, galleries and art periods", "Every artist is a person"), the following five primary classes are identified:

| Class Identifier (`mus:Class`) | Natural Language Concept | Ontological Definition |
|---|---|---|
| `mus:Person` | Person | The class of all human beings. |
| `mus:Artist` | Artist | The class of individuals who engage in the creation of visual art. |
| `mus:Artwork` | Artwork | The class of tangible or conceptual creative artistic works. |
| `mus:Gallery` | Museum Gallery | The class of museum exhibition halls or spaces where artworks are displayed. |
| `mus:ArtPeriod` | Art Period | The class of historical epochs or stylistic movements in art history. |

---

## 2. Establishment of Subclass Relationships
The problem statement asserts:
> *"Every artist is a person."*

In RDFS semantics, this translates to an `rdfs:subClassOf` assertion:
$$\text{mus:Artist} \sqsubseteq \text{mus:Person}$$

### RDF/RDFS Triple:
```turtle
mus:Artist rdfs:subClassOf mus:Person .
```

### Ontological Hierarchy:
```text
           ┌──────────────┐
           │  mus:Person  │
           └──────▲───────┘
                  │ rdfs:subClassOf
           ┌──────┴───────┐
           │  mus:Artist  │
           └──────────────┘
```

**Inference Rule (RDFS Entailment rdfs9):**
If an individual $u$ is declared as `rdf:type mus:Artist`, an RDFS-compliant reasoning engine automatically infers:
$$u \text{ rdf:type } \text{mus:Person}$$
Therefore, `mus:Leonardo` and `mus:VanGogh` are entailed to be instances of `mus:Person`.

---

## 3. Derivation of Appropriate Properties
Analyzing the relations stated in the scenario:
1. *"Artists create artworks"* / *"MonaLisa was created by Leonardo"*:
   - Primary property: `mus:createdBy` (relates an artwork to its artist)
   - Inverse property: `mus:creates` (relates an artist to their created artworks)
2. *"Artworks are displayed in galleries"* / *"MonaLisa is displayed in Gallery1"*:
   - Property: `mus:displayedIn` (relates an artwork to the gallery displaying it)
3. *"Artworks ... belong to historical art periods"* / *"MonaLisa belongs to the Renaissance period"*:
   - Property: `mus:belongsToPeriod` (relates an artwork to its historical art period)

---

## 4. Specification of Domain and Range of Each Property
In RDF Schema:
- `rdfs:domain` states that the subject of any triple using the property is an instance of the specified class.
- `rdfs:range` states that the object of any triple using the property is an instance of the specified class.

| Property | `rdfs:domain` (Subject Class) | `rdfs:range` (Object Class) | Semantic Description |
|---|---|---|---|
| `mus:createdBy` | `mus:Artwork` | `mus:Artist` | An artwork was created by an artist. |
| `mus:displayedIn` | `mus:Artwork` | `mus:Gallery` | An artwork is physically exhibited in a museum gallery. |
| `mus:belongsToPeriod` | `mus:Artwork` | `mus:ArtPeriod` | An artwork belongs to a historical art period. |
| `mus:creates` | `mus:Artist` | `mus:Artwork` | An artist created an artwork (inverse relationship). |

---

## 5. Identification of Individuals (Instances)
The entities identified from the explicit assertions:

| Individual URI | Class (`rdf:type`) | Common Name / Description |
|---|---|---|
| `mus:Leonardo` | `mus:Artist` | Leonardo da Vinci (High Renaissance master) |
| `mus:VanGogh` | `mus:Artist` | Vincent van Gogh (Dutch Post-Impressionist painter) |
| `mus:MonaLisa` | `mus:Artwork` | Mona Lisa (Famous portrait painting) |
| `mus:StarryNight` | `mus:Artwork` | The Starry Night (Famous landscape painting) |
| `mus:Gallery1` | `mus:Gallery` | Exhibition Gallery 1 |
| `mus:Gallery2` | `mus:Gallery` | Exhibition Gallery 2 |
| `mus:Renaissance` | `mus:ArtPeriod` | Renaissance historical art period |
| `mus:PostImpressionism` | `mus:ArtPeriod` | Post-Impressionism historical art movement |

---

## 6. Scenario Representation in RDF/RDFS Triples (Turtle Syntax)

```turtle
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix mus:  <http://example.org/museum#> .

# Classes
mus:Person             rdf:type rdfs:Class .
mus:Artist             rdf:type rdfs:Class ;
                       rdfs:subClassOf mus:Person .
mus:Artwork            rdf:type rdfs:Class .
mus:Gallery            rdf:type rdfs:Class .
mus:ArtPeriod          rdf:type rdfs:Class .

# Properties
mus:createdBy          rdf:type rdf:Property ;
                       rdfs:domain mus:Artwork ;
                       rdfs:range  mus:Artist .

mus:displayedIn        rdf:type rdf:Property ;
                       rdfs:domain mus:Artwork ;
                       rdfs:range  mus:Gallery .

mus:belongsToPeriod    rdf:type rdf:Property ;
                       rdfs:domain mus:Artwork ;
                       rdfs:range  mus:ArtPeriod .

mus:creates            rdf:type rdf:Property ;
                       rdfs:domain mus:Artist ;
                       rdfs:range  mus:Artwork .

# Individuals - Artists
mus:Leonardo           rdf:type mus:Artist ;
                       mus:creates mus:MonaLisa .

mus:VanGogh            rdf:type mus:Artist ;
                       mus:creates mus:StarryNight .

# Individuals - Artworks
mus:MonaLisa           rdf:type mus:Artwork ;
                       mus:createdBy mus:Leonardo ;
                       mus:displayedIn mus:Gallery1 ;
                       mus:belongsToPeriod mus:Renaissance .

mus:StarryNight        rdf:type mus:Artwork ;
                       mus:createdBy mus:VanGogh ;
                       mus:displayedIn mus:Gallery2 ;
                       mus:belongsToPeriod mus:PostImpressionism .

# Individuals - Galleries
mus:Gallery1           rdf:type mus:Gallery .
mus:Gallery2           rdf:type mus:Gallery .

# Individuals - Art Periods
mus:Renaissance        rdf:type mus:ArtPeriod .
mus:PostImpressionism  rdf:type mus:ArtPeriod .
```

---

## 7. Incorporation of `rdfs:label` and `rdfs:comment` Statements

```turtle
# Class Metadata
mus:Person
    rdfs:label "Person"@en ;
    rdfs:comment "A human being."@en .

mus:Artist
    rdfs:label "Artist"@en ;
    rdfs:comment "A person who creates works of art."@en .

mus:Artwork
    rdfs:label "Artwork"@en ;
    rdfs:comment "A physical or conceptual creation of artistic value."@en .

mus:Gallery
    rdfs:label "Museum Gallery"@en ;
    rdfs:comment "A room or building devoted to the exhibition of works of art."@en .

mus:ArtPeriod
    rdfs:label "Art Period"@en ;
    rdfs:comment "A distinct historical era characterized by a particular artistic style or philosophy."@en .

# Property Metadata
mus:createdBy
    rdfs:label "created by"@en ;
    rdfs:comment "Relates an artwork to the artist who produced or authored it."@en .

mus:displayedIn
    rdfs:label "displayed in"@en ;
    rdfs:comment "Identifies the museum gallery where an artwork is physically exhibited."@en .

mus:belongsToPeriod
    rdfs:label "belongs to period"@en ;
    rdfs:comment "Designates the historical art movement or period to which an artwork belongs."@en .

# Individual Metadata
mus:Leonardo
    rdfs:label "Leonardo da Vinci"@en ;
    rdfs:comment "Italian polymath of the High Renaissance active as a painter, draughtsman, and engineer."@en .

mus:VanGogh
    rdfs:label "Vincent van Gogh"@en ;
    rdfs:comment "Dutch Post-Impressionist painter known for bold colours and dramatic brushwork."@en .

mus:MonaLisa
    rdfs:label "Mona Lisa"@en ;
    rdfs:comment "Half-length portrait painting by Leonardo da Vinci."@en .

mus:StarryNight
    rdfs:label "The Starry Night"@en ;
    rdfs:comment "Oil-on-canvas painting by Vincent van Gogh depicting the view from his asylum room."@en .

mus:Gallery1
    rdfs:label "Gallery 1"@en ;
    rdfs:comment "Museum exhibition hall 1 dedicated to classical and Renaissance masterworks."@en .

mus:Gallery2
    rdfs:label "Gallery 2"@en ;
    rdfs:comment "Museum exhibition hall 2 dedicated to modern and post-impressionist masterworks."@en .

mus:Renaissance
    rdfs:label "Renaissance"@en ;
    rdfs:comment "Cultural movement marking transition from Middle Ages to modernity (14th-17th centuries)."@en .

mus:PostImpressionism
    rdfs:label "Post-Impressionism"@en ;
    rdfs:comment "Art movement developed between 1886 and 1905."@en .
```
