# Lecture 13: Graphs I – Breadth-First Search 

## Lecture Overview

- Applications of Graph Search
- Graph Representations
- Breadth-First Search

## Recall:

Graph \(G=(V, E)\)

- \(V=\) set of vertices (arbitrary labels)
- \(E=\) set of edges i.e. vertex pairs \((v, w)\)
- ordered pair \(⟹\) directed edge of graph
- unordered pair \(⟹\) undirected

**Image Description:**  The figure illustrates a directed graph with a directed edge from 'a' to 'b' and 'c'. The edges have labels 'V' and 'E'. The graph is labeled 'undirected' and 'directed'. The directed graph has a cycle of nodes 'a', 'b', and 'c'. The directed graph has a cycle of nodes 'a', 'b', and 'c'. The undirected graph has a cycle of nodes 'a', 'b', and 'c'. The directed graph has a cycle of nodes 'a', 'b', and 'c'. The undirected graph has a cycle of nodes 'a', 'b', and 'c'. The directed graph has a cycle of nodes 'a', 'b', and 'c'. The undirected graph has a cycle of nodes 'a', 'b', and 'c'.

Figure 1: Example to illustrate graph terminology

## Graph Search

"Explore a graph", e.g.:

- find a path from start vertex \(s\) to a desired vertex
- visit all vertices or edges of graph, or only those reachable from \(s\)

# Applications: 

There are many.

- web crawling (how Google finds pages)
- social networking (Facebook friend finder)
- network broadcast routing
- garbage collection
- model checking (finite state machine)
- checking mathematical conjectures
- solving puzzles and games

## Pocket Cube:

Consider a \(2 × 2 × 2\) Rubik's cube

**Image Description:**  The cube exhibits a 3D structure with a regular pattern of color blocks. Each block is a distinct shade of orange, yellow, green, and purple. The colors are arranged in a symmetrical fashion, creating a visually appealing and balanced composition. The number of blocks in each color group is consistent, suggesting a systematic approach to color arrangement. The cube appears to be a 3D model or visualization, possibly used for educational purposes or as a visual aid.

Configuration Graph:

- vertex for each possible state
- edge for each basic move (e.g., 90 degree turn) from one state to another
- undirected: moves are reversible

Diameter ("God's Number")
11 for \(2 × 2 × 2,20\) for \(3 × 3 × 3, Θ(n^2 /  n)\) for \(n × n × n\) [Demaine, Demaine, Eisenstat Lubiw Winslow 2011]

**Image Description:**  The figure illustrates a hierarchical clustering process, where a solution is initially identified as 'solved' and then expanded into a 'breadth-first' search. The 'breadth-first' approach is then evaluated for 'hardest configurations', and finally 'first tree' is selected. The number of nodes in each level of the hierarchy is represented by the number of circles, with the number of nodes in the 'breadth-first' and 'first tree' levels represented by three circles. The 'solved' solution is reached after two steps, while the 'breadth-first' solution is reached after three steps.

\# vertices \(=8! 3^8=264,539,520\) where 8 ! comes from having 8 cubelets in arbitrary positions and \(3^8\) comes as each cubelet has 3 possible twists.

**Image Description:**  The visualization demonstrates a 3D cube with a green cube at its center, surrounded by a red cube and a purple cube. The red cube appears to be partially overlapping the green cube. The purple cube is positioned slightly offset from the center of the green cube. The green cube occupies approximately one-third of the cube's volume. The red cube and purple cube appear to be uniformly sized and positioned. The purple cube has a smaller diameter than the red cube. The green cube has a smaller height than the red cube. The red cube has a smaller width than the purple cube. The purple cube has a smaller depth than the red cube. The green cube has a smaller height than the red cube. The red cube has a smaller width than the purple cube. The purple cube has a smaller depth than the red cube.

This can be divided by 24 if we remove cube symmetries and further divided by 3 to account for actually reachable configurations (there are 3 connected components).

# Graph Representations: (data structures) 

## Adjacency lists:

Array \(Adj\) of \(|V|\) linked lists

- for each vertex \(u ∈ V, Adj[u]\) stores \(u\) 's neighbors, i.e., \({v ∈ V |(u, v) ∈ E} .  (u, v)\) are just outgoing edges if directed. (See Fig. 2 for an example.)

**Image Description:**  The diagram illustrates a directed graph with a central node 'a' connected to three nodes 'b', 'c', and 'd'.  The graph is labeled with 'a', 'b', 'c', and 'd', and each node is connected to a single other node.  The graph is divided into three sections, each representing a different node 'a', 'b', and 'c'.  Each section is further divided into two sections, 'c' and 'd', representing the connections between the nodes.  The connections between 'a' and 'b' are represented by blue arrows, while the connections between 'a' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c' and 'd' are represented by light blue arrows. The connections between 'b' and 'c' and 'c'

