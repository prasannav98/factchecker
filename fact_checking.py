import spacy
from sentence_transformers import SentenceTransformer, util
import wikipedia_pages

# Load the NLP models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def verify_claim_across_multiple_pages(claim, search_results):
    for result in search_results[:3]:  # Limit to top 3 results for efficiency
        page_title = result['title']
        page_content = wikipedia_pages.get_wikipedia_page_content(page_title)
        
        if wikipedia_pages.verify_claim_with_negation(claim, page_content):
            return True
    
    return False

def fact_check_system(user_claim):

    # Search Wikipedia for relevant content
    search_results = wikipedia_pages.search_wikipedia(user_claim)
    if search_results:
        output = ""
        result = verify_claim_across_multiple_pages(user_claim, search_results)

        # Display the result
        if result:
            output = (f"The claim '{user_claim}' is supported by Wikipedia.")
        else:
            output = (f"The claim '{user_claim}' could not be verified.")

        return output

def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print("Extracted entities:", entities)  # Debugging output
    return entities

def similarity_score(claim, wikipedia_text):
    claim_embedding = model.encode(claim, convert_to_tensor=True)
    wiki_embedding = model.encode(wikipedia_text, convert_to_tensor=True)
    return util.pytorch_cos_sim(claim_embedding, wiki_embedding).item()

def compute_confidence_score(claim, page_title):
    sections = wikipedia_pages.fetch_sections(page_title)
    if isinstance(sections, str):
        return sections  # Error handling

    print("Fetched sections:", sections)  # Debugging output

    score = 0
    entity_matches = 0
    for section in sections:
        print("Current section:", section)  # Debugging output
        entities = extract_entities(claim)
        for ent, label in entities:
            if ent in section:
                entity_matches += 1
        score += similarity_score(claim, section)

    confidence = (entity_matches * 0.5) + (score / len(sections)) * 0.5
    return f"Confidence Score: {confidence:.2f}"

