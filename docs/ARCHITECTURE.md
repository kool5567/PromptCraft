# PromptCraft — Architecture Design Document

## 1. Project Overview

**PromptCraft** is a production-grade AI Prompt Generator Platform supporting all modern AI models (ChatGPT, Gemini, Claude, Grok, DeepSeek, Qwen, Llama, Mistral, Perplexity, Copilot, and more).

### Goals
- Generate professional AI prompts
- Manage personal & public prompt libraries
- Free & Premium subscription tiers
- Admin panel for full platform control
- GitHub & external source import
- Extensible architecture for future models & features

---

## 2. Technology Stack

### Backend (Python)
| Technology | Justification |
|---|---|
| **FastAPI** | Async, high-performance, automatic OpenAPI docs, Pydantic validation |
| **SQLAlchemy 2.0** | Mature ORM, async support, migration-friendly |
| **Alembic** | Database migration management |
| **PostgreSQL** | Advanced JSON, full-text search, ACID compliance |
| **Redis** | Caching, session store, rate limiting |
| **Celery + RabbitMQ** | Async task queue for imports & generation |
| **JWT (python-jose)** | Stateless authentication |
| **OAuth2 (authlib)** | Social login (Google, GitHub) |
| **Pydantic v2** | Request/response validation |
| **httpx** | Async HTTP for AI model APIs |
| **Docker + Nginx** | Containerized deployment |

### Frontend (Flutter)
| Technology | Justification |
|---|---|
| **Flutter 3.x** | Cross-platform (Web, Mobile, Desktop) |
| **Material 3** | Modern design system |
| **Riverpod** | Compile-safe, testable state management |
| **Go Router** | Declarative routing with deep linking |
| **Dio** | HTTP client with interceptors |
| **Freezed** | Immutable data classes |
| **Json Serializable** | JSON code generation |
| **Flutter Secure Storage** | Secure token storage |
| **Hive** | Local caching |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Client Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Flutter Web  │  │ Flutter App │  │ Flutter     │ │
│  │ (Primary)    │  │ (iOS/Android)│  │ (Desktop)   │ │
│  └──────┬───────┘  └──────┬──────┘  └──────┬──────┘ │
└─────────┼──────────────────┼──────────────────┼──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTPS
                    ┌────────┴────────┐
                    │   Nginx (SSL)   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │   FastAPI App   │
                    │  (Uvicorn ASGI) │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────┴─────┐    ┌──────┴──────┐    ┌──────┴─────┐
    │ PostgreSQL │    │    Redis    │    │  Celery    │
    │ (Primary)  │    │  (Cache)    │    │  (Worker)  │
    └───────────┘    └─────────────┘    └──────┬─────┘
                                               │
                                      ┌────────┴────────┐
                                      │  External APIs   │
                                      │ (GitHub, OpenAI, │
                                      │  HuggingFace...) │
                                      └─────────────────┘
```

---

## 4. Database Schema (ERD)

### Core Tables

```
users
├── id: UUID (PK)
├── email: VARCHAR(255) UNIQUE NOT NULL
├── username: VARCHAR(50) UNIQUE NOT NULL
├── password_hash: VARCHAR(255) NOT NULL
├── role: ENUM('user', 'premium', 'admin', 'superadmin')
├── subscription_tier: ENUM('free', 'basic', 'pro', 'enterprise')
├── is_active: BOOLEAN DEFAULT true
├── email_verified: BOOLEAN DEFAULT false
├── profile_image: TEXT
├── created_at: TIMESTAMP WITH TIME ZONE
├── updated_at: TIMESTAMP WITH TIME ZONE
└── last_login: TIMESTAMP WITH TIME ZONE

profiles
├── id: UUID (PK)
├── user_id: UUID (FK → users.id) UNIQUE
├── display_name: VARCHAR(100)
├── bio: TEXT
├── website: VARCHAR(255)
├── github_username: VARCHAR(100)
├── preferences: JSONB
│   ├── language: 'ar' | 'en'
│   ├── theme: 'light' | 'dark' | 'system'
│   ├── default_model: UUID
│   └── editor_font_size: INT
├── created_at: TIMESTAMP WITH TIME ZONE
└── updated_at: TIMESTAMP WITH TIME ZONE

