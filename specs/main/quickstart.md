# Quickstart Guide: Sales Assistant API

**Feature**: Core Knowledge Ingestion & Sales Content Generation  
**Target Audience**: Sales teams, developers integrating Sales Assistant functionality  
**Estimated Time**: 30 minutes for basic setup, 2 hours for full integration

## Prerequisites

- API key from Sales Assistant platform
- Python 3.11+ or equivalent HTTP client
- Sample knowledge sources (books, manuals, specifications)
- Basic understanding of REST APIs

## Quick Start (15 minutes)

### Step 1: Authentication Setup

Obtain your API key and test connectivity:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.salesassistant.com/v1/knowledge/sources"
```

Expected response: `{"sources": [], "total_count": 0}`

### Step 2: Upload Your First Knowledge Source

Upload a sales psychology book or car specification document:

```bash
curl -X POST "https://api.salesassistant.com/v1/knowledge/sources" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -F "file=@psychology_of_selling.pdf" \
     -F "title=The Psychology of Selling" \
     -F "author=Brian Tracy" \
     -F "type=psychology"
```

Expected response includes processing status. Wait 5-10 minutes for processing to complete.

### Step 3: Create a Customer Profile

Create a sample customer to test recommendations:

```bash
curl -X POST "https://api.salesassistant.com/v1/customers" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Customer",
       "personality_assessment": {"type": "D"},
       "decision_factors": {"primary": ["performance", "safety", "value"]},
       "buying_context": {"budget_range": "40k_60k"}
     }'
```

Save the returned `customer_id` for the next step.

### Step 4: Generate Your First Recommendation

Generate sales content using the uploaded knowledge and customer profile:

```bash
curl -X POST "https://api.salesassistant.com/v1/recommendations/generate" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_profile": {"id": "YOUR_CUSTOMER_ID", "personality_type": "D"},
       "sales_context": {
         "product_interest": "Toyota Camry",
         "sales_stage": "presentation", 
         "customer_concerns": ["price", "reliability"],
         "context_description": "Professional looking for reliable commuter car"
       },
       "output_preferences": {"format": "email", "include_sources": true}
     }'
```

You should receive personalized sales content with source attribution!

## Complete Integration (2 hours)

### Comprehensive Knowledge Base Setup

**Upload Multiple Knowledge Sources:**

1. **Sales Psychology Book** (e.g., "The Psychology of Selling")
   - Type: `psychology`
   - Focus: Persuasion techniques, objection handling, customer psychology

2. **Technical Specifications** (e.g., Car manufacturer's technical manual)
   - Type: `technical` 
   - Focus: Product features, specifications, competitive advantages

3. **Communication Guide** (e.g., "Made to Stick" or professional writing guide)
   - Type: `communication`
   - Focus: Clear communication, storytelling, presentation techniques

**Monitor Processing Status:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.salesassistant.com/v1/knowledge/sources"
```

Wait for all sources to show `"processing_status": "processed"`

### Customer Profile Development

**Create Detailed Customer Profiles:**

```json
{
  "name": "Professional Customer",
  "demographics": {
    "age": 35,
    "profession": "Engineer",
    "location": "Seattle, WA"
  },
  "personality_assessment": {
    "type": "D",
    "confidence": 0.85
  },
  "communication_preferences": {
    "style": "direct",
    "preferred_channels": ["email"]
  },
  "decision_factors": {
    "primary": ["performance", "safety", "value"],
    "secondary": ["fuel_efficiency", "technology"],
    "deal_breakers": ["poor_reliability"]
  },
  "buying_context": {
    "budget_range": "45k_65k",
    "timeline": "within_2_months",
    "trade_in_vehicle": "2019 Honda Civic"
  }
}
```

**Test Different Personality Types:**
- **D (Dominant)**: Direct, results-focused - test with performance/efficiency focus
- **I (Influential)**: Social, optimistic - test with social proof and testimonials  
- **S (Steady)**: Patient, reliable - test with safety and family benefits
- **C (Conscientious)**: Analytical, precise - test with detailed specifications

### Advanced Recommendation Scenarios

**Test Various Sales Contexts:**

1. **Early Stage Prospecting:**
```json
{
  "sales_stage": "prospecting",
  "context_description": "Initial contact, customer researching options",
  "output_preferences": {"format": "email", "tone": "consultative"}
}
```

2. **Presentation Stage:**
```json
{
  "sales_stage": "presentation", 
  "context_description": "Customer visiting showroom, comparing models",
  "output_preferences": {"format": "bullet", "length": "comprehensive"}
}
```

