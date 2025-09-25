# API Contract: Sales Recommendations

**Endpoint**: `/api/v1/recommendations`  
**Purpose**: Generate personalized sales content using integrated knowledge sources  
**Authentication**: API Key required

## POST /api/v1/recommendations/generate

Generate sales recommendations based on customer context and knowledge base.

### Request
```http
POST /api/v1/recommendations/generate
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "customer_profile": {
    "id": "customer-uuid-123",
    "personality_type": "D",
    "communication_style": "direct",
    "decision_factors": ["performance", "safety", "value"],
    "budget_range": "40k_60k"
  },
  "sales_context": {
    "product_interest": "2024 Toyota Camry Hybrid",
    "sales_stage": "presentation",
    "customer_concerns": ["fuel_costs", "reliability", "resale_value"],
    "context_description": "Professional couple, age 35, looking for reliable commuter car. Concerned about long-term costs and environmental impact.",
    "competitive_alternatives": ["Honda Accord Hybrid", "Nissan Altima"]
  },
  "output_preferences": {
    "format": "email|bullet|script|presentation",
    "tone": "professional|conversational|consultative",
    "length": "brief|detailed|comprehensive",
    "include_sources": true
  }
}
```

### Response Success (200 OK)
```json
{
  "id": "recommendation-uuid-456",
  "recommendation_text": "Based on your priorities of performance, safety, and value, the 2024 Toyota Camry Hybrid offers compelling advantages...",
  "output_format": "email",
  "confidence_score": 0.87,
  "generation_metadata": {
    "processing_time": "1.2s",
    "tokens_used": 1247,
    "model_used": "gpt-3.5-turbo"
  },
  "applied_principles": {
    "psychological": [
      {
        "principle": "Social Proof",
        "application": "Mentioned Camry's #1 selling status in mid-size sedan category",
        "source_reference": "The Psychology of Selling, Chapter 4"
      }
    ],
    "technical": [
      {
        "feature": "Safety Rating",
        "value_proposition": "IIHS Top Safety Pick+ award provides peace of mind for family protection",
        "source_reference": "2024 Camry Technical Specifications, Safety Section"
      }
    ],
    "communication": [
      {
        "technique": "Problem-Solution Framework",
        "application": "Structured response addressing each stated concern",
        "source_reference": "Professional Writing Guide, Chapter 7"
      }
    ]
  },
  "source_attribution": [
    {
      "source_id": "source-uuid-1",
      "source_title": "The Psychology of Selling",
      "concepts_used": ["social_proof", "value_demonstration"],
      "confidence": 0.92
    }
  ],
  "suggested_follow_up": [
    "Schedule test drive to demonstrate fuel efficiency",
    "Provide total cost of ownership comparison vs competitors",
    "Share customer testimonials from similar professional couples"
  ]
}
```

### Response Error (400 Bad Request)
```json
{
  "error": "insufficient_context",
  "message": "Customer context too vague to generate meaningful recommendations",
  "details": {
    "missing_fields": ["customer_concerns", "context_description"],
    "suggestions": [
      "Provide specific customer concerns or objections",
      "Include more detailed situation description"
    ]
  }
}
```

## POST /api/v1/recommendations/objection-handling

Generate responses to specific customer objections.

### Request
```http
POST /api/v1/recommendations/objection-handling
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "customer_profile_id": "customer-uuid-123",
  "product_context": "2024 Toyota Camry Hybrid",
  "objection": {
    "type": "price",
    "statement": "This car is too expensive compared to the Honda Accord",
    "context": "Customer comparing $32k Camry vs $28k Accord base models"
  },
  "response_style": "consultative",
  "include_competitive_analysis": true
}
```