oauth_accounts
├── id: UUID (PK)
├── user_id: UUID (FK → users.id)
├── provider: VARCHAR(50) ('google', 'github')
├── provider_account_id: VARCHAR(255)
├── provider_data: JSONB
├── created_at: TIMESTAMP WITH TIME ZONE
└── UNIQUE(provider, provider_account_id)

ai_models
├── id: UUID (PK)
├── name: VARCHAR(100)
├── slug: VARCHAR(100) UNIQUE
├── description: TEXT
├── provider: VARCHAR(100)
├── category: ENUM('chat', 'image', 'code', 'video', 'music')
├── logo_url: TEXT
├── is_active: BOOLEAN DEFAULT true
├── sort_order: INT DEFAULT 0
├── metadata: JSONB
├── created_at: TIMESTAMP WITH TIME ZONE
└── updated_at: TIMESTAMP WITH TIME ZONE

categories
├── id: UUID (PK)
├── name: VARCHAR(100)
├── name_ar: VARCHAR(100)
├── slug: VARCHAR(100) UNIQUE
├── description: TEXT
├── description_ar: TEXT
├── parent_id: UUID (FK → categories.id) NULL
├── icon: VARCHAR(50)
├── color: VARCHAR(7)
├── sort_order: INT DEFAULT 0
├── is_active: BOOLEAN DEFAULT true
├── created_at: TIMESTAMP WITH TIME ZONE
└── updated_at: TIMESTAMP WITH TIME ZONE

tags
├── id: UUID (PK)
├── name: VARCHAR(50)
├── name_ar: VARCHAR(50)
├── slug: VARCHAR(50) UNIQUE
├── usage_count: INT DEFAULT 0
├── created_at: TIMESTAMP WITH TIME ZONE
└── updated_at: TIMESTAMP WITH TIME ZONE

prompts
├── id: UUID (PK)
├── user_id: UUID (FK → users.id)
├── title: VARCHAR(255)
├── title_ar: VARCHAR(255)
├── content: TEXT NOT NULL
├── content_ar: TEXT
├── description: TEXT
├── description_ar: TEXT
├── model_id: UUID (FK → ai_models.id)
├── category_id: UUID (FK → categories.id)
├── is_public: BOOLEAN DEFAULT false
├── is_premium: BOOLEAN DEFAULT false
├── is_template: BOOLEAN DEFAULT false
├── variables: JSONB
│   └── [{"name": "var1", "type": "text", "default": "", "required": true}, ...]
├── variables_ar: JSONB
├── usage_count: INT DEFAULT 0
├── copy_count: INT DEFAULT 0
├── rating_avg: DECIMAL(2,1) DEFAULT 0.0
├── rating_count: INT DEFAULT 0
├── status: ENUM('draft', 'published', 'archived')
├── version: INT DEFAULT 1
├── imported_from: VARCHAR(255)
├── license: VARCHAR(50)
├── created_at: TIMESTAMP WITH TIME ZONE
├── updated_at: TIMESTAMP WITH TIME ZONE
└── deleted_at: TIMESTAMP WITH TIME ZONE NULL

prompt_tags
├── prompt_id: UUID (FK → prompts.id)
├── tag_id: UUID (FK → tags.id)
└── PRIMARY KEY (prompt_id, tag_id)

prompt_versions
├── id: UUID (PK)
├── prompt_id: UUID (FK → prompts.id)
├── content: TEXT NOT NULL
├── variables: JSONB
├── version_number: INT
├── changelog: TEXT
├── created_by: UUID (FK → users.id)
└── created_at: TIMESTAMP WITH TIME ZONE

prompt_ratings
├── id: UUID (PK)
├── prompt_id: UUID (FK → prompts.id)
├── user_id: UUID (FK → users.id)
├── rating: INT CHECK (1-5)
├── review: TEXT
├── created_at: TIMESTAMP WITH TIME ZONE
└── UNIQUE(prompt_id, user_id)