3. **Objection Handling:**
```json
{
  "sales_context": {
    "sales_stage": "negotiation",
    "customer_concerns": ["price", "monthly_payment", "insurance_costs"]
  }
}
```

### Feedback Loop Implementation

**Record Interaction Outcomes:**
```bash
curl -X POST "https://api.salesassistant.com/v1/recommendations/RECOMMENDATION_ID/feedback" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -d '{
       "interaction_outcome": "interested",
       "effectiveness_rating": 4,
       "techniques_that_worked": ["social_proof", "technical_specs"],
       "customer_response": "Impressed with safety ratings"
     }'
```

## Integration Examples

### Python Integration

```python
import requests
import json

class SalesAssistant:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.salesassistant.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_recommendation(self, customer_id, context):
        endpoint = f"{self.base_url}/recommendations/generate"
        payload = {
            "customer_profile": {"id": customer_id},
            "sales_context": context,
            "output_preferences": {"format": "email", "include_sources": True}
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()
    
    def record_feedback(self, recommendation_id, outcome, rating):
        endpoint = f"{self.base_url}/recommendations/{recommendation_id}/feedback"
        payload = {
            "interaction_outcome": outcome,
            "effectiveness_rating": rating
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()

# Usage Example
assistant = SalesAssistant("your-api-key")

recommendation = assistant.generate_recommendation(
    customer_id="customer-123",
    context={
        "product_interest": "Toyota Camry Hybrid",
        "sales_stage": "presentation",
        "customer_concerns": ["fuel_costs", "reliability"],
        "context_description": "Eco-conscious professional, daily commuter"
    }
)

print(f"Generated recommendation: {recommendation['recommendation_text']}")
print(f"Confidence: {recommendation['confidence_score']}")
```

### CLI Integration

```bash
#!/bin/bash

# Generate recommendation and save to file
generate_sales_content() {
    local customer_id=$1
    local product=$2
    local concerns=$3
    
    curl -X POST "https://api.salesassistant.com/v1/recommendations/generate" \
         -H "Authorization: Bearer $SALES_API_KEY" \
         -H "Content-Type: application/json" \
         -d "{
           \"customer_profile\": {\"id\": \"$customer_id\"},
           \"sales_context\": {
             \"product_interest\": \"$product\",
             \"customer_concerns\": [$concerns],
             \"sales_stage\": \"presentation\"
           }
         }" > recommendation.json
    
    echo "Recommendation saved to recommendation.json"
}

# Usage
generate_sales_content "customer-123" "Toyota Camry" "\"price\", \"reliability\""
```

## Testing Scenarios

### Scenario 1: Price-Sensitive Customer
- **Profile**: Budget-conscious, analytical personality (C type)
- **Context**: Comparing multiple vehicles, concerned about total cost of ownership
- **Expected Output**: Value-focused content with cost comparisons and long-term savings

### Scenario 2: Safety-Focused Family
- **Profile**: Parents with young children, steady personality (S type)  
- **Context**: Primary concern is family safety, interested in SUVs
- **Expected Output**: Safety-focused content with emotional appeal and family testimonials

### Scenario 3: Performance Enthusiast  
- **Profile**: Car enthusiast, dominant personality (D type)
- **Context**: Interested in sports cars, values performance over efficiency
- **Expected Output**: Performance-focused content with technical specifications and competitive comparisons

### Scenario 4: Eco-Conscious Professional
- **Profile**: Environmentally aware, influential personality (I type)
- **Context**: Wants hybrid/electric vehicle, concerned about environmental impact
- **Expected Output**: Environmental benefits, social responsibility angle, technology features

## Troubleshooting

### Common Issues

**1. "Insufficient Context" Error**
- **Cause**: Customer context too vague
- **Solution**: Provide more detailed situation description and specific concerns

**2. "Knowledge Unavailable" Error**  
- **Cause**: Knowledge sources not yet processed
- **Solution**: Check processing status, wait for completion

**3. "Low Confidence Score" (<0.6)**
- **Cause**: Unclear customer profile or unusual request
- **Solution**: Refine customer profile, provide more specific context

**4. Rate Limit Exceeded**
- **Cause**: Too many API requests
- **Solution**: Implement request throttling, cache responses when possible

### Support and Documentation

- **API Reference**: [api.salesassistant.com/docs](https://api.salesassistant.com/docs)
- **Support Email**: support@salesassistant.com  
- **Status Page**: [status.salesassistant.com](https://status.salesassistant.com)

---

**Next Steps:**
- Explore analytics endpoints for recommendation effectiveness tracking
- Implement A/B testing with different recommendation approaches  
- Set up automated feedback collection from your CRM system
- Scale knowledge base with additional industry-specific sources