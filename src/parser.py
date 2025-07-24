import re
from src.graph import SemanticGraph, SemanticNode
from src.api_client import FreeDictionaryClient

class Phase1_Parser:
    """
    Parses definitions to build a semantic graph.
    """
    def __init__(self, initial_definition, context_keywords, max_hops=3):
        self.initial_definition = initial_definition
        self.context_keywords = set(context_keywords)
        self.max_hops = max_hops
        self.api_client = FreeDictionaryClient()
        self.graph = SemanticGraph()
        # Common function words to exclude (articles, prepositions, conjunctions, etc.)
        self.stop_words = {
            # Articles
            "a", "an", "the",
            # Common prepositions
            "aboard", "about", "above", "across", "after", "against", "along", "amid", "among", "around",
            "as", "at", "before", "behind", "below", "beneath", "beside", "between", "beyond", "but",
            "by", "concerning", "considering", "despite", "down", "during", "except", "for", "from",
            "in", "inside", "into", "like", "near", "of", "off", "on", "onto", "out", "outside",
            "over", "past", "regarding", "round", "since", "through", "throughout", "to", "toward",
            "under", "underneath", "until", "unto", "up", "upon", "with", "within", "without",
            # Common conjunctions
            "and", "or", "but", "nor", "for", "so", "yet",
            # Other common function words
            "also", "often", "very", "just", "only", "not", "no", "yes", "well", "too"
        }
        self.processed_words = set()
        
        print(f"\n=== ALLA POC: Semantic Graph Construction ===")
        print(f"Initial definition: {initial_definition}")
        print(f"Context keywords: {context_keywords}")
        print(f"Max hops: {max_hops}")
        print(f"Stop words: {self.stop_words}")

    def _extract_words(self, text):
        """Extracts and cleans words from a text string."""
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if word not in self.stop_words]

    def _is_relevant(self, word, definition_text, pos):
        """
        Determines if a word is relevant based on POS and context.
        Uses a more inclusive approach by checking for:
        1. Exact matches in context keywords
        2. Word stems in context keywords
        3. Synonyms or related terms in the definition
        """
        # Skip very short words (1-2 characters) as they're usually not meaningful
        if len(word) <= 2 and word not in self._extract_words(self.initial_definition):
            print(f"    REJECT '{word}': Too short (length <= 2)")
            return False
            
        # First check POS filter - only accept nouns, verbs, and adjectives
        if pos not in ['noun', 'verb', 'adjective']:
            print(f"    REJECT '{word}': POS '{pos}' not in [noun, verb, adjective]")
            return False
        
        # Check if word itself is in context keywords (exact match)
        if word in self.context_keywords:
            print(f"    ACCEPT '{word}': Exact match in context keywords")
            return True
            
        # Check for word stems in context keywords (e.g., 'sleeping' matches 'sleep')
        for keyword in self.context_keywords:
            if (keyword in word or word in keyword) and len(keyword) > 3:  # Only check stems for longer words
                print(f"    ACCEPT '{word}': Stem match with context keyword '{keyword}'")
                return True
        
        # Extract words from definition and check for context keyword matches
        definition_words = set(self._extract_words(definition_text))
        
        # Check for exact matches in definition
        context_overlap = self.context_keywords.intersection(definition_words)
        if context_overlap:
            print(f"    ACCEPT '{word}': Definition contains context words: {context_overlap}")
            return True
            
        # Check for word stems in definition (only for longer words)
        for keyword in self.context_keywords:
            if len(keyword) > 3:  # Only check stems for longer words
                if any(keyword in def_word or def_word in keyword for def_word in definition_words if len(def_word) > 3):
                    print(f"    ACCEPT '{word}': Definition contains stem of context keyword '{keyword}'")
                    return True
        
        # For initial words (hop 0), be more lenient
        if word in self._extract_words(self.initial_definition):
            print(f"    ACCEPT '{word}': Part of initial definition")
            return True
            
        # If word is in the definition of a context keyword, include it
        for keyword in self.context_keywords:
            if len(keyword) > 3:  # Only check for longer keywords
                try:
                    keyword_data = self.api_client.get_definition(keyword)
                    if keyword_data:
                        keyword_definition = keyword_data[0]['meanings'][0]['definitions'][0]['definition'].lower()
                        if word in keyword_definition:
                            print(f"    ACCEPT '{word}': Found in definition of context keyword '{keyword}'")
                            return True
                except:
                    continue
            
        print(f"    REJECT '{word}': No strong connection to context")
        return False

    def build_graph(self):
        """Builds the semantic graph recursively."""
        print(f"\n--- Step 1: Extract Initial Words ---")
        initial_words = self._extract_words(self.initial_definition)
        print(f"Initial words extracted: {initial_words}")
        
        queue = [(word, 0) for word in initial_words]
        print(f"Queue initialized with: {queue}")
        
        iteration = 0
        while queue:
            iteration += 1
            word, current_hop = queue.pop(0)
            
            print(f"\n--- Iteration {iteration}: Processing '{word}' (hop {current_hop}) ---")

            if current_hop > self.max_hops:
                print(f"  SKIP '{word}': Exceeds max hops ({current_hop} > {self.max_hops})")
                continue
                
            if word in self.processed_words:
                print(f"  SKIP '{word}': Already processed")
                continue

            self.processed_words.add(word)
            print(f"  PROCESS '{word}' for the first time")
            
            api_data = self.api_client.get_definition(word)
            if not api_data:
                print(f"  ERROR: No API data found for '{word}'")
                continue

            first_meaning = api_data[0]['meanings'][0]
            pos = first_meaning['partOfSpeech']
            definition = first_meaning['definitions'][0]['definition']
            
            try:
                print(f"  DEFINE '{word}' ({pos}): {definition}")
            except UnicodeEncodeError:
                # Handle special characters in output
                safe_def = definition.encode('ascii', 'replace').decode('ascii')
                print(f"  DEFINE '{word}' ({pos}): {safe_def}")
            
            # Check if this word should be added to graph
            if self._is_relevant(word, definition, pos) or current_hop == 0:  # Always add initial words
                current_node = SemanticNode(word, pos, definition)
                if self.graph.get_node(word) is None:
                    self.graph.add_node(current_node)
                    print(f"  ADD NODE: '{word}'")
                else:
                    print(f"  EXISTS: Node '{word}' already exists")
            else:
                print(f"  SKIP: '{word}' not relevant, skipping node creation")
                continue

            definition_words = self._extract_words(definition)
            print(f"  EXTRACT: Words in definition: {definition_words}")
            
            for new_word in definition_words:
                print(f"\n    Examining '{new_word}' from '{word}' definition:")
                
                if new_word in self.processed_words:
                    print(f"      PROCESSED: '{new_word}' already processed")
                    if self.graph.get_node(new_word) and self.graph.get_node(word) and not self.graph.graph.has_edge(word, new_word):
                        self.graph.add_edge(word, new_word)
                        print(f"      ADD EDGE: ({word}, {new_word})")
                    continue

                new_api_data = self.api_client.get_definition(new_word)
                if not new_api_data:
                    print(f"      ERROR: No API data for '{new_word}'")
                    continue
                
                new_first_meaning = new_api_data[0]['meanings'][0]
                new_pos = new_first_meaning['partOfSpeech']
                new_definition_text = new_first_meaning['definitions'][0]['definition']
                
                try:
                    print(f"      DEFINE '{new_word}' ({new_pos}): {new_definition_text[:100]}...")
                except UnicodeEncodeError:
                    safe_word = new_word.encode('ascii', 'replace').decode('ascii')
                    safe_def = new_definition_text.encode('ascii', 'replace').decode('ascii')
                    print(f"      DEFINE '{safe_word}' ({new_pos}): {safe_def[:100]}...")

                if self._is_relevant(new_word, new_definition_text, new_pos):
                    new_node = SemanticNode(new_word, new_pos, new_definition_text)
                    if self.graph.get_node(new_word) is None:
                        self.graph.add_node(new_node)
                        print(f"      ADD NODE: '{new_word}'")
                    
                    if self.graph.get_node(word) and self.graph.get_node(new_word):
                        self.graph.add_edge(word, new_word)
                        print(f"      ADD EDGE: ({word}, {new_word})")
                    
                    if current_hop + 1 <= self.max_hops:
                        queue.append((new_word, current_hop + 1))
                        print(f"      QUEUE: '{new_word}' (hop {current_hop + 1})")

        print(f"\n=== Graph Construction Complete ===")
        print(f"Total nodes: {len(self.graph.graph.nodes)}")
        print(f"Total edges: {len(self.graph.graph.edges)}")
        print(f"Nodes: {list(self.graph.graph.nodes)}")
        print(f"Edges: {list(self.graph.graph.edges)}")
        
        return self.graph