favorites
├── id: UUID (PK)
├── user_id: UUID (FK → users.id)
├── prompt_id: UUID (FK → prompts.id)
├── created_at: TIMESTAMP WITH TIME ZONE
└── UNIQUE(user_id, prompt_id)

collections
├── id: UUID (PK)
├── user_id: UUID (FK → users.id)
├── name: VARCHAR(255)
├── name_ar: VARCHAR(255)
├── description: TEXT
├── is_public: BOOLEAN DEFAULT false
├── cover_image: TEXT
├── sort_order: INT DEFAULT 0
├── created_at: TIMESTAMP WITH TIME ZONE
└── updated_at: TIMESTAMP WITH TIME ZONE

collection_prompts
├── id: UUID (PK)
├── collection_id: UUID (FK → collections.id)
├── prompt_id: UUID (FK → prompts.id)
├── added_by: UUID (FK → users.id)
├── sort_order: INT DEFAULT 0
├── created_at: TIMESTAMP WITH TIME ZONE
└── UNIQUE(collection_id, prompt_id)

subscriptions
├── id: UUID (PK)
├── user_id: UUID (FK → users.id) UNIQUE
├── plan_type: ENUM('basic', 'pro', 'enterprise')
├── status: ENUM('active', 'canceled', 'expired', 'past_due')
├── start_date: TIMESTAMP WITH TIME ZONE
├── end_date: TIMESTAMP WITH TIME ZONE
├── trial_end: TIMESTAMP WITH TIME ZONE
├── payment_provider: VARCHAR(50)
├── payment_provider_id: VARCHAR(255)
├── auto_renew: BOOLEAN DEFAULT true
├── metadata: JSONB
├── created_at: TIMESTAMP WITH TIME ZONE
└── updated_at: TIMESTAMP WITH TIME ZONE

import_jobs
├── id: UUID (PK)
├── user_id: UUID (FK → users.id)
├── source_type: ENUM('github', 'json', 'csv', 'api')
├── source_url: VARCHAR(500)
├── source_config: JSONB
├── status: ENUM('pending', 'processing', 'completed', 'failed')
├── items_total: INT DEFAULT 0
├── items_imported: INT DEFAULT 0
├── items_failed: INT DEFAULT 0
├── error_log: JSONB
├── created_at: TIMESTAMP WITH TIME ZONE
├── started_at: TIMESTAMP WITH TIME ZONE
└── completed_at: TIMESTAMP WITH TIME ZONE

site_settings
├── id: UUID (PK)
├── key: VARCHAR(100) UNIQUE
├── value: JSONB
├── type: ENUM('string', 'integer', 'boolean', 'json', 'array')
├── description: TEXT
└── updated_at: TIMESTAMP WITH TIME ZONE

usage_logs
├── id: UUID (PK)
├── user_id: UUID (FK → users.id) NULL
├── prompt_id: UUID (FK → prompts.id) NULL
├── action: VARCHAR(50)
├── ip_address: INET
├── user_agent: TEXT
├── metadata: JSONB
├── created_at: TIMESTAMP WITH TIME ZONE

admin_logs
├── id: UUID (PK)
├── admin_id: UUID (FK → users.id)
├── action: VARCHAR(100)
├── target_type: VARCHAR(50)
├── target_id: UUID
├── details: JSONB
├── ip_address: INET
└── created_at: TIMESTAMP WITH TIME ZONE
```

---

## 5. API Design (RESTful)

### Base URL: `/api/v1`

#### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login | No |
| POST | `/auth/logout` | Logout | Yes |
| POST | `/auth/refresh` | Refresh token | Yes |
| GET | `/auth/verify-email/{token}` | Verify email | No |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password | No |
| GET | `/auth/oauth/{provider}` | OAuth login URL | No |
| POST | `/auth/oauth/{provider}/callback` | OAuth callback | No |

#### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/me` | Get current user | Yes |
| PUT | `/users/me` | Update profile | Yes |
| PUT | `/users/me/password` | Change password | Yes |
| DELETE | `/users/me` | Delete account | Yes |
| GET | `/users/me/stats` | User statistics | Yes |

