# Linear Algebra Intuition for GTM Engineers

> Vectors are rows in your CRM; matrices are operations that transform them.

> **Platform:** This course runs in Claude Code Desktop. Exercises happen in your terminal, not the browser.

**Type:** Learn
**Languages:** Python
**Prerequisites:** None
**Time:** ~45 minutes

---

## Learning Objectives

Understand vectors as ordered lists of business attributes (firmographic features, engagement scores) and perform element-wise operations on them.

Compute dot products to measure similarity between accounts, leads, or content embeddings without calling a black-box API.

Interpret matrix-vector multiplication as a batch transformation applied uniformly across a dataset — the same mechanism behind scoring models and recommendation engines.

Read the geometry of vector spaces well enough to reason about embedding dimensions, cosine similarity thresholds, and what "nearest neighbor" actually means in your pipeline.

## The Problem

You're handed an embedding from OpenAI or Cohere — 1536 floats — and you need to decide what "similar" means, pick a distance metric, and set thresholds that affect which accounts get routed to which reps.

Most GTM engineers treat linear algebra as someone else's problem until they have to debug why cosine similarity returns garbage matches, why their lead scoring weights produce nonsensical rankings, or why dimensionality reduction collapsed important signal.

The gap is intuition: what a vector actually represents in your domain, what a dot product computes mechanically, and why matrix operations scale the way they do.

## The Concept

**Vectors as data rows.** A vector is an ordered list of numbers — in GTM, that's a row of features describing an account, a contact, or a piece of content.

**Dot product as similarity.** The dot product multiplies corresponding elements and sums them; geometrically, it measures how much two vectors point in the same direction, weighted by magnitude.

**Cosine similarity as normalized dot product.** Dividing the dot product by the product of vector lengths gives a score between -1 and 1 that ignores magnitude and isolates direction — this is why it's the default for text embeddings.

**Matrices as transformations.** A matrix is a collection of vectors; multiplying a matrix by a vector applies a linear transformation — scaling, rotating, projecting — to that vector.

**Matrix multiplication as composed transformations.** Multiplying two matrices composes their transformations; this is the mechanism behind multi-layer neural networks and chained scoring functions.

## Build It

Implement a `Vector` class with `dot`, `magnitude`, and `cosine_similarity` methods using only Python built-ins (no NumPy), so the arithmetic is visible and debuggable.

Build a `Matrix` class that supports `multiply_vector` and `multiply_matrix`, with each step printing the intermediate computation for inspection.

Create a small dataset of account feature vectors (industry score, employee count band, engagement score, intent signal strength) and compute the full pairwise similarity matrix by hand.

## Use It

Given a set of account embeddings — real feature vectors derived from firmographic and behavioral data — rank all accounts by cosine similarity to a reference "ideal customer profile" vector.

Implement a simple linear scoring model: define a weight vector (one weight per feature), compute dot products against every account vector, and sort by score — this is mechanically identical to what a logistic regression does before the sigmoid.

Reduce a high-dimensional account dataset to 2D using a manual implementation of power iteration for PCA (two eigenvectors only), then plot the result to see natural account clusters without any ML library.

## Ship It

Package the similarity and scoring functions into a CLI tool that reads a CSV of accounts, accepts a reference account ID, and outputs the top-N most similar accounts with similarity scores.

Write the output as a markdown table suitable for piping into a sales Slack channel or account planning doc.

Add a `--method` flag that lets the user choose between `dot`, `cosine`, and `euclidean`, and document when each is appropriate in the `--help` text.

## Exercises

**Easy:** Given five 3-dimensional account vectors, compute all pairwise cosine similarities and identify the two most similar accounts by hand, then verify with your code.

**Medium:** Build a weight vector that scores accounts by predicted conversion probability using only your dot product function, then test whether normalizing the features before scoring changes the ranking — explain why.

**Hard:** Implement power iteration to find the first two principal components of a 20-account, 8-feature dataset, project the accounts onto those components, and determine whether the resulting clusters correspond to any known business segment in the data.

## Key Terms

**Vector** — An ordered list of numbers representing a single entity's features; in GTM, one row of your data.

**Dot Product** — The sum of element-wise products between two vectors; measures alignment weighted by magnitude.

**Cosine Similarity** — The dot product normalized by both vector magnitudes; measures directional alignment independent of scale.

**Matrix** — A rectangular grid of numbers; represents either a dataset (rows as entities) or a linear transformation (columns as output basis vectors).

**Principal Component** — The direction of maximum variance in a dataset, found via eigendecomposition of the covariance matrix; used to reduce dimensionality while preserving signal.
