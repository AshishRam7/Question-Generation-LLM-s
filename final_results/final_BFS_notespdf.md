# Lecture 13: Graphs I: Breadth First Search

### Lecture Overview

- Applications of Graph Search
- Graph Representations
- Breadth-First Search

#### Recall:

Graph G = (V, E)

- V = set of vertices (arbitrary labels)
- E = set of edges i.e. vertex pairs (v, w)
	- ordered pair =⇒ directed edge of graph
	- unordered pair =⇒ undirected

### Figure 1: Example to illustrate graph terminology

#### Figure Description:
 The figure illustrates the concept of directed graphs using a directed graph with labeled vertices and edges. The edges are represented by arrows, and the vertices are labeled with letters. The graph is undirected, meaning there are no edges pointing from one vertex to another. The number of vertices (a, b, c, d) is equal to the number of edges (4). The number of incoming edges (a, b, c) is equal to the number of outgoing edges (2). The number of outgoing edges (a, b, c) is equal to the number of incoming edges (2). The number of incoming edges (a, b, c) is equal to the number of outgoing edges (2).


### Graph Search

"Explore a graph", e.g.:

- find a path from start vertex s to a desired vertex
- visit all vertices or edges of graph, or only those reachable from s

## Applications:

There are many.

- web crawling (how Google finds pages)
- social networking (Facebook friend finder)
- network broadcast routing
- garbage collection
- model checking (finite state machine)
- checking mathematical conjectures
- solving puzzles and games

#### Pocket Cube:

Consider a 2 2 2 Rubik's cube × ×

### 

#### Figure Description:
 The cube is composed of six smaller cubes, each with a distinct color and orientation. The colors are arranged in a grid pattern, with each row and column alternating between red, orange, green, and purple. The numbers 1, 2, 3, 4, 5, 6 are visible on the faces of the cubes, indicating the order of the colors. This arrangement suggests a systematic approach to color coding or categorization.


Configuration Graph:

- vertex for each possible state
- edge for each basic move (e.g., 90 degree turn) from one state to another
- undirected: moves are reversible

Diameter ("God's Number")

11 for 2 × 2 × 2, 20 for 3 × 3 × 3, Θ(n 2/ lg n) for n × n × n [Demaine, Demaine, Eisenstat Lubiw Winslow 2011]

### 

#### Figure Description:
 The figure illustrates a hierarchical clustering process, where a solution is initially identified as 'solved' and then expanded into a network of possible solutions. The 'breadth-first' approach is employed, meaning solutions are explored in order of increasing depth. The 'hardest configs' are identified as the first solution, and the 'breadth-first' tree' is created as the second solution. The 'reachable in two steps' is noted as a key feature of the process, suggesting a possible optimization approach. The 'possible first moves' are highlighted as a key element of the process, indicating the potential for further exploration.


# vertices = 8! · 3 8 = 264, 539, 520 where 8! comes from having 8 cubelets in arbitrary positions and 38 comes as each cubelet has 3 possible twists.

### 

#### Figure Description:
 The visualization demonstrates a 3D cube with a green cube at the center, surrounded by a red cube and a purple cube. The red cube is partially contained within the green cube, and the purple cube is partially contained within the red cube. The green cube appears to be the largest of the three, occupying roughly one-third of the cube's volume. The red cube is slightly smaller than the green cube, and the purple cube is slightly smaller than the red cube. The red cube has a smaller area than the green cube, and the purple cube has a smaller area than the red cube. The green cube has a smaller area than the red cube, and the purple cube has a smaller area than the red cube.


This can be divided by 24 if we remove cube symmetries and further divided by 3 to account for actually reachable configurations (there are 3 connected components).

### Graph Representations: (data structures)

### Adjacency lists:

Array Adj of |V | linked lists

- for each vertex u ∈ V, Adj[u] stores u's neighbors, i.e., {v ∈ V | (u, v) ∈ E}. (u, v) are just outgoing edges if directed. (See [Fig. 2](#page-2-0) for an example.)
### 

#### Figure Description:
 The diagram illustrates a directed graph with a central node labeled 'a' connected to three nodes labeled 'b', 'c', and 'd'.  The graph is directed towards node 'a' by edges labeled 'a', 'b', and 'c'.  The graph is also directed towards node 'd' by edges labeled 'd', 'c', and 'a'.  The graph is a directed graph with a central node and three outgoing edges.


<span id="page-2-0"></span>Figure 2: Adjacency List Representation: Space Θ(V + E)

- in Python: Adj = dictionary of list/set values; vertex = any hashable object (e.g., int, tuple)
- advantage: multiple graphs on same vertices

### Implicit Graphs:

Adj(u) is a function — compute local structure on the fly (e.g., Rubik's Cube). This requires "Zero" Space.

#### Object-oriented Variations:

- object for each vertex u
- u.neighbors = list of neighbors i.e. Adj[u]

In other words, this is method for implicit graphs

#### Incidence Lists:

- can also make edges objects
### 

#### Figure Description:
 The diagram illustrates a directed graph, where each node is connected to one or more other nodes. The edges are represented by blue arrows, and the nodes are labeled with letters. The graph is symmetric, with an even number of incoming and outgoing edges. The number of nodes is equal to the number of outgoing edges.


- u.edges = list of (outgoing) edges from u.
- advantage: store edge data without hashing

### Breadth-First Search

Explore graph level by level from s

- level 0 = {s}
- level i = vertices reachable by path of i edges but not fewer

### Figure 3: Illustrating Breadth-First Search

#### Figure Description:
 Figure 3 presents a visual representation of a Breadth-First Search algorithm implemented in natural language. The graph illustrates the search process, starting at the 's' node and traversing upwards to nodes labeled 'level1', 'level2', and 'last level'. The algorithm explores connections between nodes, represented by blue dots, and employs a depth-first search approach. The graph highlights the increasing number of connections as the search progresses, starting with level1 and ending with 'last level'. The number of nodes in the graph is represented by the number of blue dots, with 's' having the fewest connections. This visualization provides a clear understanding of the Breadth-First Search algorithm's structure and its approach to exploring connections between nodes.


- build level i > 0 from level i − 1 by trying all outgoing edges, but ignoring vertices from previous levels
#### Breadth-First-Search Algorithm

BFS (V,Adj,s): See CLRS for queue-based implementation level = { s: 0 } parent = {s : None } i = 1 frontier = [s] # previous level, i − 1 while frontier: next = [ ] # next level, i for u in frontier: for v in Adj [u]: if v not in level: # not yet seen level[v] = i ] = level[u] + 1 parent[v] = u next.append(v) frontier = next i + =1

#### Example

### Figure 4: Breadth-First Search Frontier

#### Figure Description:
 Figure 4 presents a Breadth-First Search Frontier algorithm implemented in natural language. The graph is a directed graph with nodes labeled 'a', 's', 'd', 'f', 'z', 'x', 'c', and 'v'.  The nodes are connected by edges labeled 'a-x', 's-x', 'd-z', 'f-z', 'z-c', 'x-c', and 'c-v'. The graph is depicted with a red dashed line and blue circles representing nodes. The number of nodes (a, s, d, f, z, x, c, v) is shown as 1, 2, 3, 4, 5, 6, 7. The edges are labeled with numbers indicating the depth of the path from the source node to the destination node. The number of paths from 'a' to 'v' is 7. The number of paths from 's' to 'd' is 7. The number of paths from 'd' to 'f' is 7. The number of paths from 'f' to 'v' is 7. The number of paths from 'z' to 'x' is 7. The number of paths from 'x' to 'c' is 7. The number of paths from 'c' to 'v' is 7. The number of paths from 'z' to 'v' is 7. The number of paths from 'a' to 'v' is 7. The number of paths from 's' to 'd' is 7. The number of paths from 'd' to 'f' is 7. The number of paths from 'f' to 'v' is 7. The number of paths from 'z' to 'v' is 7. The number of paths from 'a' to 'v' is 7. The number of paths from 's' to 'd' is 7. The number of paths from 'd' to 'f' is 7. The number of paths from 'f' to 'v' is 7. The number of paths from 'z' to 'v' is 7. The number of paths from 'a' to 'v' is 7. The number of paths from 's' to 'd' is 7. The number of paths from 'd' to 'f' is 7. The number of paths from 'f' to 'v' is 7. The number of paths from 'z' to 'v' is 7


#### Analysis:

- vertex V enters next (& then frontier) only once (because level[v] then set)
base case: v = s

- =⇒ Adj[v] looped through only once

$$\text{time } = \sum_{v \in V} |Adj[V]| = \begin{cases} |E| \text{ for directed graphs} \\ 2|E| \text{ for undirected graphs} \end{cases}$$

- O(V + E) ("LINEAR TIME") to also list vertices unreachable from v (those still not assigned level)
#### Shortest Paths:

#### cf. L15-18

- for every vertex v, fewest edges to get from s to v is
( level[v] if v assigned level ∞ else (no path)

- parent pointers form shortest-path tree = union of such a shortest path for each v =⇒ to find shortest path, take v, parent[v], parent[parent[v]], etc., until s (or None)
<sup>•</sup> =⇒ O(E) time

MIT OpenCourseWare <http://ocw.mit.edu>

6.006 Introduction to Algorithms Fall 2011

For information about citing these materials or our Terms of Use, visit:<http://ocw.mit.edu/terms>.