#### Prompts (CRUD)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/prompts` | List prompts | Optional |
| POST | `/prompts` | Create prompt | Yes |
| GET | `/prompts/{id}` | Get prompt | Optional |
| PUT | `/prompts/{id}` | Update prompt | Owner/Admin |
| DELETE | `/prompts/{id}` | Delete prompt | Owner/Admin |
| POST | `/prompts/{id}/copy` | Copy prompt | Yes |
| POST | `/prompts/{id}/copy-to-collection` | Copy to collection | Yes |
| GET | `/prompts/{id}/versions` | Version history | Owner/Admin |
| POST | `/prompts/{id}/versions` | Create new version | Owner |

#### Generator
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/generator/generate` | Generate prompt | Yes |
| POST | `/generator/enhance` | Enhance existing prompt | Yes |
| POST | `/generator/translate` | Translate prompt | Yes |
| GET | `/generator/suggestions` | Get suggestions | Yes |
| POST | `/generator/complete` | Auto-complete prompt | Yes |

#### Library (Public)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/library` | Browse public prompts | No |
| GET | `/library/featured` | Featured prompts | No |
| GET | `/library/recent` | Recent prompts | No |
| GET | `/library/popular` | Popular prompts | No |
| GET | `/library/trending` | Trending prompts | No |

#### Categories
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/categories` | List categories | No |
| GET | `/categories/{slug}` | Get category | No |
| GET | `/categories/{slug}/prompts` | Prompts in category | No |
| POST | `/categories` | Create category | Admin |
| PUT | `/categories/{id}` | Update category | Admin |
| DELETE | `/categories/{id}` | Delete category | Admin |

#### Tags
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/tags` | List tags | No |
| GET | `/tags/{slug}` | Get tag | No |
| GET | `/tags/{slug}/prompts` | Prompts with tag | No |

#### Models
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/models` | List AI models | No |
| GET | `/models/{slug}` | Get model | No |
| POST | `/models` | Create model | Admin |
| PUT | `/models/{id}` | Update model | Admin |
| DELETE | `/models/{id}` | Delete model | Admin |

#### Favorites
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/favorites` | User favorites | Yes |
| POST | `/favorites/{prompt_id}` | Add favorite | Yes |
| DELETE | `/favorites/{prompt_id}` | Remove favorite | Yes |

#### Collections
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/collections` | User collections | Yes |
| POST | `/collections` | Create collection | Yes |
| GET | `/collections/{id}` | Get collection | Optional |
| PUT | `/collections/{id}` | Update collection | Owner |
| DELETE | `/collections/{id}` | Delete collection | Owner |
| POST | `/collections/{id}/prompts` | Add prompt to collection | Owner |
| DELETE | `/collections/{id}/prompts/{prompt_id}` | Remove from collection | Owner |

#### Templates
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/templates` | List templates | No |
| POST | `/templates` | Create template | Yes |
| GET | `/templates/{id}` | Get template | No |
| PUT | `/templates/{id}` | Update template | Owner |
| DELETE | `/templates/{id}` | Delete template | Owner |
| POST | `/templates/{id}/use` | Use template | Yes |

#### Ratings
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/prompts/{id}/rate` | Rate prompt | Yes |
| GET | `/prompts/{id}/ratings` | Get ratings | No |

#### Import/Export
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/import/github` | Import from GitHub | Yes |
| POST | `/import/file` | Import from file | Yes |
| POST | `/import/api` | Import from API | Yes |
| GET | `/import/jobs` | Import history | Yes |
| GET | `/import/jobs/{id}` | Import job status | Yes |
| GET | `/export/prompts` | Export user prompts | Yes |
| GET | `/export/collection/{id}` | Export collection | Yes |

#### Search
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/search` | Full-text search | No |
| GET | `/search/suggestions` | Search suggestions | No |

#### Subscriptions
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/subscriptions/plans` | Available plans | No |
| POST | `/subscriptions/subscribe` | Subscribe | Yes |
| POST | `/subscriptions/cancel` | Cancel subscription | Yes |
| GET | `/subscriptions/my` | My subscription | Yes |
| POST | `/subscriptions/change-plan` | Change plan | Yes |

