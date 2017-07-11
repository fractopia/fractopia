# fractopia
Little graph network

Project of a network using neo4j, mostly for learning purpose.

The main idea is the user interacts with one or more actors, which by its turn interacts with the database through extensions. All is stored in the database in "Fracti" nodes. Basic fracti types include Content, and Directories, which allows organization of other nodes "inside".


Next in line:

* Clean code
* BasicFractopus - Basic basic CRUD functionalities, tagging and basic social functionalites like sharing, posting and creates a "inbox directory" to receive from other actors .
* Keyring - Manage fracti read/write permissions
* Saver - Save copies of fractis
* Feedtopus - Importing external RSS feeds to the graph or creating internal feed creators based on specifc searches.
* Web Interface - Probally flask, managing basic inputs and some default views (forum like view for nodes marked as forum, and blogs, etc)
* Graph interface - Vizualize and interact with the network directly in graph form, probaly with D3.js.
