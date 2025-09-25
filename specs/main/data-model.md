# Data Model: Core Knowledge Ingestion & Sales Content Generation

**Feature**: Core Knowledge Ingestion & Sales Content Generation  
**Date**: 2025-09-24  
**Phase**: Phase 1 - Design

## Core Entities

### KnowledgeSource
Represents books, manuals, and documents in the system.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier
- `title` (String, Required): Source title (e.g., "The Psychology of Selling")
- `author` (String, Optional): Author name
- `type` (Enum, Required): `psychology`, `technical`, `communication`
- `file_path` (String, Required): Path to original document
- `processed_at` (DateTime, Optional): When content was last processed
- `version` (String, Optional): Source version/edition
- `metadata` (JSON, Optional): Additional source information

**Relationships**:
- Has many `KnowledgeConcepts`
- Has many `SourceReferences` through recommendations

### KnowledgeConcept
Individual concepts, principles, or facts extracted from sources.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier
- `source_id` (UUID, Foreign Key): Reference to KnowledgeSource
- `concept_type` (String, Required): Type categorization (e.g., "persuasion_principle", "safety_feature")
- `title` (String, Required): Concept name (e.g., "Social Proof", "Lane Keep Assist")
- `content` (Text, Required): Full concept description
- `keywords` (Array<String>): Search keywords
- `embedding` (Vector, Optional): Semantic search vector
- `page_reference` (String, Optional): Page/section reference in source
- `confidence_score` (Float, Optional): Extraction quality score

**Relationships**:
- Belongs to `KnowledgeSource`
- Has many `ConceptApplications`

### CustomerProfile
Customer information and preferences for personalization.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier
- `name` (String, Optional): Customer name
- `demographics` (JSON, Optional): Age, profession, location
- `personality_type` (String, Optional): DISC profile (D, I, S, C)
- `communication_style` (String, Optional): Preferred communication approach
- `decision_factors` (Array<String>): Primary purchase influences
- `budget_range` (String, Optional): Budget category
- `previous_interactions` (JSON, Optional): Interaction history summary
- `created_at` (DateTime): Profile creation time
- `updated_at` (DateTime): Last modification time

**Relationships**:
- Has many `SalesInteractions`
- Has many `CustomerPreferences`

### SalesContext
Situation-specific information for generating recommendations.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier
- `customer_id` (UUID, Foreign Key): Associated customer
- `product_interest` (String, Required): Product/vehicle of interest
- `sales_stage` (Enum, Required): `prospecting`, `presentation`, `negotiation`, `closing`
- `customer_concerns` (Array<String>): Expressed concerns or objections
- `context_description` (Text, Required): Detailed situation description
- `urgency_level` (String, Optional): Timeline pressure (low, medium, high)
- `competitive_alternatives` (Array<String>): Other options being considered
- `created_at` (DateTime): Context creation time

**Relationships**:
- Belongs to `CustomerProfile`
- Has many `SalesRecommendations`

### SalesRecommendation
Generated sales talking points and strategies.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier
- `context_id` (UUID, Foreign Key): Associated sales context
- `recommendation_text` (Text, Required): Generated content
- `output_format` (String, Required): Format type (email, bullet, script, presentation)
- `psychological_principles` (Array<String>): Applied psychology concepts
- `technical_features` (Array<String>): Referenced product features
- `communication_techniques` (Array<String>): Applied writing/speaking techniques
- `confidence_score` (Float, Required): Generation confidence (0.0-1.0)
- `generated_at` (DateTime): Creation timestamp
- `token_count` (Integer): API tokens used for generation

**Relationships**:
- Belongs to `SalesContext`
- Has many `SourceReferences`
- Has one `InteractionFeedback` (optional)

### SourceReference
Links recommendations back to knowledge sources for attribution.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier
- `recommendation_id` (UUID, Foreign Key): Associated recommendation
- `source_id` (UUID, Foreign Key): Referenced knowledge source
- `concept_id` (UUID, Foreign Key, Optional): Specific concept referenced
- `reference_type` (String, Required): How source was used (direct_quote, principle_application, supporting_evidence)
- `relevance_score` (Float, Required): How relevant source is to recommendation (0.0-1.0)
- `page_reference` (String, Optional): Specific page/section

**Relationships**:
- Belongs to `SalesRecommendation`
- Belongs to `KnowledgeSource`
- Belongs to `KnowledgeConcept` (optional)