#### Admin
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/dashboard` | Dashboard stats | Admin |
| GET | `/admin/users` | List users | Admin |
| GET | `/admin/users/{id}` | User details | Admin |
| PUT | `/admin/users/{id}` | Update user | Admin |
| DELETE | `/admin/users/{id}` | Delete user | Admin |
| GET | `/admin/prompts` | All prompts | Admin |
| PUT | `/admin/prompts/{id}/status` | Change prompt status | Admin |
| DELETE | `/admin/prompts/{id}` | Delete prompt | Admin |
| GET | `/admin/imports` | All imports | Admin |
| GET | `/admin/analytics` | Analytics | Admin |
| GET | `/admin/settings` | Site settings | Admin |
| PUT | `/admin/settings` | Update settings | Admin |
| POST | `/admin/sync-github` | Sync GitHub repos | Admin |

---

## 6. Security Architecture

### Authentication Flow
```
1. User submits credentials
2. Server validates → returns access_token (15min) + refresh_token (30d)
3. Access_token in Authorization header for API calls
4. Refresh flow: POST /auth/refresh with refresh_token
5. Token blacklist on logout (Redis)
```

### Authorization (RBAC)
```
Roles: user → premium → admin → superadmin

- user: CRUD own prompts, view public library, use generator (limited)
- premium: Unlimited generation, premium prompts, API access
- admin: Moderate content, manage users, manage categories
- superadmin: Full system access, settings, import management
```

### Security Measures
- Password hashing: bcrypt (12 rounds)
- JWT: RS256 with 4096-bit keys
- Rate limiting: 100 req/min per user, 20 req/min for auth
- CORS: Whitelist only
- SQL Injection: SQLAlchemy parameterized queries
- XSS: Input sanitization + CSP headers
- CSRF: Double-submit cookie pattern
- Data encryption at rest: PostgreSQL TDE
- HTTPS enforced

---

## 7. Frontend Architecture (Flutter)

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                  Presentation Layer                  │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │ Screens/Pages│  │  Widgets    │  │ Providers │  │
│  └──────┬───────┘  └──────┬──────┘  └─────┬─────┘  │
└─────────┼─────────────────┼────────────────┼────────┘
          │                 │                │
┌─────────┼─────────────────┼────────────────┼────────┐
│         │    Domain Layer │                │        │
│  ┌──────┴───────┐  ┌─────┴──────┐  ┌──────┴──────┐ │
│  │   Entities   │  │ UseCases   │  │ Repositories│ │
│  │  (Freezed)   │  │            │  │ (Abstract)  │ │
│  └──────────────┘  └────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────┐
│         │              Data Layer                   │
│  ┌──────┴───────┐  ┌─────────────┐  ┌───────────┐  │
│  │  Models      │  │ Repositories│  │ Datasources│  │
│  │ (JSONable)   │  │ (Impl)      │  │ API/Local  │  │
│  └──────────────┘  └─────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────┘
```

### Route Structure (Go Router)
```
/                               → HomeScreen
/login                          → LoginScreen
/register                       → RegisterScreen
/forgot-password                → ForgotPasswordScreen
/prompts                        → LibraryScreen
/prompts/new                    → CreatePromptScreen
/prompts/:id                    → PromptDetailScreen
/prompts/:id/edit               → EditPromptScreen
/generator                      → GeneratorScreen
/generator/:id                  → GeneratorDetailScreen
/templates                      → TemplatesScreen
/templates/:id                  → TemplateDetailScreen
/templates/:id/use              → UseTemplateScreen
/collections                    → CollectionsScreen
/collections/:id                → CollectionDetailScreen
/favorites                      → FavoritesScreen
/profile                        → ProfileScreen
/settings                       → SettingsScreen
/subscription                   → SubscriptionScreen
/subscription/plans             → PlansScreen
/admin                          → AdminDashboardScreen
/admin/users                    → AdminUsersScreen
/admin/prompts                  → AdminPromptsScreen
/admin/categories               → AdminCategoriesScreen
/admin/models                   → AdminModelsScreen
/admin/imports                  → AdminImportsScreen
/admin/settings                 → AdminSettingsScreen
/admin/analytics                → AdminAnalyticsScreen
```

