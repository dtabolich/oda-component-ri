# Backlog Management Guide

Comprehensive guide for organizing and managing backlogs for the main product (ProductCatalog) and supplementary plugins (ProductInventory, etc.) in Azure DevOps.

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Work Item Hierarchy](#work-item-hierarchy)
4. [Backlog Organization Strategies](#backlog-organization-strategies)
5. [Sprint Planning](#sprint-planning)
6. [Dependencies Management](#dependencies-management)
7. [Best Practices](#best-practices)
8. [Queries and Views](#queries-and-views)

---

## Overview

### Product Structure
- **Main Product**: ProductCatalog (core offering)
- **Plugins**: ProductInventory, additional extensions
- **Shared Components**: Common libraries, infrastructure

### Key Principles
- Clear separation between product and plugins
- Visibility into cross-component dependencies
- Independent plugin development cycles
- Coordinated releases when needed

---

## Project Structure

### Recommended: Single Project with Areas

**Structure:**
```
Product-Management-Platform/
├── ProductCatalog (Main Product)
│   ├── API
│   ├── Backend
│   ├── Frontend
│   └── Infrastructure
├── ProductInventory (Plugin)
│   ├── API
│   ├── Backend
│   └── Integration
├── Shared
│   ├── Libraries
│   ├── Infrastructure
│   └── DevOps
└── Cross-Component
    ├── Integration
    └── Platform
```

### Alternative: Multiple Projects

**When to Use:**
- Very large organization
- Different teams with minimal overlap
- Different security requirements
- Independent release cycles critical

**Structure:**
```
- Project: ProductCatalog (Main)
- Project: ProductInventory (Plugin)
- Project: Platform-Shared (Common)
```

---

## Azure DevOps Setup

### Step 1: Configure Area Paths

Navigate to **Project Settings** → **Project configuration** → **Areas**

**Recommended Area Structure:**

```
Product-Management-Platform
├── ProductCatalog
│   ├── Core-API
│   ├── Party-Role-API
│   ├── Promotion-API
│   ├── Metrics-API
│   └── Infrastructure
├── ProductInventory
│   ├── Inventory-API
│   ├── Party-Role-API
│   └── Integration
├── Shared-Services
│   ├── Authentication
│   ├── Monitoring
│   └── DevOps
└── Platform
    ├── Infrastructure
    ├── Security
    └── Documentation
```

**Setup Script:**
```bash
# Use Azure DevOps CLI to create area paths
az boards area project create --name "ProductCatalog" --project "Product-Management-Platform"
az boards area project create --name "ProductCatalog\\Core-API" --project "Product-Management-Platform"
az boards area project create --name "ProductCatalog\\Party-Role-API" --project "Product-Management-Platform"
az boards area project create --name "ProductCatalog\\Promotion-API" --project "Product-Management-Platform"
az boards area project create --name "ProductCatalog\\Metrics-API" --project "Product-Management-Platform"
az boards area project create --name "ProductCatalog\\Infrastructure" --project "Product-Management-Platform"

az boards area project create --name "ProductInventory" --project "Product-Management-Platform"
az boards area project create --name "ProductInventory\\Inventory-API" --project "Product-Management-Platform"
az boards area project create --name "ProductInventory\\Party-Role-API" --project "Product-Management-Platform"
az boards area project create --name "ProductInventory\\Integration" --project "Product-Management-Platform"

az boards area project create --name "Shared-Services" --project "Product-Management-Platform"
az boards area project create --name "Platform" --project "Product-Management-Platform"
```

### Step 2: Configure Iteration Paths (Sprints)

Navigate to **Project Settings** → **Project configuration** → **Iterations**

**Recommended Iteration Structure:**

```
Product-Management-Platform
├── 2025
│   ├── Q1
│   │   ├── Sprint 1 (Jan 6-19)
│   │   ├── Sprint 2 (Jan 20-Feb 2)
│   │   ├── Sprint 3 (Feb 3-16)
│   │   ├── Sprint 4 (Feb 17-Mar 2)
│   │   ├── Sprint 5 (Mar 3-16)
│   │   └── Sprint 6 (Mar 17-30)
│   ├── Q2
│   │   ├── Sprint 7-12
│   ├── Q3
│   │   ├── Sprint 13-18
│   └── Q4
│       ├── Sprint 19-24
└── Backlog (Unscheduled)
```

---

## Work Item Hierarchy

### Work Item Types

```
Epic (Strategic Initiative)
├── Feature (Deliverable Capability)
│   ├── User Story (User-Facing Functionality)
│   │   ├── Task (Development Work)
│   │   ├── Bug (Defects)
│   │   └── Test Case (Testing)
│   └── User Story
└── Feature
```

### Tagging Strategy

Use tags to add metadata beyond area paths:

**Component Tags:**
- `main-product`
- `plugin`
- `shared-service`
- `infrastructure`

**Product-Specific Tags:**
- `productcatalog`
- `productinventory`
- `metrics`
- `partyrole`

**Type Tags:**
- `api`
- `backend`
- `frontend`
- `devops`
- `database`

**Priority Tags:**
- `critical`
- `customer-facing`
- `technical-debt`
- `performance`
- `security`

**Release Tags:**
- `v1.2.0`
- `v1.3.0`
- `hotfix`

**Integration Tags:**
- `cross-component`
- `api-contract`
- `breaking-change`

---

## Backlog Organization Strategies

### Strategy 1: Area-Based Organization (Recommended)

**Best for:**
- Teams organized by component
- Clear ownership boundaries
- Independent development cycles

**Setup:**

1. **Main Product Backlog**
   - Area: `ProductCatalog`
   - Team: ProductCatalog Team
   - Sprint cadence: 2 weeks
   - Focus: Core product features

2. **Plugin Backlogs**
   - Area: `ProductInventory`
   - Team: ProductInventory Team
   - Sprint cadence: 2 weeks (synchronized)
   - Focus: Plugin-specific features

3. **Shared Backlog**
   - Area: `Shared-Services`
   - Team: Platform Team
   - Sprint cadence: 2 weeks
   - Focus: Infrastructure, shared components

**Benefits:**
- ✅ Clear separation of concerns
- ✅ Independent team velocity tracking
- ✅ Easy to filter and report
- ✅ Scales well with growth

**Backlog Views:**
```
View 1: ProductCatalog Backlog
- Filter: Area Path = ProductCatalog
- Sorted by: Priority, then Business Value

View 2: ProductInventory Backlog
- Filter: Area Path = ProductInventory
- Sorted by: Priority, then Business Value

View 3: Platform Backlog
- Filter: Area Path = Shared-Services OR Platform
- Sorted by: Priority, Impact

View 4: Integrated Backlog (Leadership View)
- Filter: All Areas
- Grouped by: Area Path
- Sorted by: Business Value
```

### Strategy 2: Tag-Based Organization

**Best for:**
- Cross-functional teams
- Flexible team structures
- Frequent cross-component work

**Setup:**

Use tags as primary organizational mechanism:

**Epic Examples:**
```
Epic: "Product Catalog Enhancement" 
- Tags: main-product, productcatalog, v1.3.0
- Area: ProductCatalog

Epic: "Inventory Management v2"
- Tags: plugin, productinventory, v1.2.0
- Area: ProductInventory

Epic: "Platform Monitoring Upgrade"
- Tags: shared-service, infrastructure, monitoring
- Area: Shared-Services
```

### Strategy 3: Hybrid Approach (Recommended for Most)

**Combination of Areas + Tags:**

- **Areas**: Organizational boundaries (teams, components)
- **Tags**: Additional metadata (release, type, priority)

**Example Work Item:**
```
Title: "Add pagination support to Product Catalog API"
Type: User Story
Area: ProductCatalog\Core-API
Tags: main-product, api, v1.3.0, performance
Priority: 2
Business Value: 50
```

---

## Work Item Templates

### Epic Template

```
Title: [Epic] {Strategic Initiative Name}

Description:
## Overview
Brief description of the strategic initiative

## Business Value
Why this is important and expected outcomes

## Scope
### In Scope
- Item 1
- Item 2

### Out of Scope
- Item 1
- Item 2

## Success Criteria
- Measurable outcome 1
- Measurable outcome 2

## Dependencies
- Dependency 1
- Dependency 2

## Timeline
Target: Q1 2025

Area Path: ProductCatalog or ProductInventory
Tags: main-product/plugin, version-tag
```

### Feature Template

```
Title: [Feature] {Capability Name}

Description:
## Feature Description
What capability are we building?

## User Benefit
How does this help users?

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Approach
High-level technical approach

## Dependencies
- List of dependent features/components

## API Changes
- New endpoints
- Modified endpoints
- Breaking changes

Area Path: ProductCatalog\Core-API
Tags: api, v1.3.0
Parent: Link to Epic
```

### User Story Template

```
Title: As a {user type}, I want to {action}, so that {benefit}

Description:
## User Story
As a [role]
I want [feature]
So that [benefit]

## Acceptance Criteria
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]

## Technical Notes
- Implementation details
- API contracts
- Database changes

## Definition of Done
- [ ] Code complete and reviewed
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Deployed to dev environment
- [ ] QA validated

Area Path: ProductCatalog\Core-API
Tags: api, backend
Parent: Link to Feature
Story Points: 5
```

---

## Sprint Planning

### Coordinated Sprint Planning (Recommended)

**Schedule:**
- All teams follow same sprint cadence (2 weeks)
- Sprint Planning: Monday, Week 1 (9 AM - 11 AM)
- Sprint Review: Friday, Week 2 (2 PM - 4 PM)
- Sprint Retrospective: Friday, Week 2 (4 PM - 5 PM)

**Process:**

**Week Before Sprint:**
1. **Backlog Refinement** (Wednesday)
   - Each team refines their backlog
   - Identify cross-component dependencies
   - Estimate stories

2. **Cross-Team Sync** (Friday)
   - Platform team presents upcoming infrastructure work
   - Teams flag dependencies
   - Coordinate integration points

**Sprint Planning Day:**

**9:00 AM - Team Planning (Parallel)**
- ProductCatalog team plans their sprint
- ProductInventory team plans their sprint
- Platform team plans their sprint

**10:30 AM - Cross-Team Integration Planning**
- Review dependencies
- Identify integration points
- Coordinate deployment timing
- Align on acceptance criteria

**11:00 AM - Sprint Commitment**
- Teams finalize commitments
- Document cross-team dependencies
- Set integration milestones

### Independent Sprint Planning

**When to Use:**
- Plugin development completely independent
- No shared dependencies in sprint
- Different team velocities

**Best Practices:**
- Maintain shared calendar of releases
- Weekly sync on integration status
- Monthly roadmap alignment

---

## Dependencies Management

### Dependency Types

1. **Hard Dependencies**: Must be completed sequentially
2. **Soft Dependencies**: Preferred order, can work in parallel
3. **Integration Dependencies**: Require coordination
4. **Shared Resource Dependencies**: Same infrastructure/service

### Tracking Dependencies in Azure DevOps

**Method 1: Work Item Links**

```
Feature A (ProductCatalog)
└── Predecessor Link → Feature B (ProductInventory)
```

**Setup:**
1. Open work item
2. Click **Add link** → **Existing item**
3. Link type: **Predecessor** or **Successor**
4. Select dependent work item

**Method 2: Dependency Tracking Board**

Create custom board for dependencies:
1. Navigate to **Boards** → **Boards**
2. Create new board: "Cross-Component Dependencies"
3. Columns: Identified → In Progress → Integrated → Validated
4. Swimlanes: ProductCatalog, ProductInventory, Platform

**Method 3: Tags**

Use dependency tags:
- `depends-on-catalog`
- `depends-on-inventory`
- `depends-on-platform`
- `blocks-others`

### Dependency Review Meeting

**Frequency**: Weekly (15 minutes)

**Agenda:**
1. Review dependency board
2. Identify new dependencies
3. Update status of existing dependencies
4. Resolve blockers
5. Plan integration testing

---

## Queries and Views

### Essential Queries

#### 1. My Active Work
```sql
Work Item Type IN ('User Story', 'Task', 'Bug')
AND State NOT IN ('Closed', 'Removed')
AND Assigned To = @Me
ORDER BY Priority ASC, Created Date DESC
```

#### 2. ProductCatalog Backlog
```sql
Work Item Type IN ('Epic', 'Feature', 'User Story')
AND Area Path UNDER 'Product-Management-Platform\ProductCatalog'
AND State NOT IN ('Closed', 'Removed')
ORDER BY Stack Rank ASC
```

#### 3. ProductInventory Backlog
```sql
Work Item Type IN ('Epic', 'Feature', 'User Story')
AND Area Path UNDER 'Product-Management-Platform\ProductInventory'
AND State NOT IN ('Closed', 'Removed')
ORDER BY Stack Rank ASC
```

#### 4. Cross-Component Dependencies
```sql
Work Item Type IN ('Feature', 'User Story')
AND (Tags CONTAINS 'cross-component' OR Tags CONTAINS 'integration')
AND State NOT IN ('Closed', 'Removed')
ORDER BY Priority ASC
```

#### 5. Current Sprint - All Teams
```sql
Work Item Type IN ('User Story', 'Task', 'Bug')
AND Iteration Path = @CurrentIteration
ORDER BY Area Path, State
```

#### 6. Upcoming Release Items
```sql
Work Item Type IN ('Feature', 'User Story')
AND Tags CONTAINS 'v1.3.0'
AND State NOT IN ('Closed', 'Removed')
ORDER BY Priority ASC, Area Path
```

#### 7. Blocked Items
```sql
Work Item Type IN ('User Story', 'Task')
AND State = 'Active'
AND Blocked = 'Yes'
ORDER BY Priority ASC
```

#### 8. Technical Debt
```sql
Work Item Type IN ('User Story', 'Task')
AND Tags CONTAINS 'technical-debt'
AND State NOT IN ('Closed', 'Removed')
ORDER BY Priority ASC, Business Value DESC
```

### Dashboard Widgets

**Recommended Dashboard Layout:**

**Dashboard 1: Product Overview**
- Epic Progress (ProductCatalog)
- Epic Progress (ProductInventory)
- Sprint Burndown (All Teams)
- Velocity Chart (All Teams)
- Bug Trend
- Release Progress

**Dashboard 2: Team Dashboards (Per Component)**
- Sprint Burndown
- Cumulative Flow Diagram
- Velocity
- Work Item Chart (by state)
- Bug Analysis

**Dashboard 3: Dependencies Dashboard**
- Cross-Component Work Items
- Blocked Items
- Integration Status
- Release Timeline

---

## Portfolio Management

### Roadmap View

**Setup in Azure DevOps:**
1. Navigate to **Boards** → **Plans**
2. Create new plan: "Product Roadmap"
3. Add teams:
   - ProductCatalog Team
   - ProductInventory Team
   - Platform Team
4. Configure:
   - Show: Epics and Features
   - Group by: Team
   - Time scale: Months

**Roadmap Structure:**
```
Q1 2025
├── ProductCatalog
│   ├── [Epic] Enhanced Search Capabilities
│   ├── [Epic] Multi-Language Support
│   └── [Feature] API v2 Migration
├── ProductInventory
│   ├── [Epic] Real-Time Inventory Sync
│   └── [Feature] Bulk Operations
└── Platform
    ├── [Epic] Infrastructure Upgrade
    └── [Feature] Monitoring Enhancement

Q2 2025
├── ProductCatalog
│   └── [Epic] Advanced Analytics
├── ProductInventory
│   └── [Epic] Warehouse Management
└── Platform
    └── [Epic] Security Hardening
```

---

## Best Practices

### 1. Backlog Grooming

**Weekly Grooming Sessions:**
- **ProductCatalog**: Wednesdays, 2 PM (1 hour)
- **ProductInventory**: Wednesdays, 3 PM (1 hour)
- **Cross-Component**: Fridays, 10 AM (30 minutes)

**Grooming Checklist:**
- [ ] Review upcoming stories
- [ ] Break down large items
- [ ] Add acceptance criteria
- [ ] Estimate story points
- [ ] Identify dependencies
- [ ] Update priority
- [ ] Assign to sprint (if ready)

### 2. Work Item Standards

**Title Conventions:**
```
✅ Good:
- "Add pagination to Product Catalog API"
- "Fix: Memory leak in inventory sync process"
- "Refactor: Authentication middleware"

❌ Bad:
- "Update"
- "Fix bug"
- "Changes"
```

**Description Requirements:**
- Clear problem statement
- Acceptance criteria
- Technical approach (for complex items)
- Dependencies listed
- Definition of done

### 3. Priority Management

**Priority Levels:**
- **1 - Critical**: Production issues, security vulnerabilities
- **2 - High**: Customer commitments, blocking issues
- **3 - Medium**: Planned features, improvements
- **4 - Low**: Nice-to-have, future enhancements

**Priority Review:**
- Daily: Review P1 items
- Weekly: Review P2 items
- Bi-weekly: Reprioritize backlog

### 4. Capacity Planning

**Story Points Scale:**
- 1 point: < 4 hours
- 2 points: 4-8 hours
- 3 points: 1-2 days
- 5 points: 2-3 days
- 8 points: 3-5 days
- 13 points: Too large, break down

**Team Capacity:**
- Track velocity over last 3-5 sprints
- Plan for 80% of capacity (buffer for unplanned work)
- Reserve 20% for bugs, tech debt, support

### 5. Definition of Ready (DoR)

Before pulling into sprint:
- [ ] User story has clear title and description
- [ ] Acceptance criteria defined
- [ ] Dependencies identified and tracked
- [ ] Story points estimated
- [ ] No major unknowns
- [ ] Testable
- [ ] Sized appropriately (≤ 8 points)

### 6. Definition of Done (DoD)

Before marking complete:
- [ ] Code complete and peer reviewed
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Deployed to dev environment
- [ ] QA validated (if applicable)
- [ ] No outstanding defects
- [ ] Acceptance criteria met

---

## Plugin Development Workflow

### Independent Plugin Development

**Process:**
1. Plugin team maintains separate backlog
2. Independent sprint planning
3. Own release cadence
4. Integration points documented as contracts

**When Main Product API Changes:**
1. Create "API Contract Change" work item in Platform backlog
2. Link to affected plugin work items
3. Schedule coordination meeting
4. Plan migration work in plugin backlogs

### Coordinated Plugin Development

**Process:**
1. Shared backlog refinement
2. Synchronized sprints
3. Coordinated releases
4. Integration testing in sprint

**Example:**
```
Sprint N:
- ProductCatalog: Implement new API endpoint
- ProductInventory: Consume new API endpoint
- Platform: Update integration tests
- Joint: Integration testing day (Thursday)
```

---

## Reporting and Metrics

### Key Metrics to Track

**Velocity Metrics:**
- Sprint velocity per team
- Rolling velocity (last 3 sprints)
- Velocity trends

**Quality Metrics:**
- Bug count by component
- Bug resolution time
- Bug reopen rate
- Defect density

**Delivery Metrics:**
- Lead time (idea to production)
- Cycle time (start to done)
- Deployment frequency
- Change failure rate

**Backlog Health:**
- Backlog size (story points)
- Backlog age (work items > 90 days)
- Ready items count
- Dependency count

### Reports Setup

**Create Custom Reports:**
1. Navigate to **Analytics** → **Analytics views**
2. Create new view
3. Configure filters and metrics
4. Add to dashboard

**Example Reports:**
- Sprint Burndown by Component
- Cumulative Flow by Area
- Velocity Comparison (Main vs Plugins)
- Dependency Impact Analysis
- Cross-Component Work Distribution

---

## Templates and Automation

### Work Item Templates

**Create Templates:**
1. Navigate to **Boards** → **Work Items**
2. Create template work item
3. Three dots → **Create template**
4. Save and reuse

**Template Library:**
- API Feature Template
- Bug Report Template
- Technical Debt Story Template
- Integration Story Template
- Security Work Item Template

### Automation Rules

**Common Automations:**

**Auto-assign based on area:**
```
IF Area Path = ProductCatalog\Core-API
THEN Assign to = @ProductCatalogTeam
```

**Auto-tag releases:**
```
IF Iteration = Sprint 10
THEN Add tag = v1.3.0
```

**Dependency alerts:**
```
IF Work item has Predecessor
AND Predecessor.State = Closed
THEN Send notification to Assigned To
```

---

## Migration Guide

### Moving from Current Setup

**Step 1: Audit Current Backlog**
```bash
# Export all work items
az boards work-item query --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems" --output table
```

**Step 2: Create Area Structure**
- Set up areas as documented
- Assign teams to areas

**Step 3: Bulk Update Work Items**
- Filter by component
- Bulk edit Area Path
- Add appropriate tags

**Step 4: Train Teams**
- Document new structure
- Conduct training sessions
- Update team processes

**Step 5: Monitor and Adjust**
- Review after 2 sprints
- Gather feedback
- Refine structure

---

## Appendix

### Sample Queries (SQL)

Save these as shared queries:

```sql
-- All ProductCatalog work for current quarter
SELECT [System.Id], [System.Title], [System.State], [System.IterationPath]
FROM WorkItems
WHERE [System.WorkItemType] IN ('Epic', 'Feature', 'User Story')
AND [System.AreaPath] UNDER 'Product-Management-Platform\ProductCatalog'
AND [System.IterationPath] UNDER 'Product-Management-Platform\2025\Q1'
ORDER BY [Microsoft.VSTS.Common.Priority] ASC

-- Cross-component integration work
SELECT [System.Id], [System.Title], [System.Tags], [System.State]
FROM WorkItems
WHERE [System.Tags] CONTAINS 'cross-component'
OR [System.Tags] CONTAINS 'integration'
AND [System.State] NOT IN ('Closed', 'Removed')
ORDER BY [Microsoft.VSTS.Common.Priority] ASC

-- Dependency tracking
SELECT [System.Id], [System.Title], [System.State], [System.AreaPath]
FROM WorkItemLinks
WHERE [Source].[System.WorkItemType] = 'Feature'
AND [System.Links.LinkType] = 'System.LinkTypes.Dependency-Forward'
AND [Target].[System.State] <> 'Closed'
MODE (Recursive)
```

### Useful Azure DevOps CLI Commands

```bash
# List all areas
az boards area project list --project "Product-Management-Platform"

# Create work item
az boards work-item create --type "User Story" --title "New story" --area "ProductCatalog"

# Update work item
az boards work-item update --id 123 --state "Active"

# Query work items
az boards work-item query --wiql "SELECT [System.Id] FROM WorkItems WHERE [System.WorkItemType] = 'Bug'"

# Create area path
az boards area project create --name "ProductCatalog\New-API" --project "Product-Management-Platform"
```

---

## Support and Resources

- **Azure Boards Documentation**: https://docs.microsoft.com/en-us/azure/devops/boards/
- **Team Contact**: backlog-admin@yourcompany.com
- **Training Resources**: [Internal Wiki Link]

---

*Last Updated: December 2025*