### InteractionFeedback
Captures outcomes and effectiveness of sales interactions.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier
- `recommendation_id` (UUID, Foreign Key): Associated recommendation
- `outcome` (String, Required): Result (interested, neutral, resistant, purchase, no_decision)
- `customer_response` (Text, Optional): Customer's reaction/feedback
- `salesperson_notes` (Text, Optional): Sales rep observations
- `techniques_that_worked` (Array<String>): Effective approaches
- `techniques_that_failed` (Array<String>): Ineffective approaches
- `follow_up_required` (Boolean): Whether follow-up needed
- `effectiveness_rating` (Integer, Required): 1-5 scale rating
- `created_at` (DateTime): Feedback timestamp

**Relationships**:
- Belongs to `SalesRecommendation`

## Entity Relationships Summary

```
KnowledgeSource (1) → (many) KnowledgeConcept
CustomerProfile (1) → (many) SalesContext
SalesContext (1) → (many) SalesRecommendation
SalesRecommendation (1) → (many) SourceReference
SourceReference (many) → (1) KnowledgeSource
SourceReference (many) → (1) KnowledgeConcept
SalesRecommendation (1) → (1) InteractionFeedback [optional]
```

## Database Schema Design

### Indexing Strategy
- **Text Search**: Full-text indexes on `content`, `title`, and `keywords` fields
- **Vector Search**: Vector indexes on `embedding` fields for semantic search
- **Performance**: Indexes on foreign keys and frequently queried fields
- **Analytics**: Composite indexes for reporting and analytics queries

### Partitioning Strategy
- **KnowledgeConcepts**: Partition by `source_id` for large knowledge bases
- **SalesRecommendations**: Partition by `generated_at` date for archival
- **InteractionFeedback**: Partition by `created_at` for time-series analysis

### Data Retention Policy
- **Customer Data**: Retain indefinitely with anonymization options
- **Recommendations**: Archive after 2 years, maintain aggregated analytics
- **Feedback**: Retain all feedback for learning system improvement
- **Knowledge Sources**: Version control with historical preservation

## API Data Transfer Objects (DTOs)

### CustomerProfileDTO
```json
{
  "id": "uuid",
  "name": "string",
  "demographics": {
    "age": "integer",
    "profession": "string",
    "location": "string"
  },
  "personality_type": "D|I|S|C",
  "communication_style": "direct|collaborative|analytical|expressive",
  "decision_factors": ["price", "safety", "performance"],
  "budget_range": "under_25k|25k_40k|40k_60k|above_60k"
}
```

### SalesContextDTO
```json
{
  "customer_id": "uuid",
  "product_interest": "string",
  "sales_stage": "prospecting|presentation|negotiation|closing",
  "customer_concerns": ["price", "reliability", "fuel_economy"],
  "context_description": "string",
  "urgency_level": "low|medium|high",
  "competitive_alternatives": ["Toyota Camry", "Honda Accord"]
}
```

### SalesRecommendationDTO
```json
{
  "id": "uuid",
  "recommendation_text": "string",
  "output_format": "email|bullet|script|presentation",
  "confidence_score": 0.85,
  "source_references": [
    {
      "source_title": "The Psychology of Selling",
      "concept": "Social Proof",
      "page_reference": "Chapter 4, p. 67",
      "relevance_score": 0.92
    }
  ],
  "applied_principles": {
    "psychological": ["social_proof", "authority"],
    "technical": ["safety_rating", "fuel_efficiency"],
    "communication": ["storytelling", "emotional_appeal"]
  }
}
```

### FeedbackDTO
```json
{
  "recommendation_id": "uuid",
  "outcome": "interested|neutral|resistant|purchase|no_decision",
  "customer_response": "string",
  "salesperson_notes": "string",
  "effectiveness_rating": 4,
  "techniques_that_worked": ["social_proof", "technical_specs"],
  "techniques_that_failed": ["urgency_tactics"]
}
```

## Migration Strategy

### Phase 1: Core Tables
1. Create `knowledge_sources` table
2. Create `knowledge_concepts` table with basic text search
3. Create `customer_profiles` table
4. Create basic relationship tables

### Phase 2: Advanced Features
1. Add vector search capabilities to `knowledge_concepts`
2. Create `sales_contexts` and `sales_recommendations` tables
3. Implement `source_references` for attribution
4. Add `interaction_feedback` for learning system

### Phase 3: Optimization
1. Add performance indexes and partitioning
2. Implement data archival policies
3. Add analytics and reporting views
4. Optimize for high-volume operations

---

**Data Model Complete**: All entities designed with relationships and constraints defined. Ready for contract definition.