---

## 8. Subscription Tiers

| Feature | Free | Basic ($9.99/mo) | Pro ($19.99/mo) | Enterprise ($49.99/mo) |
|---------|------|-------------------|------------------|------------------------|
| Daily generations | 5 | 50 | Unlimited | Unlimited |
| Prompt library | 50 | 500 | Unlimited | Unlimited |
| Public library access | ✓ | ✓ | ✓ | ✓ |
| Premium prompts | ✗ | ✗ | ✓ | ✓ |
| Templates | Basic | Full | Full | Full |
| Version history | 7 days | 30 days | 90 days | Unlimited |
| API access | ✗ | 1000/day | 10000/day | Unlimited |
| GitHub import | ✗ | ✓ | ✓ | ✓ |
| Bulk export | ✗ | ✗ | ✓ | ✓ |
| Priority support | ✗ | ✗ | Email | 24/7 |
| Team accounts | 1 | 1 | 3 | 10+ |
| Custom branding | ✗ | ✗ | ✗ | ✓ |

---

## 9. Admin Dashboard Features

1. **Dashboard** — Real-time stats (users, prompts, generations, revenue)
2. **Users Management** — CRUD, ban, role change, subscription override
3. **Prompts Management** — Moderate, feature, delete, bulk operations
4. **Categories Management** — CRUD with drag-drop ordering
5. **Tags Management** — CRUD, merge, clean duplicates
6. **AI Models Management** — CRUD, toggle active/inactive, API config
7. **Site Settings** — Key-value configuration UI
8. **Import Management** — GitHub repos, file uploads, API sync
9. **Analytics** — Charts, export CSV, user growth, top prompts
10. **Logs** — Admin action logs, system logs
11. **Theme Customization** — Colors, logos, branding
12. **Payment Management** — Subscriptions, invoices, refunds

---

## 10. Project Structure