### Response Success (200 OK)
```json
{
  "objection_responses": [
    {
      "strategy": "Value Reframing",
      "response": "I understand price is important. Let's look at the total value equation...",
      "psychological_basis": "Anchoring and value demonstration",
      "supporting_evidence": [
        "Toyota's superior resale value (+$3,200 after 5 years)",
        "Lower maintenance costs (Toyota Care included)",
        "Better fuel economy saves $400/year"
      ]
    }
  ],
  "competitive_analysis": {
    "total_cost_5_years": {
      "camry": "$41,200",
      "accord": "$42,800"
    },
    "key_advantages": ["reliability", "resale_value", "fuel_efficiency"]
  },
  "recommended_next_steps": [
    "Show 5-year cost comparison calculator",
    "Highlight unique Camry features not available on Accord",
    "Offer test drive to demonstrate value proposition"
  ]
}
```

## GET /api/v1/recommendations/{id}

Retrieve a previously generated recommendation.

### Response Success (200 OK)
```json
{
  "id": "recommendation-uuid-456",
  "recommendation_text": "...",
  "created_at": "2025-09-24T10:30:00Z",
  "customer_context": {
    "customer_id": "customer-uuid-123",
    "product_interest": "2024 Toyota Camry Hybrid"
  },
  "usage_analytics": {
    "views": 3,
    "last_accessed": "2025-09-24T14:22:00Z"
  }
}
```

## POST /api/v1/recommendations/{id}/feedback

Submit feedback on recommendation effectiveness.

### Request
```http
POST /api/v1/recommendations/recommendation-uuid-456/feedback
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "interaction_outcome": "interested",
  "customer_response": "Customer was impressed with the safety features and fuel economy data",
  "salesperson_notes": "The social proof examples really resonated. Customer asked for test drive.",
  "effectiveness_rating": 4,
  "techniques_that_worked": ["social_proof", "technical_specifications", "cost_analysis"],
  "techniques_that_failed": [],
  "follow_up_scheduled": true,
  "additional_notes": "Customer wants to bring spouse for test drive next week"
}
```

### Response Success (201 Created)
```json
{
  "feedback_id": "feedback-uuid-789",
  "recommendation_id": "recommendation-uuid-456",
  "recorded_at": "2025-09-24T15:30:00Z",
  "learning_impact": {
    "concepts_reinforced": ["social_proof_effectiveness", "technical_focus"],
    "model_updates": "Feedback incorporated into learning system"
  }
}
```

## GET /api/v1/recommendations/analytics

Get recommendation effectiveness analytics.

### Request
```http
GET /api/v1/recommendations/analytics?period=30d&group_by=customer_type&format=summary
Authorization: Bearer <api_key>
```

### Response Success (200 OK)
```json
{
  "period": "2025-08-25 to 2025-09-24",
  "summary": {
    "total_recommendations": 847,
    "average_effectiveness": 3.8,
    "success_rate": 0.74,
    "most_effective_techniques": ["social_proof", "technical_specs", "value_analysis"]
  },
  "by_customer_type": [
    {
      "personality_type": "D",
      "recommendation_count": 203,
      "average_effectiveness": 4.1,
      "top_techniques": ["direct_benefits", "competitive_advantage", "performance_data"]
    }
  ],
  "knowledge_source_performance": [
    {
      "source": "The Psychology of Selling",
      "usage_frequency": 0.89,
      "effectiveness_score": 4.2,
      "top_concepts": ["social_proof", "reciprocity", "commitment"]
    }
  ]
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "error_code",
  "message": "Human-readable error description", 
  "details": {
    "additional_context": "value"
  },
  "timestamp": "2025-09-24T10:30:00Z",
  "request_id": "req-uuid"
}
```

### Common Error Codes
- `insufficient_context`: Not enough customer/sales context provided
- `knowledge_unavailable`: Required knowledge sources not processed
- `generation_failed`: AI service unavailable or failed
- `invalid_customer_profile`: Customer profile data validation failed
- `recommendation_not_found`: Recommendation ID doesn't exist
- `feedback_already_submitted`: Feedback already exists for this recommendation

## Rate Limiting

- **Generation Requests**: 100 per hour per API key (due to AI processing costs)
- **Retrieval Operations**: 1000 per hour per API key
- **Analytics Requests**: 50 per hour per API key

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73  
X-RateLimit-Reset: 1695559200
X-AI-Tokens-Used: 15847
X-AI-Tokens-Limit: 50000
```