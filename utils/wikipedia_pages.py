import requests
from fuzzywuzzy import fuzz
import spacy
import wikipedia

# Load spaCy's model
nlp = spacy.load("en_core_web_sm")

def is_claim_semantically_supported(claim, page_content):
    """Calculate semantic similarity between the claim and the Wikipedia page content."""
    claim_doc = nlp(claim)
    page_doc = nlp(page_content)
    
    # Calculate similarity score based on semantics
    similarity = claim_doc.similarity(page_doc)
    return similarity > 0.7  # You can adjust the threshold based on experimentation

def contains_negation(claim):
    """Check if the claim contains negation words."""
    negation_words = ["not", "no", "never", "none", "n't"]
    return any(negation_word in claim.lower() for negation_word in negation_words)

def search_wikipedia(query):
    """Search Wikipedia using the Wikipedia API."""
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        search_results = data.get("query", {}).get("search", [])
        return search_results
    else:
        print("Failed to fetch data from Wikipedia.")
        return []

def get_wikipedia_page_content(page_title):
    """Retrieve the content of a Wikipedia page."""
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles={page_title}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        page_content = next(iter(data['query']['pages'].values())).get('extract', '')
        return page_content
    else:
        print("Failed to retrieve page content.")
        return ''

def is_claim_supported(claim, page_content):
    """Compare the similarity between the claim and the page content using fuzzy matching."""
    similarity = fuzz.token_set_ratio(claim, page_content)
    return similarity > 70  # You can adjust the threshold

def verify_claim_with_negation(claim, page_content):
    """Verify the claim considering possible negation."""
    negation_present = contains_negation(claim)
    
    # Perform semantic analysis of the claim and the content
    if negation_present:
        # Invert the meaning by checking if the content supports the opposite claim
        opposite_claim = claim.replace("not", "").replace("no", "").strip()
        if is_claim_semantically_supported(opposite_claim, page_content):
            return "Incorrect and Verified"
    else:
        # Regular semantic analysis for claims without negation
        if is_claim_semantically_supported(claim, page_content):
            return "Verified"
    
    return "Not Verified"

def verify_claim_across_multiple_pages(claim, search_results):
    """Verify the claim against multiple Wikipedia pages."""
    for result in search_results[:3]:  # Limit to top 3 results for efficiency
        page_title = result['title']
        page_content = get_wikipedia_page_content(page_title)
        
        verification_result = verify_claim_with_negation(claim, page_content)
        if verification_result != "Not Verified":
            return f"The claim '{claim}' is {verification_result} by Wikipedia page: {page_title}."
    
    return f"The claim '{claim}' could not be verified by any Wikipedia pages."

def fetch_sections(page_title):
    try:
        page = wikipedia.page(page_title)
        content = page.content
        return content.split('\n\n')  # Split content into sections based on paragraphs
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple entries found for {page_title}: {e.options}"
    except wikipedia.exceptions.PageError:
        return f"Page not found for {page_title}"

