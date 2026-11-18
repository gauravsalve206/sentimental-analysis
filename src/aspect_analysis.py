import re

ASPECT_TERMS = {
    "quality": ["quality", "durable", "build", "material", "broken", "defective"],
    "price": ["price", "cost", "expensive", "cheap", "value", "worth"],
    "delivery": ["delivery", "shipping", "arrived", "late", "package arrived", "courier"],
    "packaging": ["packaging", "box", "bottle", "container", "sealed", "wrapping"],
    "battery life": ["battery", "battery life", "charging", "charge lasts"],
    "performance": ["performance", "speed", "fast", "slow", "works", "working"],
    "design": ["design", "look", "looks", "appearance", "style", "color"],
    "customer service": ["customer service", "support", "refund", "return", "replacement"],
}

POSITIVE_TERMS = {
    "excellent", "good", "great", "amazing", "love", "best", "perfect", "works",
    "beautiful", "fast", "easy", "satisfied", "happy", "nice", "recommend", "worth"
}
NEGATIVE_TERMS = {
    "bad", "poor", "terrible", "worst", "broken", "defective", "slow", "late",
    "disappointed", "hate", "difficult", "expensive", "refund", "never", "no"
}


def analyze_aspects(text):
    text_lower = text.lower()
    sentences = re.split(r"[.!?;]+", text_lower)
    output = {}

    for aspect, terms in ASPECT_TERMS.items():
        related = [sentence for sentence in sentences if any(term in sentence for term in terms)]
        if not related:
            continue

        positive = sum(sum(1 for term in POSITIVE_TERMS if term in sentence) for sentence in related)
        negative = sum(sum(1 for term in NEGATIVE_TERMS if term in sentence) for sentence in related)

        if positive > negative:
            sentiment = "Positive"
        elif negative > positive:
            sentiment = "Negative"
        elif positive == negative and positive > 0:
            sentiment = "Neutral"
        else:
            sentiment = "Neutral"

        output[aspect] = {
            "sentiment": sentiment,
            "positive_evidence": positive,
            "negative_evidence": negative,
            "excerpt": ". ".join(related[:2]).strip(),
        }

    return output