Figure 2: Adjacency List Representation: Space $\Theta(V+E)$

- in Python: \(Adj=\) dictionary of list/set values; vertex \(=\) any hashable object (e.g., int, tuple)
- advantage: multiple graphs on same vertices

## Implicit Graphs:

\(Adj(u)\) is a function - compute local structure on the fly (e.g., Rubik's Cube). This requires "Zero" Space.

# Object-oriented Variations: 

- object for each vertex \(u\)
- \(u\).neighbors \(=\) list of neighbors i.e. \(Adj[u]\)

In other words, this is method for implicit graphs

## Incidence Lists:

- can also make edges objects

**Image Description:**  The figure illustrates a simple network structure.  The top node is labeled 'e.a' and connected to the bottom node labeled 'e'.  The bottom node is labeled 'e.b' and is connected to the top node.  The number of connections between the nodes is 2.  The network appears to be a directed graph, where each node is a node and each connection is an edge.
- $u$.edges $=$ list of (outgoing) edges from $u$.
- advantage: store edge data without hashing

## Breadth-First Search

Explore graph level by level from \(s\)

- level \(0={s}\)
- level \(i=\) vertices reachable by path of \(i\) edges but not fewer

**Image Description:**  The visualization demonstrates a hierarchical neural network structure.  It shows two levels of neurons, labeled 'level1' and 'level2', connected by blue lines.  Each level has a single input neuron and multiple output neurons.  The number of input neurons and output neurons in each level is represented by a number.  The last level has three input neurons and three output neurons.  The number of connections between neurons in each level is represented by a number.

Figure 3: Illustrating Breadth-First Search

- build level \(i>0\) from level \(i-1\) by trying all outgoing edges, but ignoring vertices from previous levels

# Breadth-First-Search Algorithm 

```math

\begin{aligned}
& \text { BFS (V,Adj,s): } \\
& \text { level }={\text { s: } 0} \\
& \text { parent }={s: \text { None }} \\
& i=1 \\
& \text { frontier }=[s] \\
& \text { while frontier: } \\
& \text { next }=[] \\
& \text { for } u \text { in frontier: } \\
& \text { for } v \text { in } Adj[u] \text { : } \\
& \text { if } v \text { not in level: } \\
& \text { level }[v]=i \\
& \text { parent }[v]=u \\
& \text { next.append }(v) \\
& \text { frontier }=\text { next } \\
& i+=1
\end{aligned}

```

See CLRS for queue-based implementation

## Example

**Image Description:**  The diagram illustrates a hierarchical structure, likely representing a biological process or system.  Level 1 and Level 2 are connected by a red line, while Level 3 is isolated.  Each level is numbered, and the nodes are labeled with letters.  The connections between nodes are represented by blue lines.  The number of nodes in each level appears to be the same.  The structure suggests a hierarchical organization, with each level potentially representing a different stage or component of a larger system.
frontier $_{n}=\{\mathrm{s}\}$
frontier $_{1}=\{\mathrm{a}, \mathrm{x}\}$
frontier $_{2}=\{\mathrm{z}, \mathrm{d}, \mathrm{c}\}$
frontier $_{3}=\{\mathrm{f}, \mathrm{v}\}$
(not $\mathrm{x}, \mathrm{c}, \mathrm{d})$

Figure 4: Breadth-First Search Frontier

## Analysis:

- vertex \(V\) enters next (\& then frontier) only once (because level \([v]\) then set)
base case: \(v=s\)

- \(⟹ Adj[v]\) looped through only once

```math

\text { time }=∑_v ∈ V|Adj[V]|=\left{\begin{array}{l}
|E| \text { for directed graphs } \\
2|E| \text { for undirected graphs }
\end{array}\right.

```

- \(⟹ O(E)\) time
- \(O(V+E)\) ("LINEAR TIME") to also list vertices unreachable from \(v\) (those still not assigned level)

# Shortest Paths: 

cf. L15-18

- for every vertex \(v\), fewest edges to get from \(s\) to \(v\) is

```math

\left{\begin{array}{l}
\text { level }[v] \text { if } v \text { assigned level } \\
∞   \text { else (no path) }
\end{array}\right.

```

- parent pointers form shortest-path tree \(=\) union of such a shortest path for each \(v\) \(⟹\) to find shortest path, take \(v\), parent \([v]\), parent[parent \([v]]\), etc., until \(s\) (or None)

MIT OpenCourseWare
http://ocw.mit.edu

# 6.006 Introduction to Algorithms 

Fall 2011

For information about citing these materials or our Terms of Use, visit: http://ocw.mit.edu/terms.