```
promptcraft/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── prompts.py
│   │   │   ├── generator.py
│   │   │   ├── library.py
│   │   │   ├── categories.py
│   │   │   ├── tags.py
│   │   │   ├── models.py
│   │   │   ├── favorites.py
│   │   │   ├── collections.py
│   │   │   ├── templates.py
│   │   │   ├── ratings.py
│   │   │   ├── import_export.py
│   │   │   ├── search.py
│   │   │   ├── subscriptions.py
│   │   │   ├── admin.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   ├── cache.py
│   │   │   ├── celery_app.py
│   │   │   └── exceptions.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── profile.py
│   │   │   ├── prompt.py
│   │   │   ├── category.py
│   │   │   ├── tag.py
│   │   │   ├── ai_model.py
│   │   │   ├── collection.py
│   │   │   ├── subscription.py
│   │   │   ├── import_job.py
│   │   │   ├── favorite.py
│   │   │   ├── rating.py
│   │   │   ├── setting.py
│   │   │   └── log.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── prompt.py
│   │   │   ├── category.py
│   │   │   ├── tag.py
│   │   │   ├── ai_model.py
│   │   │   ├── collection.py
│   │   │   ├── subscription.py
│   │   │   ├── import_job.py
│   │   │   ├── generator.py
│   │   │   ├── search.py
│   │   │   ├── admin.py
│   │   │   └── common.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── prompt_service.py
│   │   │   ├── generator_service.py
│   │   │   ├── library_service.py
│   │   │   ├── category_service.py
│   │   │   ├── tag_service.py
│   │   │   ├── model_service.py
│   │   │   ├── favorite_service.py
│   │   │   ├── collection_service.py
│   │   │   ├── template_service.py
│   │   │   ├── import_service.py
│   │   │   ├── export_service.py
│   │   │   ├── search_service.py
│   │   │   ├── subscription_service.py
│   │   │   ├── admin_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── github_service.py
│   │   │   └── notification_service.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user_repository.py
│   │   │   ├── prompt_repository.py
│   │   │   ├── category_repository.py
│   │   │   ├── tag_repository.py
│   │   │   ├── model_repository.py
│   │   │   ├── collection_repository.py
│   │   │   ├── subscription_repository.py
│   │   │   ├── import_repository.py
│   │   │   ├── favorite_repository.py
│   │   │   └── setting_repository.py
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── database.py
│   │   │   └── pagination.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   ├── rate_limit.py
│   │   │   ├── logging.py
│   │   │   └── subscription_check.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── slug.py
│   │   │   ├── pagination.py
│   │   │   ├── validators.py
│   │   │   └── helpers.py
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── import_tasks.py
│   │   │   ├── generation_tasks.py
│   │   │   └── cleanup_tasks.py
│   │   ├── main.py
│   │   └── __init__.py
│   ├── migrations/
│   │   ├── env.py
│   │   ├── alembic.ini
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_prompts.py
│   │   ├── test_generator.py
│   │   └── test_admin.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── lib/
│   │   ├── core/
│   │   │   ├── constants/
│   │   │   │   ├── api_constants.dart
│   │   │   │   ├── app_constants.dart
│   │   │   │   └── app_colors.dart
│   │   │   ├── errors/
│   │   │   │   ├── exceptions.dart
│   │   │   │   └── failures.dart
│   │   │   ├── network/
│   │   │   │   ├── dio_client.dart
│   │   │   │   ├── api_interceptors.dart
│   │   │   │   └── network_info.dart
│   │   │   ├── theme/
│   │   │   │   ├── app_theme.dart
│   │   │   │   ├── dark_theme.dart
│   │   │   │   └── light_theme.dart
│   │   │   └── utils/
│   │   │       ├── validators.dart
│   │   │       ├── helpers.dart
│   │   │       └── extensions.dart
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── prompts/
│   │   │   ├── library/
│   │   │   ├── generator/
│   │   │   ├── admin/
│   │   │   ├── subscription/
│   │   │   └── templates/
│   │   ├── app.dart
│   │   └── main.dart
│   ├── pubspec.yaml
│   ├── analysis_options.yaml
│   └── Dockerfile
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── ssl/
│   └── postgres/
│       └── init.sql
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── .gitignore
├── .env.example
└── README.md
```

---

## 11. Data Flow Diagrams

### Prompt Generation Flow
```
User → Generator Screen → API Gateway → Generator Service
    → Check Subscription Tier → Check Daily Limit
    → Call AI Model API (OpenAI/Claude/etc)
    → Process Response → Save to History → Return Result
```

### GitHub Import Flow
```
Admin → Import Screen → Submit GitHub URL → API Gateway
    → Import Service → Create Import Job → Celery Worker
    → Fetch GitHub API → Parse Repository → Extract Prompts
    → Save to Database → Update Import Status → Notify Admin
```

### Search Flow
```
User → Search Query → API Gateway → Search Service
    → Full-Text Search (PostgreSQL tsvector)
    → Filter by Tags/Categories/Models
    → Sort by Relevance/Popularity/Date
    → Paginate → Return Results
```

---

## 12. Scalability Considerations

- **Horizontal scaling**: FastAPI is stateless → multiple workers behind Nginx
- **Database**: Read replicas for library/search, connection pooling
- **Caching**: Redis for hot prompts, categories, and user sessions
- **CDN**: Static assets on CloudFront/CDN
- **Background jobs**: Celery for heavy operations (import, generation)
- **Rate limiting**: Redis-based sliding window
- **Search**: PostgreSQL full-text search initially → Elasticsearch later

---

## 13. Future Extensibility

1. **Plugin system** for custom AI model integrations
2. **WebSocket** for real-time collaborative editing
3. **Mobile app** (Flutter already supports iOS/Android)
4. **Chrome extension** for quick prompt access
5. **Community marketplace** for paid prompt templates
6. **Team/collaboration** features with shared workspaces
7. **AI prompt chaining** for complex workflows
8. **API marketplace** for third-party developers
9. **Multi-language** support (RTL for Arabic)
10. **A/B testing** framework for prompt optimization
